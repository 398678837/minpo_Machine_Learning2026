# ============================================================
# 03_cross_validation_demo.py
# 교차 검증 (Cross-Validation) 전략 비교 데모
#
# 다양한 교차 검증 전략의 원리, 구현, 성능 추정 분산을
# 비교하여, 각 전략의 장단점을 이해한다.
#
# 전략: Hold-Out, K-Fold, Stratified K-Fold, Leave-One-Out (LOO)
# ============================================================

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec

from sklearn.datasets import load_iris, make_classification
from sklearn.model_selection import (
    train_test_split, KFold, StratifiedKFold,
    LeaveOneOut, cross_val_score, RepeatedKFold,
    RepeatedStratifiedKFold
)
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

# --- 한글 폰트 설정 ---
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# --- 시드 고정 ---
np.random.seed(42)


# ============================================================
# 1. 교차 검증 전략 설명
# ============================================================
CV_STRATEGIES = {
    "Hold-Out": {
        "설명": "데이터를 한 번만 학습/테스트로 분할",
        "장점": "계산 비용이 가장 낮음",
        "단점": "분할에 따라 결과가 크게 달라짐 (높은 분산)",
        "사용_시기": "데이터가 매우 많을 때, 빠른 프로토타이핑",
    },
    "K-Fold": {
        "설명": "데이터를 K개의 폴드로 나누어 K번 평가",
        "장점": "모든 데이터를 학습과 평가에 사용, 적당한 분산",
        "단점": "클래스 불균형 시 폴드별 클래스 비율이 다를 수 있음",
        "사용_시기": "일반적인 모델 평가",
    },
    "Stratified K-Fold": {
        "설명": "각 폴드에서 클래스 비율을 원본과 동일하게 유지",
        "장점": "클래스 불균형 데이터에서 안정적",
        "단점": "회귀 문제에는 직접 적용 불가",
        "사용_시기": "분류 문제, 특히 클래스 불균형 시 (기본 추천)",
    },
    "Leave-One-Out (LOO)": {
        "설명": "한 번에 하나의 샘플만 테스트로 사용",
        "장점": "편향이 가장 낮음 (거의 전체 데이터로 학습)",
        "단점": "계산 비용이 매우 높음, 분산이 높을 수 있음",
        "사용_시기": "데이터가 매우 적을 때",
    },
}


# ============================================================
# 2. 시각화 1: 교차 검증 분할 패턴
# ============================================================
def plot_cv_splits():
    """
    4가지 교차 검증 전략의 데이터 분할 패턴을 시각화한다.
    파란색 = 학습 데이터, 빨간색 = 테스트 데이터
    """
    n_samples = 20  # 시각화를 위해 작은 수
    n_splits_kfold = 5
    X = np.arange(n_samples).reshape(-1, 1)
    # 불균형 클래스: 0이 14개, 1이 6개
    y = np.array([0]*14 + [1]*6)

    fig, axes = plt.subplots(4, 1, figsize=(14, 12))

    strategies = [
        ("Hold-Out (80:20)", None),
        (f"K-Fold (K={n_splits_kfold})", KFold(n_splits=n_splits_kfold, shuffle=False)),
        (f"Stratified K-Fold (K={n_splits_kfold})",
         StratifiedKFold(n_splits=n_splits_kfold, shuffle=False)),
        (f"Leave-One-Out (LOO)", None),  # LOO는 별도 처리
    ]

    for ax_idx, (name, cv) in enumerate(strategies):
        ax = axes[ax_idx]

        if name.startswith("Hold-Out"):
            # Hold-Out: 1회 분할만 시각화
            n_splits = 3  # 3번의 서로 다른 random split
            for split_idx in range(n_splits):
                train_idx, test_idx = train_test_split(
                    range(n_samples), test_size=0.2,
                    random_state=split_idx
                )
                for j in range(n_samples):
                    color = '#4285F4' if j in train_idx else '#EA4335'
                    ax.barh(split_idx, 1, left=j, height=0.7,
                            color=color, edgecolor='white', linewidth=0.5)
                    # 클래스 표시
                    ax.text(j + 0.5, split_idx, str(y[j]),
                            ha='center', va='center', fontsize=6,
                            color='white', fontweight='bold')

            ax.set_yticks(range(n_splits))
            ax.set_yticklabels([f'분할 {i+1}' for i in range(n_splits)])

        elif name.startswith("Leave-One-Out"):
            # LOO: 처음 10개만 표시 (전체는 n_samples개)
            n_show = min(10, n_samples)
            for split_idx in range(n_show):
                for j in range(n_samples):
                    color = '#EA4335' if j == split_idx else '#4285F4'
                    ax.barh(split_idx, 1, left=j, height=0.7,
                            color=color, edgecolor='white', linewidth=0.5)

            ax.set_yticks(range(n_show))
            ax.set_yticklabels([f'반복 {i+1}' for i in range(n_show)])
            ax.text(n_samples + 0.5, n_show / 2,
                    f'... 총 {n_samples}회\n(각각 1개만 테스트)',
                    fontsize=9, va='center')

        else:
            # K-Fold 또는 Stratified K-Fold
            for split_idx, (train_idx, test_idx) in enumerate(cv.split(X, y)):
                for j in range(n_samples):
                    color = '#4285F4' if j in train_idx else '#EA4335'
                    ax.barh(split_idx, 1, left=j, height=0.7,
                            color=color, edgecolor='white', linewidth=0.5)
                    # 클래스 표시
                    ax.text(j + 0.5, split_idx, str(y[j]),
                            ha='center', va='center', fontsize=6,
                            color='white', fontweight='bold')

                # 테스트셋의 클래스 비율 표시
                test_ratio = y[test_idx].mean()
                ax.text(n_samples + 0.5, split_idx,
                        f'테스트 클래스1: {test_ratio:.0%}',
                        fontsize=8, va='center')

            ax.set_yticks(range(n_splits_kfold))
            ax.set_yticklabels([f'폴드 {i+1}' for i in range(n_splits_kfold)])

        ax.set_xlim(-0.5, n_samples + 6)
        ax.set_xlabel('샘플 인덱스')
        ax.set_title(name, fontsize=12, fontweight='bold', loc='left')
        ax.grid(False)

    # 범례
    train_patch = mpatches.Patch(color='#4285F4', label='학습 데이터 (Train)')
    test_patch = mpatches.Patch(color='#EA4335', label='테스트 데이터 (Test)')
    fig.legend(handles=[train_patch, test_patch], loc='upper right',
               fontsize=11, bbox_to_anchor=(0.98, 0.99))

    plt.suptitle('교차 검증 전략별 데이터 분할 패턴\n'
                 '(숫자 = 클래스 레이블, 클래스 0: 14개, 클래스 1: 6개)',
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig('03_cv_splits.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("[저장 완료] 03_cv_splits.png")


# ============================================================
# 3. 시각화 2: 성능 추정의 분산 비교
# ============================================================
def plot_variance_comparison():
    """
    각 교차 검증 전략을 여러 번 반복하여,
    성능 추정치의 분산(안정성)을 비교한다.
    """
    # 데이터 생성 (중간 크기, 약간의 노이즈)
    X, y = make_classification(
        n_samples=150, n_features=10, n_informative=5,
        n_redundant=2, n_classes=2, class_sep=1.0,
        random_state=42
    )

    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))

    n_repeats = 50  # 실험 반복 횟수
    results = {}

    # --- Hold-Out (여러 번 반복) ---
    print("  Hold-Out 평가 중...")
    holdout_scores = []
    for i in range(n_repeats):
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=i
        )
        model.fit(X_train, y_train)
        score = model.score(X_test, y_test)
        holdout_scores.append(score)
    results["Hold-Out\n(80:20)"] = holdout_scores

    # --- K-Fold (K=5, 여러 번 반복) ---
    print("  K-Fold 평가 중...")
    kfold_scores = []
    for i in range(n_repeats):
        cv = KFold(n_splits=5, shuffle=True, random_state=i)
        scores = cross_val_score(model, X, y, cv=cv)
        kfold_scores.append(scores.mean())
    results["K-Fold\n(K=5)"] = kfold_scores

    # --- Stratified K-Fold (K=5, 여러 번 반복) ---
    print("  Stratified K-Fold 평가 중...")
    skfold_scores = []
    for i in range(n_repeats):
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=i)
        scores = cross_val_score(model, X, y, cv=cv)
        skfold_scores.append(scores.mean())
    results["Stratified\nK-Fold\n(K=5)"] = skfold_scores

    # --- K-Fold (K=10) ---
    print("  K-Fold (K=10) 평가 중...")
    kfold10_scores = []
    for i in range(n_repeats):
        cv = KFold(n_splits=10, shuffle=True, random_state=i)
        scores = cross_val_score(model, X, y, cv=cv)
        kfold10_scores.append(scores.mean())
    results["K-Fold\n(K=10)"] = kfold10_scores

    # --- Leave-One-Out (1회만, 결정적이므로) ---
    print("  Leave-One-Out 평가 중...")
    loo = LeaveOneOut()
    loo_scores = cross_val_score(model, X, y, cv=loo)
    loo_mean = loo_scores.mean()
    # LOO는 결정적이므로 동일 값을 반복
    results["LOO"] = [loo_mean] * n_repeats

    # --- 시각화 ---
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # 좌측: 박스 플롯
    ax1 = axes[0]
    labels = list(results.keys())
    data = [results[k] for k in labels]

    bp = ax1.boxplot(data, labels=labels, patch_artist=True,
                     widths=0.6, showmeans=True,
                     meanprops=dict(marker='D', markerfacecolor='red',
                                    markersize=6))

    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax1.set_ylabel('정확도 (Accuracy)', fontsize=12)
    ax1.set_title('교차 검증 전략별 성능 추정 분포\n(50회 반복 실험)',
                  fontsize=12, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)
    ax1.axhline(y=loo_mean, color='gray', linestyle='--', alpha=0.5,
                label=f'LOO 정확도: {loo_mean:.3f}')
    ax1.legend(fontsize=9)

    # 우측: 통계 요약
    ax2 = axes[1]
    ax2.axis('off')

    # 표 데이터 작성
    table_data = []
    headers = ['전략', '평균', '표준편차', '최소', '최대', '범위']
    table_data.append(headers)

    for name, scores in results.items():
        clean_name = name.replace('\n', ' ')
        mean = np.mean(scores)
        std = np.std(scores)
        min_val = np.min(scores)
        max_val = np.max(scores)
        range_val = max_val - min_val
        table_data.append([
            clean_name,
            f'{mean:.4f}',
            f'{std:.4f}',
            f'{min_val:.4f}',
            f'{max_val:.4f}',
            f'{range_val:.4f}'
        ])

    table = ax2.table(
        cellText=table_data[1:],
        colLabels=table_data[0],
        loc='center',
        cellLoc='center',
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.8)

    # 헤더 스타일
    for j in range(len(headers)):
        table[0, j].set_facecolor('#4285F4')
        table[0, j].set_text_props(color='white', fontweight='bold')

    # 최소 분산 행 강조
    stds = [np.std(results[k]) for k in labels]
    # LOO는 분산 0이므로 제외하고 비교
    valid_stds = [(i, s) for i, s in enumerate(stds) if s > 0]
    if valid_stds:
        best_idx = min(valid_stds, key=lambda x: x[1])[0]
        for j in range(len(headers)):
            table[best_idx + 1, j].set_facecolor('#E8F5E9')

    ax2.set_title('성능 추정 통계 요약\n(초록 = 가장 낮은 분산)',
                  fontsize=12, fontweight='bold', pad=20)

    plt.suptitle('교차 검증 전략별 성능 추정 안정성 비교',
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig('03_variance_comparison.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("[저장 완료] 03_variance_comparison.png")

    return results


# ============================================================
# 4. 시각화 3: K값에 따른 편향-분산 트레이드오프
# ============================================================
def plot_k_tradeoff():
    """
    K-Fold에서 K값의 변화에 따른 성능 추정의 편향과 분산을 분석한다.
    K가 클수록 편향 감소, 분산 증가 (편향-분산 트레이드오프)
    """
    X, y = make_classification(
        n_samples=100, n_features=10, n_informative=5,
        n_redundant=2, n_classes=2, class_sep=1.0,
        random_state=42
    )

    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))

    k_values = [2, 3, 5, 7, 10, 15, 20, 50, 100]
    means = []
    stds = []
    n_repeats = 30

    for k in k_values:
        if k >= len(X):
            # LOO와 동일
            cv = LeaveOneOut()
            scores = cross_val_score(model, X, y, cv=cv)
            means.append(scores.mean())
            stds.append(0.0)  # 결정적
        else:
            repeat_means = []
            for i in range(n_repeats):
                cv = KFold(n_splits=k, shuffle=True, random_state=i)
                scores = cross_val_score(model, X, y, cv=cv)
                repeat_means.append(scores.mean())
            means.append(np.mean(repeat_means))
            stds.append(np.std(repeat_means))

    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    # 좌측: 평균 정확도 (편향 관련)
    ax1 = axes[0]
    ax1.errorbar(k_values, means, yerr=stds, fmt='o-',
                 color='#4285F4', linewidth=2, markersize=8,
                 capsize=5, capthick=2,
                 label='평균 정확도 +/- 표준편차')
    ax1.set_xlabel('K (폴드 수)', fontsize=12)
    ax1.set_ylabel('평균 정확도', fontsize=12)
    ax1.set_title('K값에 따른 평균 성능 추정\n(K 증가 → 편향 감소)',
                  fontsize=12, fontweight='bold')
    ax1.set_xscale('log')
    ax1.set_xticks(k_values)
    ax1.set_xticklabels([str(k) for k in k_values])
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=10)

    # 우측: 분산 (불안정성)
    ax2 = axes[1]
    ax2.plot(k_values, stds, 'o-', color='#EA4335', linewidth=2,
             markersize=8, label='성능 추정의 표준편차')
    ax2.fill_between(k_values, 0, stds, alpha=0.2, color='#EA4335')
    ax2.set_xlabel('K (폴드 수)', fontsize=12)
    ax2.set_ylabel('표준편차', fontsize=12)
    ax2.set_title('K값에 따른 성능 추정 분산\n(K 증가 → 분산 증가 경향)',
                  fontsize=12, fontweight='bold')
    ax2.set_xscale('log')
    ax2.set_xticks(k_values)
    ax2.set_xticklabels([str(k) for k in k_values])
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=10)

    # 주석
    ax2.annotate('K=5~10이\n가장 일반적',
                 xy=(7, stds[k_values.index(7)]),
                 xytext=(15, max(stds) * 0.7),
                 arrowprops=dict(arrowstyle='->', color='black'),
                 fontsize=11, fontweight='bold',
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow'))

    plt.suptitle('K-Fold의 K값에 따른 편향-분산 트레이드오프',
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig('03_k_tradeoff.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("[저장 완료] 03_k_tradeoff.png")


# ============================================================
# 5. 시각화 4: Iris 데이터셋 실전 예제
# ============================================================
def plot_iris_cv_comparison():
    """
    Iris 데이터셋에서 다양한 CV 전략의 실제 성능을 비교한다.
    """
    iris = load_iris()
    X, y = iris.data, iris.target

    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))

    print("\n[Iris 데이터셋 교차 검증 결과]")
    print(f"데이터 크기: {X.shape[0]}개, 특성 수: {X.shape[1]}개")
    print(f"클래스: {iris.target_names}")
    print(f"클래스 분포: {np.bincount(y)}")

    all_scores = {}

    # Hold-Out (10회 반복)
    holdout_scores = []
    for i in range(10):
        X_tr, X_te, y_tr, y_te = train_test_split(
            X, y, test_size=0.3, random_state=i, stratify=y
        )
        model.fit(X_tr, y_tr)
        holdout_scores.append(model.score(X_te, y_te))
    all_scores['Hold-Out'] = holdout_scores
    print(f"\nHold-Out (70:30, 10회): {np.mean(holdout_scores):.4f} "
          f"+/- {np.std(holdout_scores):.4f}")

    # 5-Fold
    cv5 = KFold(n_splits=5, shuffle=True, random_state=42)
    scores_5fold = cross_val_score(model, X, y, cv=cv5)
    all_scores['5-Fold'] = scores_5fold
    print(f"5-Fold CV: {scores_5fold.mean():.4f} +/- {scores_5fold.std():.4f}")
    print(f"  각 폴드: {scores_5fold}")

    # Stratified 5-Fold
    cv5s = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores_5sfold = cross_val_score(model, X, y, cv=cv5s)
    all_scores['Stratified\n5-Fold'] = scores_5sfold
    print(f"Stratified 5-Fold CV: {scores_5sfold.mean():.4f} "
          f"+/- {scores_5sfold.std():.4f}")
    print(f"  각 폴드: {scores_5sfold}")

    # 10-Fold
    cv10 = KFold(n_splits=10, shuffle=True, random_state=42)
    scores_10fold = cross_val_score(model, X, y, cv=cv10)
    all_scores['10-Fold'] = scores_10fold
    print(f"10-Fold CV: {scores_10fold.mean():.4f} "
          f"+/- {scores_10fold.std():.4f}")

    # LOO
    loo = LeaveOneOut()
    scores_loo = cross_val_score(model, X, y, cv=loo)
    all_scores['LOO'] = scores_loo
    print(f"LOO CV: {scores_loo.mean():.4f} (총 {len(scores_loo)}회)")

    # --- 시각화 ---
    fig, ax = plt.subplots(figsize=(12, 6))

    positions = range(len(all_scores))
    labels = list(all_scores.keys())
    data = [all_scores[k] for k in labels]

    bp = ax.boxplot(data, positions=positions, labels=labels,
                    patch_artist=True, widths=0.5, showmeans=True,
                    meanprops=dict(marker='D', markerfacecolor='red',
                                   markersize=7))

    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
    for i, (patch, color) in enumerate(zip(bp['boxes'], colors)):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    # 평균값 레이블
    for i, d in enumerate(data):
        mean_val = np.mean(d)
        ax.text(i, mean_val + 0.005, f'{mean_val:.3f}',
                ha='center', fontsize=10, fontweight='bold', color='red')

    ax.set_ylabel('정확도 (Accuracy)', fontsize=12)
    ax.set_title('Iris 데이터셋: 교차 검증 전략별 성능 추정 비교\n'
                 '(빨간 다이아몬드 = 평균, 빨간 숫자 = 평균값)',
                 fontsize=13, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim(0.85, 1.02)

    plt.tight_layout()
    plt.savefig('03_iris_cv_comparison.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("[저장 완료] 03_iris_cv_comparison.png")


# ============================================================
# 메인 실행
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("교차 검증 (Cross-Validation) 전략 비교 데모")
    print("=" * 60)

    # 전략 설명 출력
    print("\n[교차 검증 전략 설명]")
    for name, info in CV_STRATEGIES.items():
        print(f"\n  {name}:")
        print(f"    설명: {info['설명']}")
        print(f"    장점: {info['장점']}")
        print(f"    단점: {info['단점']}")
        print(f"    권장: {info['사용_시기']}")

    # --- 시각화 1: 분할 패턴 ---
    print(f"\n[1/4] 교차 검증 분할 패턴 시각화...")
    plot_cv_splits()

    # --- 시각화 2: 분산 비교 ---
    print(f"\n[2/4] 성능 추정 분산 비교...")
    results = plot_variance_comparison()

    # --- 시각화 3: K값 트레이드오프 ---
    print(f"\n[3/4] K값에 따른 편향-분산 트레이드오프...")
    plot_k_tradeoff()

    # --- 시각화 4: Iris 실전 예제 ---
    print(f"\n[4/4] Iris 데이터셋 실전 비교...")
    plot_iris_cv_comparison()

    # --- 최종 요약 ---
    print("\n" + "=" * 60)
    print("최종 요약: 교차 검증 전략 선택 가이드")
    print("=" * 60)
    print("""
1. 일반적인 권장사항:
   - 기본: Stratified K-Fold (K=5 또는 K=10)
   - 분류 문제에서 가장 안정적인 성능 추정
   - sklearn의 cross_val_score 기본값도 Stratified 5-Fold

2. 데이터 크기별 권장:
   - 대용량 (>10,000): Hold-Out 또는 3-Fold
   - 중간 (100~10,000): 5-Fold 또는 10-Fold
   - 소용량 (<100): LOO 또는 Repeated K-Fold

3. 핵심 원리 (편향-분산 트레이드오프):
   - K가 작을 때: 높은 편향 (학습 데이터 부족), 낮은 분산
   - K가 클 때: 낮은 편향 (거의 전체 데이터 사용), 높은 분산
   - LOO (K=N): 가장 낮은 편향, 가장 높은 분산
   - 실무적 최적점: K=5~10

4. 주의사항:
   - 시계열 데이터: 시간 순서를 존중하는 Time Series Split 사용
   - 그룹 데이터: Group K-Fold 사용 (데이터 누수 방지)
   - 불균형 데이터: 반드시 Stratified 사용

[완료] 생성된 파일:
  - 03_cv_splits.png
  - 03_variance_comparison.png
  - 03_k_tradeoff.png
  - 03_iris_cv_comparison.png
""")
