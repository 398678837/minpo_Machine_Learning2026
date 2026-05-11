"""
03_tree_ensemble_basics.py
단일 의사결정나무의 불안정성과 앙상블의 동기 부여

핵심 내용:
1. 부트스트랩 샘플에서의 트리 학습 - 구조적 불안정성 확인
2. 10개 트리의 예측 분산(variance) 비교
3. 다수결 투표(앙상블)의 분산 감소 효과 시각화
4. 앙상블 크기에 따른 성능 안정화 관찰

데이터셋: Iris (sklearn 내장)
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris, make_moons
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from collections import Counter


# ============================================================
# 1. 데이터 준비
# ============================================================

print("=" * 70)
print("  단일 트리의 불안정성과 앙상블 동기 부여")
print("=" * 70)

# Iris 데이터셋 로드
iris = load_iris()
X, y = iris.data, iris.target
feature_names = iris.feature_names

# 학습/테스트 분할
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

print(f"\n[데이터 정보]")
print(f"  학습 데이터: {X_train.shape[0]}개")
print(f"  테스트 데이터: {X_test.shape[0]}개")
print(f"  특성 수: {X_train.shape[1]}개")


# ============================================================
# 2. 부트스트랩 샘플에서 10개 트리 학습
# ============================================================

print("\n[1] 부트스트랩 샘플에서 10개 독립 트리 학습")

n_trees = 10
np.random.seed(42)

trees = []
train_accuracies = []
test_accuracies = []
tree_predictions = []  # 각 트리의 테스트 데이터 예측
feature_importances_list = []

for i in range(n_trees):
    # 부트스트랩 샘플링 (중복 허용 랜덤 추출)
    n_samples = len(X_train)
    bootstrap_idx = np.random.choice(n_samples, size=n_samples, replace=True)
    X_boot = X_train[bootstrap_idx]
    y_boot = y_train[bootstrap_idx]

    # 고유 샘플 비율 계산
    unique_ratio = len(set(bootstrap_idx)) / n_samples

    # 트리 학습 (가지치기 없이 완전 성장)
    tree = DecisionTreeClassifier(random_state=None)  # 랜덤 시드 다르게
    tree.fit(X_boot, y_boot)
    trees.append(tree)

    # 성능 측정
    train_acc = accuracy_score(y_train, tree.predict(X_train))
    test_acc = accuracy_score(y_test, tree.predict(X_test))
    train_accuracies.append(train_acc)
    test_accuracies.append(test_acc)

    # 예측 저장
    tree_predictions.append(tree.predict(X_test))
    feature_importances_list.append(tree.feature_importances_)

    print(f"  트리 {i + 1:2d}: 고유샘플={unique_ratio:.1%}, "
          f"깊이={tree.get_depth()}, "
          f"Train={train_acc:.4f}, Test={test_acc:.4f}")

print(f"\n  [통계 요약]")
print(f"  Train Accuracy: 평균={np.mean(train_accuracies):.4f}, "
      f"표준편차={np.std(train_accuracies):.4f}")
print(f"  Test Accuracy:  평균={np.mean(test_accuracies):.4f}, "
      f"표준편차={np.std(test_accuracies):.4f}")


# ============================================================
# 3. 예측 분산 분석
# ============================================================

print("\n[2] 예측 분산 분석")

# 각 테스트 샘플에 대해 10개 트리의 예측 변동 확인
predictions_array = np.array(tree_predictions)  # (10, n_test)

# 각 샘플별 예측 일치도 (모든 트리가 같은 클래스를 예측하는 비율)
agreement_ratios = []
for j in range(len(y_test)):
    sample_preds = predictions_array[:, j]
    most_common_count = Counter(sample_preds).most_common(1)[0][1]
    agreement_ratios.append(most_common_count / n_trees)

agreement_ratios = np.array(agreement_ratios)

print(f"  완전 일치 (10/10 동의) 샘플 비율: "
      f"{np.mean(agreement_ratios == 1.0):.1%}")
print(f"  높은 일치 (>= 8/10 동의) 샘플 비율: "
      f"{np.mean(agreement_ratios >= 0.8):.1%}")
print(f"  낮은 일치 (< 7/10 동의) 샘플 비율: "
      f"{np.mean(agreement_ratios < 0.7):.1%}")

# 불일치가 높은 샘플 출력
low_agreement_idx = np.where(agreement_ratios < 0.7)[0]
if len(low_agreement_idx) > 0:
    print(f"\n  [불안정한 예측 사례] (10개 트리 중 동의율 < 70%)")
    for idx in low_agreement_idx[:5]:  # 최대 5개만 출력
        preds = predictions_array[:, idx]
        actual = y_test[idx]
        pred_counts = Counter(preds)
        print(f"    샘플 {idx}: 실제={iris.target_names[actual]}, "
              f"예측 분포={dict(pred_counts)}, "
              f"동의율={agreement_ratios[idx]:.0%}")


# ============================================================
# 4. 다수결 투표 (Simple Ensemble)
# ============================================================

print("\n[3] 다수결 투표 앙상블 vs 개별 트리")

# 다수결 투표로 앙상블 예측
ensemble_predictions = []
for j in range(len(y_test)):
    sample_preds = predictions_array[:, j]
    # 가장 많이 예측된 클래스를 선택
    majority_vote = Counter(sample_preds).most_common(1)[0][0]
    ensemble_predictions.append(majority_vote)

ensemble_predictions = np.array(ensemble_predictions)
ensemble_acc = accuracy_score(y_test, ensemble_predictions)

print(f"\n  개별 트리 Test Accuracy:")
for i, acc in enumerate(test_accuracies):
    marker = " <-- 최고" if acc == max(test_accuracies) else ""
    print(f"    트리 {i + 1:2d}: {acc:.4f}{marker}")

print(f"\n  10개 트리 다수결 투표 앙상블 Accuracy: {ensemble_acc:.4f}")
print(f"  개별 트리 평균 Accuracy:               {np.mean(test_accuracies):.4f}")
print(f"  개별 트리 최고 Accuracy:               {max(test_accuracies):.4f}")

improvement = ensemble_acc - np.mean(test_accuracies)
print(f"\n  앙상블 효과 (평균 대비 개선): {improvement:+.4f}")


# ============================================================
# 5. 특성 중요도의 불안정성
# ============================================================

print("\n[4] 특성 중요도의 불안정성")

importances_array = np.array(feature_importances_list)  # (10, 4)

print(f"\n  {'특성':<25} | {'평균':>8} | {'표준편차':>8} | {'최소':>8} | {'최대':>8}")
print(f"  {'-' * 65}")
for i, name in enumerate(feature_names):
    vals = importances_array[:, i]
    print(f"  {name:<25} | {np.mean(vals):>8.4f} | {np.std(vals):>8.4f} | "
          f"{np.min(vals):>8.4f} | {np.max(vals):>8.4f}")

# 특성 중요도 분산 시각화
fig, ax = plt.subplots(figsize=(10, 6))
bp = ax.boxplot([importances_array[:, i] for i in range(len(feature_names))],
                labels=feature_names, patch_artist=True)

colors = ['#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)

ax.set_ylabel('특성 중요도 (Feature Importance)', fontsize=12)
ax.set_title('10개 부트스트랩 트리의 특성 중요도 분포\n'
             '(각 트리마다 중요도가 크게 변동 = 불안정성)', fontsize=13)
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig('feature_importance_variance.png', dpi=150, bbox_inches='tight')
plt.show()
print("  [시각화] 특성 중요도 분산 그래프 저장 완료")


# ============================================================
# 6. 앙상블 크기에 따른 성능 변화
# ============================================================

print("\n[5] 앙상블 크기에 따른 성능 안정화")

np.random.seed(123)
max_trees = 100

# 더 많은 부트스트랩 트리 학습
all_predictions = []
for i in range(max_trees):
    n_samples = len(X_train)
    bootstrap_idx = np.random.choice(n_samples, size=n_samples, replace=True)
    tree = DecisionTreeClassifier(random_state=None)
    tree.fit(X_train[bootstrap_idx], y_train[bootstrap_idx])
    all_predictions.append(tree.predict(X_test))

all_predictions = np.array(all_predictions)  # (max_trees, n_test)

# 앙상블 크기를 1부터 max_trees까지 증가시키며 성능 추적
ensemble_sizes = range(1, max_trees + 1)
ensemble_accuracies = []

for size in ensemble_sizes:
    # 처음 size개의 트리로 다수결 투표
    subset_preds = all_predictions[:size, :]
    ensemble_pred = np.zeros(len(y_test), dtype=int)

    for j in range(len(y_test)):
        votes = subset_preds[:, j]
        ensemble_pred[j] = Counter(votes).most_common(1)[0][0]

    ensemble_accuracies.append(accuracy_score(y_test, ensemble_pred))

# 시각화
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(ensemble_sizes, ensemble_accuracies, 'b-', linewidth=1.5,
        label='앙상블 (다수결 투표) 정확도')

# 개별 트리의 평균과 범위
individual_accs = [accuracy_score(y_test, all_predictions[i, :])
                   for i in range(max_trees)]
ax.axhline(y=np.mean(individual_accs), color='red', linestyle='--',
           linewidth=1.5, label=f'개별 트리 평균 ({np.mean(individual_accs):.4f})')
ax.fill_between(ensemble_sizes,
                np.min(individual_accs), np.max(individual_accs),
                alpha=0.1, color='red', label='개별 트리 범위')

ax.set_xlabel('트리 수 (앙상블 크기)', fontsize=12)
ax.set_ylabel('테스트 정확도', fontsize=12)
ax.set_title('앙상블 크기에 따른 성능 변화\n'
             '(트리가 많아질수록 예측이 안정적으로 수렴)', fontsize=14)
ax.legend(fontsize=11, loc='lower right')
ax.grid(True, alpha=0.3)
ax.set_xlim([1, max_trees])
plt.tight_layout()
plt.savefig('ensemble_size_effect.png', dpi=150, bbox_inches='tight')
plt.show()
print("  [시각화] 앙상블 크기 효과 그래프 저장 완료")


# ============================================================
# 7. 2D 결정 경계 비교 (make_moons 데이터)
# ============================================================

print("\n[6] 결정 경계 비교 (2D 데이터)")

# 2D 데이터 생성 (시각화 용이)
X_2d, y_2d = make_moons(n_samples=300, noise=0.3, random_state=42)
X_train_2d, X_test_2d, y_train_2d, y_test_2d = train_test_split(
    X_2d, y_2d, test_size=0.3, random_state=42
)

# 결정 경계 시각화 함수
def plot_decision_boundary(ax, model, X, y, title):
    """모델의 결정 경계를 시각화한다."""
    h = 0.02
    x_min, x_max = X[:, 0].min() - 0.5, X[:, 0].max() + 0.5
    y_min, y_max = X[:, 1].min() - 0.5, X[:, 1].max() + 0.5
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                          np.arange(y_min, y_max, h))
    Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)
    ax.contourf(xx, yy, Z, alpha=0.3, cmap=plt.cm.RdYlBu)
    ax.scatter(X[:, 0], X[:, 1], c=y, cmap=plt.cm.RdYlBu,
               edgecolors='black', s=20)
    ax.set_title(title, fontsize=10)
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

# 부트스트랩 트리 6개의 결정 경계 비교
fig, axes = plt.subplots(2, 3, figsize=(15, 9))
np.random.seed(42)

for i, ax in enumerate(axes.flat):
    if i < 5:
        # 부트스트랩 샘플 트리
        n_samples = len(X_train_2d)
        boot_idx = np.random.choice(n_samples, size=n_samples, replace=True)
        tree = DecisionTreeClassifier(random_state=None)
        tree.fit(X_train_2d[boot_idx], y_train_2d[boot_idx])
        acc = accuracy_score(y_test_2d, tree.predict(X_test_2d))
        plot_decision_boundary(
            ax, tree, X_test_2d, y_test_2d,
            f'부트스트랩 트리 {i + 1} (Acc={acc:.2f})'
        )
    else:
        # 앙상블 (5개 트리의 다수결)
        # 간단한 앙상블 구현
        class SimpleEnsemble:
            def __init__(self, trees):
                self.trees = trees
            def predict(self, X):
                preds = np.array([t.predict(X) for t in self.trees])
                return np.array([
                    Counter(preds[:, j]).most_common(1)[0][0]
                    for j in range(X.shape[0])
                ])

        np.random.seed(42)
        ens_trees = []
        for _ in range(20):
            boot_idx = np.random.choice(
                len(X_train_2d), size=len(X_train_2d), replace=True
            )
            t = DecisionTreeClassifier(random_state=None)
            t.fit(X_train_2d[boot_idx], y_train_2d[boot_idx])
            ens_trees.append(t)

        ensemble = SimpleEnsemble(ens_trees)
        ens_acc = accuracy_score(y_test_2d, ensemble.predict(X_test_2d))
        plot_decision_boundary(
            ax, ensemble, X_test_2d, y_test_2d,
            f'앙상블 20개 트리 (Acc={ens_acc:.2f})'
        )

fig.suptitle('단일 트리의 불안정성 vs 앙상블의 안정성\n'
             '(각 부트스트랩 트리는 서로 다른 결정 경계를 학습한다)',
             fontsize=14, y=1.02)
plt.tight_layout()
plt.savefig('decision_boundary_variance.png', dpi=150, bbox_inches='tight')
plt.show()
print("  [시각화] 결정 경계 비교 그래프 저장 완료")


# ============================================================
# 8. 요약
# ============================================================

print("\n" + "=" * 70)
print("  분석 요약")
print("=" * 70)
print(f"""
  [핵심 발견]

  1. 단일 트리의 불안정성 (High Variance):
     - 같은 데이터에서 부트스트랩 샘플만 다르게 해도 트리 구조가 크게 변한다.
     - 테스트 정확도의 표준편차: {np.std(test_accuracies):.4f}
     - 특성 중요도도 트리마다 크게 변동한다.

  2. 앙상블의 분산 감소 효과:
     - 개별 트리 평균 정확도: {np.mean(test_accuracies):.4f}
     - 10개 트리 다수결 정확도: {ensemble_acc:.4f}
     - 앙상블이 개별 트리보다 안정적이고 대체로 더 정확하다.

  3. 앙상블 크기의 효과:
     - 트리 수가 증가하면 성능이 안정적으로 수렴한다.
     - 일정 수 이상에서는 추가 트리의 효과가 미미하다.
     - 이것이 랜덤 포레스트의 n_estimators 파라미터의 의미이다.

  [동기 부여: 왜 앙상블이 필요한가?]
     - 단일 트리는 데이터의 작은 변동에도 구조가 크게 바뀐다 (높은 분산).
     - 여러 트리를 결합하면 개별 트리의 오류가 상쇄되어 분산이 감소한다.
     - 이 아이디어를 체계화한 것이 배깅(Bagging)이고,
       여기에 특성 랜덤 선택을 추가한 것이 랜덤 포레스트(Random Forest)이다.
""")
