"""
02_cart_pruning.py
비용-복잡도 가지치기(Cost-Complexity Pruning, CART) 구현 및 시각화

핵심 구현 내용:
1. 완전 트리 성장(Full Tree Growth)
2. 비용-복잡도 경로(Cost-Complexity Pruning Path) 계산
3. 각 하위 트리의 alpha 계산
4. 교차검증을 통한 최적 alpha 선택
5. 가지치기 전후 트리 시각화
6. 1-SE Rule 적용

데이터셋: Breast Cancer (sklearn 내장)
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.metrics import accuracy_score


# ============================================================
# 1. 데이터 로드 및 전처리
# ============================================================

print("=" * 70)
print("  비용-복잡도 가지치기 (Cost-Complexity Pruning) 분석")
print("=" * 70)

# 유방암 데이터셋 로드
cancer = load_breast_cancer()
X, y = cancer.data, cancer.target
feature_names = cancer.feature_names
target_names = cancer.target_names

print(f"\n[데이터 정보]")
print(f"  샘플 수: {X.shape[0]}")
print(f"  특성 수: {X.shape[1]}")
print(f"  클래스: {target_names}")
print(f"  클래스 분포: 악성(0)={sum(y == 0)}개, 양성(1)={sum(y == 1)}개")

# 학습/테스트 분할
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)
print(f"  학습 데이터: {len(y_train)}개, 테스트 데이터: {len(y_test)}개")


# ============================================================
# 2. 완전 트리 성장 (Full Tree)
# ============================================================

print("\n[1] 완전 트리 (가지치기 없음) 성장")

# 제한 없이 완전히 성장시킨 트리
full_tree = DecisionTreeClassifier(random_state=42)
full_tree.fit(X_train, y_train)

full_train_acc = accuracy_score(y_train, full_tree.predict(X_train))
full_test_acc = accuracy_score(y_test, full_tree.predict(X_test))

print(f"  완전 트리 깊이: {full_tree.get_depth()}")
print(f"  리프 노드 수: {full_tree.get_n_leaves()}")
print(f"  Train Accuracy: {full_train_acc:.4f}")
print(f"  Test Accuracy:  {full_test_acc:.4f}")
print(f"  과적합 격차: {full_train_acc - full_test_acc:.4f}")


# ============================================================
# 3. 비용-복잡도 가지치기 경로 (CCP Path) 계산
# ============================================================

print("\n[2] 비용-복잡도 가지치기 경로 계산")

# ccp_alphas: 각 alpha에서의 유효 alpha 값
# impurities: 각 alpha에서의 총 불순도
path = full_tree.cost_complexity_pruning_path(X_train, y_train)
ccp_alphas = path.ccp_alphas
impurities = path.impurities

print(f"  가능한 alpha 값 개수: {len(ccp_alphas)}")
print(f"  alpha 범위: [{ccp_alphas[0]:.6f}, {ccp_alphas[-1]:.6f}]")

# alpha에 따른 불순도 변화 시각화
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(ccp_alphas[:-1], impurities[:-1], 'o-', markersize=3, color='steelblue')
ax.set_xlabel('alpha (복잡도 파라미터)', fontsize=12)
ax.set_ylabel('총 불순도 (Total Impurity)', fontsize=12)
ax.set_title('alpha에 따른 트리의 총 불순도 변화', fontsize=14)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('ccp_alpha_impurity.png', dpi=150, bbox_inches='tight')
plt.show()
print("  [시각화] alpha-불순도 그래프 저장 완료")


# ============================================================
# 4. alpha별 트리 학습 및 성능 변화
# ============================================================

print("\n[3] alpha별 트리 학습 및 성능 분석")

# 각 alpha에 대해 트리를 학습
trees = []
train_scores = []
test_scores = []
n_leaves_list = []
depths_list = []

for alpha in ccp_alphas:
    tree = DecisionTreeClassifier(ccp_alpha=alpha, random_state=42)
    tree.fit(X_train, y_train)
    trees.append(tree)
    train_scores.append(accuracy_score(y_train, tree.predict(X_train)))
    test_scores.append(accuracy_score(y_test, tree.predict(X_test)))
    n_leaves_list.append(tree.get_n_leaves())
    depths_list.append(tree.get_depth())

# 성능 변화 시각화
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# (a) alpha에 따른 Train/Test 정확도
ax = axes[0]
ax.plot(ccp_alphas, train_scores, 'b-o', markersize=2, label='Train', linewidth=1.5)
ax.plot(ccp_alphas, test_scores, 'r-s', markersize=2, label='Test', linewidth=1.5)
ax.set_xlabel('alpha', fontsize=12)
ax.set_ylabel('Accuracy', fontsize=12)
ax.set_title('alpha에 따른 정확도 변화', fontsize=13)
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)

# (b) alpha에 따른 리프 노드 수
ax = axes[1]
ax.plot(ccp_alphas, n_leaves_list, 'g-o', markersize=2, linewidth=1.5)
ax.set_xlabel('alpha', fontsize=12)
ax.set_ylabel('리프 노드 수', fontsize=12)
ax.set_title('alpha에 따른 트리 복잡도 변화', fontsize=13)
ax.grid(True, alpha=0.3)

# (c) alpha에 따른 트리 깊이
ax = axes[2]
ax.plot(ccp_alphas, depths_list, 'm-o', markersize=2, linewidth=1.5)
ax.set_xlabel('alpha', fontsize=12)
ax.set_ylabel('트리 깊이', fontsize=12)
ax.set_title('alpha에 따른 트리 깊이 변화', fontsize=13)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('ccp_alpha_performance.png', dpi=150, bbox_inches='tight')
plt.show()
print("  [시각화] alpha별 성능 변화 그래프 저장 완료")


# ============================================================
# 5. 교차검증을 통한 최적 alpha 선택
# ============================================================

print("\n[4] 5-폴드 교차검증으로 최적 alpha 선택")

# 합리적 범위의 alpha만 사용 (계산 효율)
# alpha가 너무 크면 리프만 남으므로, 합리적 범위로 제한
reasonable_alphas = ccp_alphas[ccp_alphas <= 0.05]

cv_means = []
cv_stds = []

for alpha in reasonable_alphas:
    tree = DecisionTreeClassifier(ccp_alpha=alpha, random_state=42)
    scores = cross_val_score(tree, X_train, y_train, cv=5,
                              scoring='accuracy')
    cv_means.append(scores.mean())
    cv_stds.append(scores.std())

cv_means = np.array(cv_means)
cv_stds = np.array(cv_stds)

# 최적 alpha: CV 정확도가 최대인 지점
best_idx = np.argmax(cv_means)
best_alpha = reasonable_alphas[best_idx]
best_cv_mean = cv_means[best_idx]
best_cv_std = cv_stds[best_idx]

print(f"  최적 alpha: {best_alpha:.6f}")
print(f"  최적 CV 정확도: {best_cv_mean:.4f} (+/- {best_cv_std:.4f})")

# 1-SE Rule 적용
# CV 정확도가 (최적 - 1*SE) 이상인 범위에서 가장 큰 alpha 선택
one_se_threshold = best_cv_mean - best_cv_std
one_se_candidates = reasonable_alphas[cv_means >= one_se_threshold]
alpha_1se = one_se_candidates[-1] if len(one_se_candidates) > 0 else best_alpha

print(f"\n  [1-SE Rule 적용]")
print(f"  1-SE 임계값: {one_se_threshold:.4f}")
print(f"  1-SE alpha: {alpha_1se:.6f}")

# 교차검증 결과 시각화
fig, ax = plt.subplots(figsize=(10, 6))
ax.errorbar(reasonable_alphas, cv_means, yerr=cv_stds,
            fmt='o-', markersize=3, capsize=3, linewidth=1.5,
            color='steelblue', label='CV 정확도 (mean +/- std)')
ax.axvline(x=best_alpha, color='red', linestyle='--', linewidth=1.5,
           label=f'최적 alpha = {best_alpha:.4f}')
ax.axvline(x=alpha_1se, color='green', linestyle='-.', linewidth=1.5,
           label=f'1-SE alpha = {alpha_1se:.4f}')
ax.axhline(y=one_se_threshold, color='gray', linestyle=':', alpha=0.7,
           label=f'1-SE 임계값 = {one_se_threshold:.4f}')
ax.set_xlabel('alpha (복잡도 파라미터)', fontsize=12)
ax.set_ylabel('교차검증 정확도', fontsize=12)
ax.set_title('교차검증을 통한 최적 alpha 선택', fontsize=14)
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('ccp_cv_alpha_selection.png', dpi=150, bbox_inches='tight')
plt.show()
print("  [시각화] 교차검증 alpha 선택 그래프 저장 완료")


# ============================================================
# 6. 가지치기 전후 트리 비교
# ============================================================

print("\n[5] 가지치기 전후 트리 비교")

# 가지치기 후 트리 (최적 alpha)
pruned_tree_best = DecisionTreeClassifier(ccp_alpha=best_alpha, random_state=42)
pruned_tree_best.fit(X_train, y_train)

# 가지치기 후 트리 (1-SE alpha)
pruned_tree_1se = DecisionTreeClassifier(ccp_alpha=alpha_1se, random_state=42)
pruned_tree_1se.fit(X_train, y_train)

# 성능 비교
models = {
    '완전 트리 (alpha=0)': full_tree,
    f'최적 alpha ({best_alpha:.4f})': pruned_tree_best,
    f'1-SE alpha ({alpha_1se:.4f})': pruned_tree_1se,
}

print(f"\n  {'모델':<30} | {'깊이':>4} | {'리프':>4} | {'Train':>8} | {'Test':>8} | {'격차':>8}")
print(f"  {'-' * 75}")

for name, model in models.items():
    train_acc = accuracy_score(y_train, model.predict(X_train))
    test_acc = accuracy_score(y_test, model.predict(X_test))
    print(f"  {name:<30} | {model.get_depth():>4} | {model.get_n_leaves():>4} | "
          f"{train_acc:>8.4f} | {test_acc:>8.4f} | {train_acc - test_acc:>8.4f}")


# ============================================================
# 7. 트리 시각화 (가지치기 전후)
# ============================================================

print("\n[6] 트리 시각화")

# 완전 트리 (상위 3단계만)
fig, ax = plt.subplots(figsize=(24, 10))
plot_tree(full_tree, max_depth=3,
          feature_names=feature_names,
          class_names=target_names,
          filled=True, rounded=True, fontsize=9, ax=ax)
ax.set_title(f'완전 트리 (깊이={full_tree.get_depth()}, '
             f'리프={full_tree.get_n_leaves()}) - 상위 3단계만 표시',
             fontsize=14)
plt.tight_layout()
plt.savefig('tree_full_top3.png', dpi=150, bbox_inches='tight')
plt.show()

# 가지치기 후 트리 (최적 alpha)
fig, ax = plt.subplots(figsize=(24, 10))
plot_tree(pruned_tree_best,
          feature_names=feature_names,
          class_names=target_names,
          filled=True, rounded=True, fontsize=9, ax=ax)
ax.set_title(f'가지치기 후 트리 (alpha={best_alpha:.4f}, '
             f'깊이={pruned_tree_best.get_depth()}, '
             f'리프={pruned_tree_best.get_n_leaves()})',
             fontsize=14)
plt.tight_layout()
plt.savefig('tree_pruned_best.png', dpi=150, bbox_inches='tight')
plt.show()

# 1-SE Rule 트리
fig, ax = plt.subplots(figsize=(20, 8))
plot_tree(pruned_tree_1se,
          feature_names=feature_names,
          class_names=target_names,
          filled=True, rounded=True, fontsize=10, ax=ax)
ax.set_title(f'1-SE Rule 트리 (alpha={alpha_1se:.4f}, '
             f'깊이={pruned_tree_1se.get_depth()}, '
             f'리프={pruned_tree_1se.get_n_leaves()})',
             fontsize=14)
plt.tight_layout()
plt.savefig('tree_pruned_1se.png', dpi=150, bbox_inches='tight')
plt.show()

print("  [시각화] 가지치기 전후 트리 시각화 저장 완료")


# ============================================================
# 8. 요약
# ============================================================

print("\n" + "=" * 70)
print("  비용-복잡도 가지치기 분석 요약")
print("=" * 70)
print(f"""
  [핵심 결과]
  1. 완전 트리: 깊이={full_tree.get_depth()}, 리프={full_tree.get_n_leaves()},
     Train={full_train_acc:.4f}, Test={full_test_acc:.4f}
     -> 과적합 존재 (격차: {full_train_acc - full_test_acc:.4f})

  2. 최적 alpha={best_alpha:.4f}: 깊이={pruned_tree_best.get_depth()},
     리프={pruned_tree_best.get_n_leaves()},
     Test={accuracy_score(y_test, pruned_tree_best.predict(X_test)):.4f}

  3. 1-SE alpha={alpha_1se:.4f}: 깊이={pruned_tree_1se.get_depth()},
     리프={pruned_tree_1se.get_n_leaves()},
     Test={accuracy_score(y_test, pruned_tree_1se.predict(X_test)):.4f}

  [결론]
  - 비용-복잡도 가지치기는 트리의 과적합을 효과적으로 제어한다.
  - 1-SE Rule은 "비슷한 성능 범위에서 가장 단순한 모델"을 선택하는 원칙이다.
  - alpha를 교차검증으로 선택하면 데이터에 적합한 최적 복잡도를 찾을 수 있다.
""")
