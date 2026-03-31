# -*- coding: utf-8 -*-
"""
02_discriminative_vs_generative.py
판별 모델(로지스틱 회귀) vs 생성 모델(나이브 베이즈) 비교

Ng & Jordan (2002) "On Discriminative vs. Generative classifiers"의 핵심 결과 재현:
1. 판별 모델(로지스틱 회귀)은 점근적으로 더 낮은 오차를 달성
2. 생성 모델(나이브 베이즈)은 적은 데이터에서 더 빠르게 수렴
3. 전환점(crossover point)이 존재하여 소표본/대표본에서 최적 모델이 다름

구현 내용:
- 표본 크기별 학습 곡선(learning curve) 비교
- 다양한 데이터 설정에서의 비교
- 전환점 식별 시각화
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.metrics import accuracy_score
from sklearn.datasets import make_classification
from sklearn.preprocessing import StandardScaler


# ============================================================
# 1. 핵심 실험 함수
# ============================================================

def compare_models_by_sample_size(X, y, train_fractions, n_repeats=50, test_size=0.3):
    """
    다양한 학습 데이터 크기에서 로지스틱 회귀와 나이브 베이즈 비교

    Ng & Jordan(2002)의 핵심 실험:
    - 학습 데이터 크기를 점진적으로 증가시키며
    - 두 모델의 테스트 정확도를 반복 측정
    - 평균과 표준편차를 산출

    매개변수:
        X: 전체 특성 행렬
        y: 전체 레이블 벡터
        train_fractions: 학습 데이터 비율 리스트 (예: [0.01, 0.05, 0.1, ...])
        n_repeats: 각 비율에서 반복 실험 횟수
        test_size: 테스트 세트 비율

    반환:
        results: 딕셔너리 (각 모델의 정확도 평균/표준편차)
    """
    n_total = len(y)

    # 결과 저장용
    lr_means = []  # 로지스틱 회귀 평균 정확도
    lr_stds = []   # 로지스틱 회귀 표준편차
    nb_means = []  # 나이브 베이즈 평균 정확도
    nb_stds = []   # 나이브 베이즈 표준편차
    actual_sizes = []  # 실제 학습 데이터 크기

    for frac in train_fractions:
        # 학습에 사용할 표본 수 계산
        n_train = max(int(n_total * (1 - test_size) * frac), 4)  # 최소 4개

        lr_scores = []
        nb_scores = []

        for seed in range(n_repeats):
            # 전체 데이터를 학습/테스트로 분리
            splitter = StratifiedShuffleSplit(n_splits=1, test_size=test_size,
                                              random_state=seed)
            train_idx, test_idx = next(splitter.split(X, y))

            X_test = X[test_idx]
            y_test = y[test_idx]

            # 학습 데이터에서 n_train개만 샘플링
            rng = np.random.RandomState(seed + 1000)
            if n_train < len(train_idx):
                selected = rng.choice(len(train_idx), n_train, replace=False)
                train_subset = train_idx[selected]
            else:
                train_subset = train_idx

            X_train = X[train_subset]
            y_train = y[train_subset]

            # 클래스가 1개만 있으면 건너뛰기
            if len(np.unique(y_train)) < 2:
                continue

            # 표준화
            scaler = StandardScaler()
            X_train_s = scaler.fit_transform(X_train)
            X_test_s = scaler.transform(X_test)

            # --- 로지스틱 회귀 (판별 모델) ---
            try:
                lr_model = LogisticRegression(max_iter=2000, random_state=42,
                                              solver='lbfgs')
                lr_model.fit(X_train_s, y_train)
                lr_pred = lr_model.predict(X_test_s)
                lr_scores.append(accuracy_score(y_test, lr_pred))
            except Exception:
                pass

            # --- 나이브 베이즈 (생성 모델) ---
            try:
                nb_model = GaussianNB()
                nb_model.fit(X_train_s, y_train)
                nb_pred = nb_model.predict(X_test_s)
                nb_scores.append(accuracy_score(y_test, nb_pred))
            except Exception:
                pass

        if len(lr_scores) > 0 and len(nb_scores) > 0:
            lr_means.append(np.mean(lr_scores))
            lr_stds.append(np.std(lr_scores))
            nb_means.append(np.mean(nb_scores))
            nb_stds.append(np.std(nb_scores))
            actual_sizes.append(n_train)

    return {
        'train_sizes': actual_sizes,
        'lr_means': np.array(lr_means),
        'lr_stds': np.array(lr_stds),
        'nb_means': np.array(nb_means),
        'nb_stds': np.array(nb_stds)
    }


def plot_learning_curves(results, title, ax=None, show_crossover=True):
    """
    학습 곡선 시각화

    Ng & Jordan(2002)의 Figure 1을 재현:
    - x축: 학습 데이터 크기
    - y축: 테스트 정확도
    - 로지스틱 회귀와 나이브 베이즈의 곡선 비교
    - 전환점(crossover point) 표시
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))

    sizes = results['train_sizes']

    # 로지스틱 회귀 (판별 모델) - 파란색
    ax.plot(sizes, results['lr_means'], 'b-o', linewidth=2, markersize=5,
            label='로지스틱 회귀 (판별)', zorder=3)
    ax.fill_between(sizes,
                     results['lr_means'] - results['lr_stds'],
                     results['lr_means'] + results['lr_stds'],
                     color='blue', alpha=0.15)

    # 나이브 베이즈 (생성 모델) - 빨간색
    ax.plot(sizes, results['nb_means'], 'r-s', linewidth=2, markersize=5,
            label='나이브 베이즈 (생성)', zorder=3)
    ax.fill_between(sizes,
                     results['nb_means'] - results['nb_stds'],
                     results['nb_means'] + results['nb_stds'],
                     color='red', alpha=0.15)

    # 전환점 식별 및 표시
    if show_crossover:
        diff = results['lr_means'] - results['nb_means']
        # 나이브 베이즈가 우세 -> 로지스틱 회귀가 우세로 전환되는 지점
        crossover_found = False
        for i in range(1, len(diff)):
            if diff[i-1] <= 0 and diff[i] > 0:
                # 선형 보간으로 전환점 추정
                crossover_size = sizes[i-1] + (sizes[i] - sizes[i-1]) * (-diff[i-1]) / (diff[i] - diff[i-1])
                crossover_acc = results['nb_means'][i-1] + (results['nb_means'][i] - results['nb_means'][i-1]) * (-diff[i-1]) / (diff[i] - diff[i-1])
                ax.axvline(x=crossover_size, color='green', linestyle=':', linewidth=2, alpha=0.7)
                ax.annotate(f'전환점\nn={int(crossover_size)}',
                           xy=(crossover_size, crossover_acc),
                           xytext=(crossover_size * 1.3, crossover_acc - 0.03),
                           fontsize=10, color='green',
                           arrowprops=dict(arrowstyle='->', color='green'))
                crossover_found = True
                break

        if not crossover_found:
            # 전환점이 없는 경우 (한 모델이 항상 우세)
            if np.mean(diff) > 0:
                note = "(로지스틱 회귀가 전 구간에서 우세)"
            else:
                note = "(나이브 베이즈가 전 구간에서 우세)"
            ax.text(0.5, 0.02, note, transform=ax.transAxes,
                    fontsize=9, ha='center', style='italic', color='gray')

    ax.set_xlabel('학습 데이터 크기', fontsize=12)
    ax.set_ylabel('테스트 정확도', fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.legend(fontsize=11, loc='lower right')
    ax.grid(True, alpha=0.3)

    return ax


# ============================================================
# 2. 실험 1: 나이브 베이즈 가정이 성립하는 데이터
# ============================================================

print("=" * 70)
print("실험 1: 나이브 베이즈 가정이 (대략) 성립하는 데이터")
print("  - 특성 간 독립성이 높음")
print("  - Ng & Jordan: 생성 모델이 소표본에서 우세해야 함")
print("=" * 70)

# 특성 간 독립적인 데이터 생성
# n_informative와 n_features를 같게 하여 독립적 특성 최대화
np.random.seed(42)
X1, y1 = make_classification(
    n_samples=2000,
    n_features=20,
    n_informative=20,      # 모든 특성이 유용함
    n_redundant=0,          # 중복 특성 없음 (독립성 높임)
    n_clusters_per_class=1, # 단순한 가우시안 분포
    class_sep=1.0,          # 적당한 클래스 분리
    random_state=42
)

# 다양한 학습 데이터 비율
train_fractions = [0.01, 0.02, 0.05, 0.08, 0.1, 0.15, 0.2, 0.3, 0.5, 0.7, 1.0]

print("학습 곡선 계산 중 (반복 50회)...")
results1 = compare_models_by_sample_size(X1, y1, train_fractions, n_repeats=50)

print("완료!")
print(f"\n표본 크기별 정확도 비교:")
print(f"{'크기':>6s} | {'로지스틱회귀':>12s} | {'나이브베이즈':>12s} | {'우세 모델':>12s}")
print("-" * 55)
for i, size in enumerate(results1['train_sizes']):
    lr_acc = results1['lr_means'][i]
    nb_acc = results1['nb_means'][i]
    winner = "나이브베이즈" if nb_acc > lr_acc else "로지스틱회귀" if lr_acc > nb_acc else "동일"
    print(f"{size:>6d} | {lr_acc:>12.4f} | {nb_acc:>12.4f} | {winner:>12s}")


# ============================================================
# 3. 실험 2: 나이브 베이즈 가정이 위반되는 데이터
# ============================================================

print("\n" + "=" * 70)
print("실험 2: 나이브 베이즈 가정이 위반되는 데이터")
print("  - 특성 간 높은 상관관계 (중복 특성 존재)")
print("  - Ng & Jordan: 판별 모델이 점근적으로 더 우세해야 함")
print("=" * 70)

X2, y2 = make_classification(
    n_samples=2000,
    n_features=20,
    n_informative=10,       # 유용한 특성 10개
    n_redundant=10,          # 중복 특성 10개 (상관관계 높음)
    n_clusters_per_class=2,  # 복잡한 클래스 구조
    class_sep=0.8,
    flip_y=0.05,             # 5% 노이즈
    random_state=42
)

print("학습 곡선 계산 중 (반복 50회)...")
results2 = compare_models_by_sample_size(X2, y2, train_fractions, n_repeats=50)

print("완료!")
print(f"\n표본 크기별 정확도 비교:")
print(f"{'크기':>6s} | {'로지스틱회귀':>12s} | {'나이브베이즈':>12s} | {'우세 모델':>12s}")
print("-" * 55)
for i, size in enumerate(results2['train_sizes']):
    lr_acc = results2['lr_means'][i]
    nb_acc = results2['nb_means'][i]
    winner = "나이브베이즈" if nb_acc > lr_acc else "로지스틱회귀" if lr_acc > nb_acc else "동일"
    print(f"{size:>6d} | {lr_acc:>12.4f} | {nb_acc:>12.4f} | {winner:>12s}")


# ============================================================
# 4. 실험 3: 높은 차원의 데이터 (특성 수 >> 표본 수 상황)
# ============================================================

print("\n" + "=" * 70)
print("실험 3: 고차원 데이터 (특성 수가 많은 경우)")
print("  - 특성 50개: 소표본에서 로지스틱 회귀가 불안정할 수 있음")
print("  - Ng & Jordan: 생성 모델의 O(log n) 수렴이 더 유리해야 함")
print("=" * 70)

X3, y3 = make_classification(
    n_samples=2000,
    n_features=50,
    n_informative=30,
    n_redundant=10,
    n_clusters_per_class=1,
    class_sep=1.0,
    random_state=42
)

print("학습 곡선 계산 중 (반복 50회)...")
results3 = compare_models_by_sample_size(X3, y3, train_fractions, n_repeats=50)

print("완료!")
print(f"\n표본 크기별 정확도 비교:")
print(f"{'크기':>6s} | {'로지스틱회귀':>12s} | {'나이브베이즈':>12s} | {'우세 모델':>12s}")
print("-" * 55)
for i, size in enumerate(results3['train_sizes']):
    lr_acc = results3['lr_means'][i]
    nb_acc = results3['nb_means'][i]
    winner = "나이브베이즈" if nb_acc > lr_acc else "로지스틱회귀" if lr_acc > nb_acc else "동일"
    print(f"{size:>6d} | {lr_acc:>12.4f} | {nb_acc:>12.4f} | {winner:>12s}")


# ============================================================
# 5. 종합 시각화
# ============================================================

print("\n" + "=" * 70)
print("종합 시각화: 세 가지 실험의 학습 곡선")
print("=" * 70)

fig, axes = plt.subplots(1, 3, figsize=(20, 6))

plot_learning_curves(
    results1,
    "실험 1: 독립적 특성\n(나이브 베이즈 가정 성립)",
    ax=axes[0]
)

plot_learning_curves(
    results2,
    "실험 2: 상관된 특성\n(나이브 베이즈 가정 위반)",
    ax=axes[1]
)

plot_learning_curves(
    results3,
    "실험 3: 고차원 데이터\n(50개 특성)",
    ax=axes[2]
)

plt.suptitle(
    'Ng & Jordan (2002) 재현: 판별 모델 vs 생성 모델 학습 곡선 비교',
    fontsize=16, y=1.03
)
plt.tight_layout()
plt.savefig('discriminative_vs_generative_learning_curves.png',
            dpi=150, bbox_inches='tight')
plt.show()
print("[저장 완료] discriminative_vs_generative_learning_curves.png")


# ============================================================
# 6. 정확도 차이 시각화 (전환점 분석)
# ============================================================

print("\n" + "=" * 70)
print("전환점 분석: 정확도 차이 (로지스틱 회귀 - 나이브 베이즈)")
print("=" * 70)

fig, axes = plt.subplots(1, 3, figsize=(20, 5))

titles = [
    "실험 1: 독립적 특성",
    "실험 2: 상관된 특성",
    "실험 3: 고차원 데이터"
]

for ax, results, title in zip(axes, [results1, results2, results3], titles):
    diff = results['lr_means'] - results['nb_means']
    sizes = results['train_sizes']

    # 차이 막대 그래프
    colors = ['blue' if d > 0 else 'red' for d in diff]
    ax.bar(range(len(sizes)), diff, color=colors, alpha=0.7, edgecolor='black', linewidth=0.5)
    ax.axhline(y=0, color='black', linewidth=1)
    ax.set_xticks(range(len(sizes)))
    ax.set_xticklabels([str(s) for s in sizes], rotation=45, fontsize=9)
    ax.set_xlabel('학습 데이터 크기', fontsize=11)
    ax.set_ylabel('정확도 차이\n(LR - NB)', fontsize=11)
    ax.set_title(title, fontsize=12)
    ax.grid(True, alpha=0.3, axis='y')

    # 범례 추가
    ax.text(0.02, 0.98, '파랑: 로지스틱 회귀 우세', transform=ax.transAxes,
            fontsize=9, va='top', color='blue')
    ax.text(0.02, 0.90, '빨강: 나이브 베이즈 우세', transform=ax.transAxes,
            fontsize=9, va='top', color='red')

plt.suptitle('표본 크기별 정확도 차이 (양수 = 로지스틱 회귀 우세)', fontsize=14, y=1.02)
plt.tight_layout()
plt.savefig('accuracy_difference_analysis.png', dpi=150, bbox_inches='tight')
plt.show()
print("[저장 완료] accuracy_difference_analysis.png")


# ============================================================
# 7. 편향-분산 관점의 분석
# ============================================================

print("\n" + "=" * 70)
print("편향-분산 분석")
print("=" * 70)

# 실험 2 데이터로 편향-분산 분해 (근사)
print("\n실험 2 (상관된 특성) 데이터에 대한 분석:")
print()

# 특정 표본 크기에서의 예측 분포 분석
sample_sizes_to_analyze = [14, 56, 140, 700]

for n_train in sample_sizes_to_analyze:
    lr_scores_list = []
    nb_scores_list = []

    for seed in range(100):
        # 학습/테스트 분리
        splitter = StratifiedShuffleSplit(n_splits=1, test_size=0.3,
                                          random_state=seed)
        train_idx, test_idx = next(splitter.split(X2, y2))

        # n_train개만 샘플링
        rng = np.random.RandomState(seed + 2000)
        if n_train < len(train_idx):
            selected = rng.choice(len(train_idx), n_train, replace=False)
            train_subset = train_idx[selected]
        else:
            train_subset = train_idx

        X_tr = X2[train_subset]
        y_tr = y2[train_subset]
        X_te = X2[test_idx]
        y_te = y2[test_idx]

        if len(np.unique(y_tr)) < 2:
            continue

        scaler = StandardScaler()
        X_tr_s = scaler.fit_transform(X_tr)
        X_te_s = scaler.transform(X_te)

        try:
            lr = LogisticRegression(max_iter=2000, random_state=42)
            lr.fit(X_tr_s, y_tr)
            lr_scores_list.append(accuracy_score(y_te, lr.predict(X_te_s)))
        except Exception:
            pass

        nb = GaussianNB()
        nb.fit(X_tr_s, y_tr)
        nb_scores_list.append(accuracy_score(y_te, nb.predict(X_te_s)))

    lr_arr = np.array(lr_scores_list)
    nb_arr = np.array(nb_scores_list)

    print(f"n_train = {n_train:>4d}:")
    print(f"  로지스틱 회귀 - 평균: {lr_arr.mean():.4f}, 분산: {lr_arr.var():.6f}")
    print(f"  나이브 베이즈 - 평균: {nb_arr.mean():.4f}, 분산: {nb_arr.var():.6f}")
    print(f"  -> {'로지스틱 회귀' if lr_arr.mean() > nb_arr.mean() else '나이브 베이즈'} 우세")
    print(f"     (나이브 베이즈 분산이 {'더 낮음' if nb_arr.var() < lr_arr.var() else '더 높음'})")
    print()


# ============================================================
# 8. 최종 요약
# ============================================================

print("=" * 70)
print("최종 요약: Ng & Jordan (2002) 핵심 결과 재현")
print("=" * 70)
print("""
Ng & Jordan (2002)의 핵심 발견:

1. 판별-생성 쌍의 관계:
   - 나이브 베이즈(생성)와 로지스틱 회귀(판별)는 동일한 모델 패밀리를 공유
   - 차이점은 파라미터를 추정하는 방법(결합 우도 vs 조건부 우도)

2. 수렴 속도의 차이:
   - 생성 모델(나이브 베이즈): O(log n)으로 빠르게 점근적 성능에 도달
   - 판별 모델(로지스틱 회귀): O(n)으로 느리게 수렴하지만 점근적 오차가 더 낮음

3. 전환점(Crossover Point)의 존재:
   - 소표본: 나이브 베이즈가 우세 (빠른 수렴의 이점)
   - 대표본: 로지스틱 회귀가 우세 (더 낮은 점근적 오차)
   - 전환점은 데이터의 특성과 모델 가정의 정확도에 따라 달라짐

4. 실용적 함의:
   - 데이터가 적으면: 나이브 베이즈(생성 모델) 사용
   - 데이터가 충분하면: 로지스틱 회귀(판별 모델) 사용
   - 확신이 없으면: 학습 곡선을 그려서 전환점을 확인
""")
