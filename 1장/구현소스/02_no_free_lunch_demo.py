# ============================================================
# 02_no_free_lunch_demo.py
# No Free Lunch 정리 데모
#
# 참고 논문: Wolpert & Macready (1997) "No Free Lunch Theorems
#           for Optimization"
#
# 이 코드는 다양한 데이터셋에 여러 알고리즘을 적용하여,
# 어떤 단일 알고리즘도 모든 데이터셋에서 최상이 아님을 보여준다.
# 이것이 바로 No Free Lunch 정리의 핵심 메시지이다.
# ============================================================

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

from sklearn.datasets import make_moons, make_circles, make_classification
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

# --- 한글 폰트 설정 ---
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# --- 시드 고정 ---
np.random.seed(42)


# ============================================================
# 1. 다양한 데이터셋 생성
# ============================================================
def create_datasets():
    """
    4가지 서로 다른 구조를 가진 데이터셋을 생성한다.
    각 데이터셋은 서로 다른 알고리즘에 유리한 구조를 가진다.

    Returns
    -------
    datasets : list of tuples
        각 원소는 (X, y, 이름, 설명) 튜플
    """
    n_samples = 300

    # 데이터셋 1: 선형 분리 가능 (Linear) → 선형 모델에 유리
    X_linear, y_linear = make_classification(
        n_samples=n_samples, n_features=2, n_redundant=0,
        n_informative=2, n_clusters_per_class=1,
        class_sep=2.0, random_state=42
    )

    # 데이터셋 2: 원형 (Circles) → RBF 커널 SVM에 유리
    X_circles, y_circles = make_circles(
        n_samples=n_samples, noise=0.1, factor=0.5, random_state=42
    )

    # 데이터셋 3: XOR 패턴 → 결정 트리 / 비선형 모델에 유리
    X_xor = np.random.randn(n_samples, 2)
    y_xor = np.logical_xor(X_xor[:, 0] > 0, X_xor[:, 1] > 0).astype(int)

    # 데이터셋 4: 반달 (Moons) → k-NN / 비선형 모델에 유리
    X_moons, y_moons = make_moons(
        n_samples=n_samples, noise=0.2, random_state=42
    )

    datasets = [
        (X_linear, y_linear, "선형 분리 (Linear)",
         "선형 결정 경계로 분리 가능한 데이터"),
        (X_circles, y_circles, "원형 (Circles)",
         "동심원 구조의 비선형 데이터"),
        (X_xor, y_xor, "XOR 패턴",
         "XOR 논리 연산 구조의 데이터"),
        (X_moons, y_moons, "반달 (Moons)",
         "반달 형태의 비선형 데이터"),
    ]

    return datasets


# ============================================================
# 2. 알고리즘 정의
# ============================================================
def create_classifiers():
    """
    5가지 대표적인 분류 알고리즘을 정의한다.
    각 알고리즘은 서로 다른 귀납적 편향(inductive bias)을 가진다.

    Returns
    -------
    classifiers : list of tuples
        각 원소는 (모델 객체, 이름, 귀납적 편향 설명) 튜플
    """
    classifiers = [
        (
            LogisticRegression(random_state=42, max_iter=1000),
            "로지스틱 회귀\n(Linear)",
            "선형 결정 경계 가정"
        ),
        (
            KNeighborsClassifier(n_neighbors=5),
            "k-NN\n(k=5)",
            "국소적 유사성 가정"
        ),
        (
            SVC(kernel='rbf', gamma='auto', random_state=42),
            "SVM\n(RBF Kernel)",
            "마진 최대화 + 비선형 커널"
        ),
        (
            DecisionTreeClassifier(max_depth=10, random_state=42),
            "결정 트리\n(Decision Tree)",
            "축 정렬 분할 가정"
        ),
        (
            RandomForestClassifier(n_estimators=100, random_state=42),
            "랜덤 포레스트\n(Random Forest)",
            "앙상블 + 축 정렬 분할"
        ),
    ]

    return classifiers


# ============================================================
# 3. 교차 검증으로 성능 평가
# ============================================================
def evaluate_all(datasets, classifiers):
    """
    모든 데이터셋-알고리즘 조합에 대해 교차 검증 성능을 계산한다.

    Returns
    -------
    results : dict
        results[데이터셋이름][알고리즘이름] = (평균 정확도, 표준편차)
    scores_matrix : ndarray
        (n_datasets, n_classifiers) 크기의 정확도 행렬
    """
    results = {}
    n_datasets = len(datasets)
    n_classifiers = len(classifiers)
    scores_matrix = np.zeros((n_datasets, n_classifiers))

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    for i, (X, y, ds_name, _) in enumerate(datasets):
        # 데이터 스케일링
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        results[ds_name] = {}
        for j, (clf, clf_name, _) in enumerate(classifiers):
            scores = cross_val_score(clf, X_scaled, y, cv=cv, scoring='accuracy')
            mean_score = scores.mean()
            std_score = scores.std()
            results[ds_name][clf_name] = (mean_score, std_score)
            scores_matrix[i, j] = mean_score

    return results, scores_matrix


# ============================================================
# 4. 시각화 1: 데이터셋과 결정 경계
# ============================================================
def plot_decision_boundaries(datasets, classifiers):
    """
    각 데이터셋-알고리즘 조합의 결정 경계를 시각화한다.
    """
    n_datasets = len(datasets)
    n_classifiers = len(classifiers)

    fig, axes = plt.subplots(n_datasets, n_classifiers,
                             figsize=(n_classifiers * 3.5, n_datasets * 3.5))

    # 결정 경계 색상
    cm_bg = ListedColormap(['#FFAAAA', '#AAAAFF'])
    cm_pts = ListedColormap(['#FF0000', '#0000FF'])

    h = 0.02  # 메시 해상도

    for i, (X, y, ds_name, _) in enumerate(datasets):
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        x_min, x_max = X_scaled[:, 0].min() - 0.5, X_scaled[:, 0].max() + 0.5
        y_min, y_max = X_scaled[:, 1].min() - 0.5, X_scaled[:, 1].max() + 0.5
        xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                             np.arange(y_min, y_max, h))

        for j, (clf, clf_name, _) in enumerate(classifiers):
            ax = axes[i, j]
            clf_copy = type(clf)(**clf.get_params())
            clf_copy.fit(X_scaled, y)

            # 결정 경계 그리기
            Z = clf_copy.predict(np.c_[xx.ravel(), yy.ravel()])
            Z = Z.reshape(xx.shape)
            ax.contourf(xx, yy, Z, cmap=cm_bg, alpha=0.4)
            ax.scatter(X_scaled[:, 0], X_scaled[:, 1], c=y,
                      cmap=cm_pts, s=10, alpha=0.6, edgecolors='gray',
                      linewidths=0.3)

            # 학습 정확도 표시
            train_acc = clf_copy.score(X_scaled, y)
            ax.set_title(f'{train_acc:.1%}', fontsize=10)

            if j == 0:
                ax.set_ylabel(ds_name, fontsize=10, fontweight='bold')
            if i == 0:
                ax.set_title(f'{clf_name}\n{train_acc:.1%}', fontsize=9)

            ax.set_xticks([])
            ax.set_yticks([])

    plt.suptitle('No Free Lunch 정리: 데이터셋별 결정 경계 비교\n'
                 '(각 숫자는 학습 정확도)',
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig('02_decision_boundaries.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("[저장 완료] 02_decision_boundaries.png")


# ============================================================
# 5. 시각화 2: 성능 비교 히트맵
# ============================================================
def plot_performance_heatmap(datasets, classifiers, scores_matrix):
    """
    데이터셋 x 알고리즘의 성능 히트맵을 그린다.
    각 행(데이터셋)에서 최고 성능 알고리즘을 강조한다.
    """
    ds_names = [ds[2] for ds in datasets]
    clf_names = [clf[1].replace('\n', ' ') for clf in classifiers]

    fig, ax = plt.subplots(figsize=(12, 6))

    # 히트맵 그리기
    im = ax.imshow(scores_matrix, cmap='YlOrRd', aspect='auto',
                   vmin=0.5, vmax=1.0)

    # 축 레이블
    ax.set_xticks(range(len(clf_names)))
    ax.set_xticklabels(clf_names, fontsize=10, rotation=15, ha='right')
    ax.set_yticks(range(len(ds_names)))
    ax.set_yticklabels(ds_names, fontsize=11)

    # 셀에 값 표시
    for i in range(len(ds_names)):
        best_j = np.argmax(scores_matrix[i])
        for j in range(len(clf_names)):
            val = scores_matrix[i, j]
            color = 'white' if val > 0.85 else 'black'
            weight = 'bold' if j == best_j else 'normal'
            text = f'{val:.1%}'
            if j == best_j:
                text += '\n★ 최고'
            ax.text(j, i, text, ha='center', va='center',
                    color=color, fontsize=10, fontweight=weight)

    plt.colorbar(im, ax=ax, label='교차 검증 정확도', shrink=0.8)
    ax.set_title('No Free Lunch 정리: 데이터셋별 알고리즘 성능 비교\n'
                 '(5-Fold 교차 검증 정확도)',
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig('02_performance_heatmap.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("[저장 완료] 02_performance_heatmap.png")


# ============================================================
# 6. 시각화 3: 알고리즘별 순위 분석
# ============================================================
def plot_rank_analysis(datasets, classifiers, scores_matrix):
    """
    각 데이터셋에서 알고리즘의 순위를 분석한다.
    NFL 정리의 핵심: 모든 데이터셋에서 1위인 알고리즘은 없다.
    """
    ds_names = [ds[2] for ds in datasets]
    clf_names = [clf[1].replace('\n', ' ') for clf in classifiers]

    # 순위 계산 (높은 정확도 = 1위)
    ranks = np.zeros_like(scores_matrix)
    for i in range(len(ds_names)):
        order = np.argsort(-scores_matrix[i])
        for rank, j in enumerate(order):
            ranks[i, j] = rank + 1

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # 왼쪽: 순위 히트맵
    ax = axes[0]
    im = ax.imshow(ranks, cmap='RdYlGn_r', aspect='auto',
                   vmin=1, vmax=len(clf_names))
    ax.set_xticks(range(len(clf_names)))
    ax.set_xticklabels(clf_names, fontsize=9, rotation=15, ha='right')
    ax.set_yticks(range(len(ds_names)))
    ax.set_yticklabels(ds_names, fontsize=10)

    for i in range(len(ds_names)):
        for j in range(len(clf_names)):
            rank = int(ranks[i, j])
            medal = {1: '🥇', 2: '🥈', 3: '🥉'}.get(rank, str(rank))
            ax.text(j, i, f'{rank}위', ha='center', va='center',
                    fontsize=11, fontweight='bold' if rank == 1 else 'normal')

    ax.set_title('데이터셋별 알고리즘 순위', fontsize=12, fontweight='bold')
    plt.colorbar(im, ax=ax, label='순위 (1=최고)', shrink=0.8)

    # 오른쪽: 평균 순위 막대 그래프
    ax2 = axes[1]
    mean_ranks = ranks.mean(axis=0)
    colors = plt.cm.Set2(np.linspace(0, 1, len(clf_names)))
    bars = ax2.barh(range(len(clf_names)), mean_ranks, color=colors,
                    edgecolor='gray', linewidth=0.5)

    # 값 표시
    for idx, (bar, rank) in enumerate(zip(bars, mean_ranks)):
        ax2.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
                 f'{rank:.1f}', va='center', fontsize=11, fontweight='bold')

    ax2.set_yticks(range(len(clf_names)))
    ax2.set_yticklabels(clf_names, fontsize=10)
    ax2.set_xlabel('평균 순위 (낮을수록 좋음)', fontsize=11)
    ax2.set_title('알고리즘별 평균 순위\n(NFL: 압도적 1위는 없다)',
                  fontsize=12, fontweight='bold')
    ax2.set_xlim(0, len(clf_names) + 0.5)
    ax2.grid(axis='x', alpha=0.3)
    ax2.invert_yaxis()

    plt.suptitle('No Free Lunch 정리 검증: 알고리즘 순위 분석',
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig('02_rank_analysis.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("[저장 완료] 02_rank_analysis.png")


# ============================================================
# 7. 결과 표 출력
# ============================================================
def print_comparison_table(datasets, classifiers, results, scores_matrix):
    """
    콘솔에 비교 결과 표를 출력한다.
    """
    ds_names = [ds[2] for ds in datasets]
    clf_names = [clf[1].replace('\n', ' ') for clf in classifiers]

    print("\n" + "=" * 90)
    print("No Free Lunch 정리 검증: 데이터셋별 알고리즘 성능 비교표")
    print("=" * 90)

    # 헤더
    header = f"{'데이터셋':<18}"
    for name in clf_names:
        header += f" | {name:<16}"
    header += " | 최고 알고리즘"
    print(header)
    print("-" * 90)

    # 각 행
    for i, ds_name in enumerate(ds_names):
        row = f"{ds_name:<18}"
        best_j = np.argmax(scores_matrix[i])
        for j, clf_name in enumerate(clf_names):
            score = scores_matrix[i, j]
            marker = " *" if j == best_j else "  "
            row += f" | {score:.3f}{marker:<11}"
        row += f" | {clf_names[best_j]}"
        print(row)

    print("-" * 90)

    # 각 알고리즘의 1위 횟수
    print(f"\n{'알고리즘별 1위 횟수':}")
    for j, clf_name in enumerate(clf_names):
        wins = sum(1 for i in range(len(ds_names))
                   if np.argmax(scores_matrix[i]) == j)
        print(f"  {clf_name:<25}: {wins}회 / {len(ds_names)}회")

    print(f"\n핵심 결론 (NFL 정리):")
    print(f"  → 모든 데이터셋에서 1위인 단일 알고리즘은 존재하지 않는다!")
    print(f"  → 문제의 특성에 맞는 알고리즘 선택이 핵심이다.")


# ============================================================
# 메인 실행
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("No Free Lunch 정리 데모")
    print("참고: Wolpert & Macready (1997)")
    print("=" * 60)

    # 데이터셋과 분류기 생성
    datasets = create_datasets()
    classifiers = create_classifiers()

    print(f"\n사용 데이터셋 ({len(datasets)}개):")
    for _, _, name, desc in datasets:
        print(f"  - {name}: {desc}")

    print(f"\n사용 알고리즘 ({len(classifiers)}개):")
    for _, name, bias in classifiers:
        print(f"  - {name.replace(chr(10), ' ')}: {bias}")

    # --- 성능 평가 ---
    print(f"\n[1/4] 교차 검증 성능 평가 중...")
    results, scores_matrix = evaluate_all(datasets, classifiers)

    # --- 결과 표 출력 ---
    print_comparison_table(datasets, classifiers, results, scores_matrix)

    # --- 시각화 1: 결정 경계 ---
    print(f"\n[2/4] 결정 경계 시각화 중...")
    plot_decision_boundaries(datasets, classifiers)

    # --- 시각화 2: 성능 히트맵 ---
    print(f"\n[3/4] 성능 히트맵 시각화 중...")
    plot_performance_heatmap(datasets, classifiers, scores_matrix)

    # --- 시각화 3: 순위 분석 ---
    print(f"\n[4/4] 순위 분석 시각화 중...")
    plot_rank_analysis(datasets, classifiers, scores_matrix)

    # --- 최종 요약 ---
    print("\n" + "=" * 60)
    print("최종 요약: No Free Lunch 정리의 시사점")
    print("=" * 60)
    print("""
1. Wolpert & Macready (1997)의 NFL 정리:
   "모든 문제에 대해 평균적으로 최상인 최적화 알고리즘은 존재하지 않는다."

2. 이 실험에서의 관찰:
   - 선형 데이터: 로지스틱 회귀가 단순하면서도 효과적
   - 원형 데이터: RBF 커널 SVM이 비선형 구조를 잘 포착
   - XOR 패턴: 결정 트리 계열이 축 정렬 분할에 유리
   - 반달 데이터: k-NN과 비선형 모델이 유리

3. 실무적 교훈:
   - 항상 여러 알고리즘을 시도하고 비교할 것
   - 데이터의 구조를 먼저 파악한 후 알고리즘을 선택할 것
   - 교차 검증으로 공정한 비교를 수행할 것

[완료] 생성된 파일:
  - 02_decision_boundaries.png
  - 02_performance_heatmap.png
  - 02_rank_analysis.png
""")
