"""
02_feature_importance_analysis.py
MDI(지니 중요도) vs 순열 중요도(Permutation Importance) 비교 분석

Strobl et al. (2007) "Bias in Random Forest Variable Importance Measures" 기반

핵심 구현 내용:
1. MDI (Mean Decrease in Impurity, 지니 중요도) - sklearn 기본 제공
2. 순열 중요도 (Permutation Importance) - 직접 구현 + sklearn 비교
3. 카디널리티 편향 시연: 고카디널리티 변수가 MDI에서 과대평가되는 현상
4. 상관 변수에서의 편향 분석

데이터셋: 합성 데이터 + Breast Cancer
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.inspection import permutation_importance
import warnings
warnings.filterwarnings('ignore')


# ============================================================
# 1. 순열 중요도 직접 구현 (Scratch)
# ============================================================

def permutation_importance_scratch(model, X, y, n_repeats=10,
                                    random_state=42):
    """
    순열 중요도를 직접 구현한다.

    Strobl et al. (2007)의 방법:
    1. 원래 데이터에서 모델의 정확도를 계산한다.
    2. 각 특성 j에 대해:
       a. 특성 j의 값을 무작위로 섞는다.
       b. 섞은 데이터에서 정확도를 계산한다.
       c. 정확도 감소량 = 원래 정확도 - 섞은 정확도
    3. n_repeats번 반복하여 평균과 표준편차를 계산한다.

    Parameters
    ----------
    model : 학습된 모델
    X : numpy.ndarray, shape (n_samples, n_features)
    y : numpy.ndarray, shape (n_samples,)
    n_repeats : int
        반복 횟수
    random_state : int
        랜덤 시드

    Returns
    -------
    dict : importances_mean, importances_std, importances (n_repeats x n_features)
    """
    rng = np.random.RandomState(random_state)
    n_features = X.shape[1]

    # 원래 정확도
    baseline_score = accuracy_score(y, model.predict(X))

    # 결과 저장 배열
    importances = np.zeros((n_repeats, n_features))

    for repeat in range(n_repeats):
        for feat_idx in range(n_features):
            # 특성 j의 값을 섞은 데이터 생성
            X_permuted = X.copy()
            X_permuted[:, feat_idx] = rng.permutation(X_permuted[:, feat_idx])

            # 섞은 데이터에서 정확도 계산
            permuted_score = accuracy_score(y, model.predict(X_permuted))

            # 정확도 감소량 = 중요도
            importances[repeat, feat_idx] = baseline_score - permuted_score

    return {
        'importances_mean': importances.mean(axis=0),
        'importances_std': importances.std(axis=0),
        'importances': importances
    }


# ============================================================
# 2. 카디널리티 편향 시연
# ============================================================

print("=" * 70)
print("  MDI vs 순열 중요도 비교 분석")
print("  (Strobl et al. 2007 재현)")
print("=" * 70)

print("\n[1] 카디널리티 편향 시연")
print("  -> 모든 변수가 타겟과 무관한 데이터에서 MDI의 편향을 확인")

np.random.seed(42)
n_samples = 1000

# 타겟과 완전히 무관한 변수 생성 (다양한 카디널리티)
X_bias = np.column_stack([
    np.random.choice(2, n_samples),       # X0: 2값 범주형
    np.random.choice(2, n_samples),       # X1: 2값 범주형
    np.random.choice(5, n_samples),       # X2: 5값 범주형
    np.random.choice(5, n_samples),       # X3: 5값 범주형
    np.random.choice(20, n_samples),      # X4: 20값 범주형
    np.random.choice(20, n_samples),      # X5: 20값 범주형
    np.random.uniform(0, 1, n_samples),   # X6: 연속형
    np.random.uniform(0, 1, n_samples),   # X7: 연속형
])

# 타겟: 변수와 완전히 무관하게 랜덤 생성
y_bias = np.random.choice(2, n_samples)

bias_feature_names = [
    'X0 (2값)', 'X1 (2값)',
    'X2 (5값)', 'X3 (5값)',
    'X4 (20값)', 'X5 (20값)',
    'X6 (연속)', 'X7 (연속)'
]

# 랜덤 포레스트 학습
rf_bias = RandomForestClassifier(
    n_estimators=500, max_depth=10, random_state=42, n_jobs=-1
)
rf_bias.fit(X_bias, y_bias)

# MDI (지니 중요도) - sklearn 기본 제공
mdi_importances = rf_bias.feature_importances_

# 순열 중요도
perm_result = permutation_importance(
    rf_bias, X_bias, y_bias, n_repeats=30, random_state=42, n_jobs=-1
)
perm_importances = perm_result.importances_mean

# 결과 출력
print(f"\n  {'특성':<15} | {'카디널리티':>10} | {'MDI(지니)':>12} | {'순열 중요도':>12}")
print(f"  {'-' * 58}")
cardinalities = [2, 2, 5, 5, 20, 20, '연속', '연속']
for i, name in enumerate(bias_feature_names):
    print(f"  {name:<15} | {str(cardinalities[i]):>10} | "
          f"{mdi_importances[i]:>12.4f} | {perm_importances[i]:>12.4f}")

print(f"\n  [해석]")
print(f"  - MDI: 카디널리티가 높은 변수(연속형 > 20값 > 5값 > 2값)가 더 높은 중요도")
print(f"  - 순열 중요도: 모든 변수가 0 근처 (올바른 결과 - 모두 무관)")
print(f"  -> MDI의 카디널리티 편향이 명확하게 확인됨!")

# 시각화
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

ax = axes[0]
colors = ['#4ECDC4'] * 2 + ['#45B7D1'] * 2 + ['#96CEB4'] * 2 + ['#FF6B6B'] * 2
sorted_idx = np.argsort(mdi_importances)
ax.barh(range(len(bias_feature_names)),
        mdi_importances[sorted_idx],
        color=[colors[i] for i in sorted_idx])
ax.set_yticks(range(len(bias_feature_names)))
ax.set_yticklabels([bias_feature_names[i] for i in sorted_idx])
ax.set_xlabel('MDI (지니 중요도)', fontsize=11)
ax.set_title('MDI: 카디널리티 편향 존재\n(모든 변수가 무관한데도 연속형이 높음)',
             fontsize=12)
ax.grid(True, alpha=0.3, axis='x')

ax = axes[1]
sorted_idx2 = np.argsort(perm_importances)
ax.barh(range(len(bias_feature_names)),
        perm_importances[sorted_idx2],
        color=[colors[i] for i in sorted_idx2])
ax.set_yticks(range(len(bias_feature_names)))
ax.set_yticklabels([bias_feature_names[i] for i in sorted_idx2])
ax.set_xlabel('순열 중요도 (Permutation)', fontsize=11)
ax.set_title('순열 중요도: 편향 없음\n(모든 변수가 0 근처 = 올바른 결과)',
             fontsize=12)
ax.axvline(x=0, color='red', linestyle='--', linewidth=1)
ax.grid(True, alpha=0.3, axis='x')

plt.tight_layout()
plt.savefig('cardinality_bias_comparison.png', dpi=150, bbox_inches='tight')
plt.show()
print("  [시각화] 카디널리티 편향 비교 그래프 저장 완료")


# ============================================================
# 3. 상관 변수에서의 편향 분석
# ============================================================

print(f"\n[2] 상관 변수에서의 중요도 분석")

np.random.seed(42)
n_samples = 1000

# X1: 타겟과 관련된 진짜 중요한 변수
X1 = np.random.randn(n_samples)

# X2: X1과 높은 상관 (rho=0.9), 타겟과는 간접적 관련
X2 = 0.9 * X1 + 0.1 * np.random.randn(n_samples)

# X3: 타겟과 약하게 관련
X3 = np.random.randn(n_samples)

# X4: 타겟과 무관한 노이즈
X4 = np.random.randn(n_samples)

# 타겟: X1 + 약간의 X3 기반
y_corr = (X1 + 0.3 * X3 + 0.5 * np.random.randn(n_samples) > 0).astype(int)

X_corr = np.column_stack([X1, X2, X3, X4])
corr_feature_names = ['X1 (진짜 중요)', 'X2 (X1과 상관 0.9)',
                       'X3 (약하게 관련)', 'X4 (무관)']

# 상관계수 확인
print(f"  상관계수 행렬:")
corr_matrix = np.corrcoef(X_corr.T)
for i in range(4):
    row = "  "
    for j in range(4):
        row += f"{corr_matrix[i, j]:>8.3f}"
    print(row)

# 학습/테스트 분할
X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(
    X_corr, y_corr, test_size=0.3, random_state=42
)

# 랜덤 포레스트 학습
rf_corr = RandomForestClassifier(
    n_estimators=500, max_depth=10, random_state=42, n_jobs=-1
)
rf_corr.fit(X_train_c, y_train_c)

# MDI
mdi_corr = rf_corr.feature_importances_

# 순열 중요도 (Scratch 구현)
perm_scratch = permutation_importance_scratch(
    rf_corr, X_test_c, y_test_c, n_repeats=30, random_state=42
)

# 순열 중요도 (sklearn)
perm_sklearn = permutation_importance(
    rf_corr, X_test_c, y_test_c, n_repeats=30, random_state=42, n_jobs=-1
)

print(f"\n  {'특성':<25} | {'MDI':>8} | {'Perm(Scratch)':>14} | {'Perm(sklearn)':>14}")
print(f"  {'-' * 68}")
for i, name in enumerate(corr_feature_names):
    print(f"  {name:<25} | {mdi_corr[i]:>8.4f} | "
          f"{perm_scratch['importances_mean'][i]:>14.4f} | "
          f"{perm_sklearn.importances_mean[i]:>14.4f}")

print(f"\n  [해석]")
print(f"  - X1(진짜 중요)과 X2(X1과 상관): MDI에서는 두 변수 모두 높은 중요도")
print(f"  - 순열 중요도에서는 X1이 X2보다 높지만, 상관 때문에 X1도 과소평가될 수 있음")
print(f"  - X2는 X1의 대리(proxy) 역할을 하므로 간접적 중요도를 가짐")


# ============================================================
# 4. 실제 데이터에서의 비교 (Breast Cancer)
# ============================================================

print(f"\n[3] 실제 데이터에서의 MDI vs 순열 중요도 비교 (Breast Cancer)")

cancer = load_breast_cancer()
X_bc, y_bc = cancer.data, cancer.target
bc_features = cancer.feature_names

X_train_bc, X_test_bc, y_train_bc, y_test_bc = train_test_split(
    X_bc, y_bc, test_size=0.3, random_state=42, stratify=y_bc
)

rf_bc = RandomForestClassifier(
    n_estimators=500, max_depth=None, random_state=42, n_jobs=-1
)
rf_bc.fit(X_train_bc, y_train_bc)

test_acc_bc = accuracy_score(y_test_bc, rf_bc.predict(X_test_bc))
print(f"  모델 Test Accuracy: {test_acc_bc:.4f}")

# MDI
mdi_bc = rf_bc.feature_importances_

# 순열 중요도
perm_bc = permutation_importance(
    rf_bc, X_test_bc, y_test_bc, n_repeats=30, random_state=42, n_jobs=-1
)

# 상위 10개 비교
mdi_top10_idx = np.argsort(mdi_bc)[-10:][::-1]
perm_top10_idx = np.argsort(perm_bc.importances_mean)[-10:][::-1]

print(f"\n  MDI 상위 10개 vs 순열 중요도 상위 10개:")
print(f"  {'순위':>4} | {'MDI 특성':<25} {'MDI값':>8} | {'순열 특성':<25} {'순열값':>8}")
print(f"  {'-' * 80}")
for rank in range(10):
    mdi_idx = mdi_top10_idx[rank]
    perm_idx = perm_top10_idx[rank]
    print(f"  {rank + 1:>4} | {bc_features[mdi_idx]:<25} {mdi_bc[mdi_idx]:>8.4f} | "
          f"{bc_features[perm_idx]:<25} {perm_bc.importances_mean[perm_idx]:>8.4f}")

# 시각화: 상위 15개 특성 비교
fig, axes = plt.subplots(1, 2, figsize=(16, 8))

# MDI
top15_mdi = np.argsort(mdi_bc)[-15:]
ax = axes[0]
ax.barh(range(15), mdi_bc[top15_mdi], color='steelblue', alpha=0.8)
ax.set_yticks(range(15))
ax.set_yticklabels(bc_features[top15_mdi], fontsize=9)
ax.set_xlabel('MDI (지니 중요도)', fontsize=11)
ax.set_title('MDI (Mean Decrease in Impurity)\n'
             '카디널리티 편향 가능성 있음', fontsize=12)
ax.grid(True, alpha=0.3, axis='x')

# 순열 중요도
top15_perm = np.argsort(perm_bc.importances_mean)[-15:]
ax = axes[1]
ax.barh(range(15), perm_bc.importances_mean[top15_perm],
        xerr=perm_bc.importances_std[top15_perm],
        color='coral', alpha=0.8, capsize=3)
ax.set_yticks(range(15))
ax.set_yticklabels(bc_features[top15_perm], fontsize=9)
ax.set_xlabel('순열 중요도 (Permutation Importance)', fontsize=11)
ax.set_title('순열 중요도 (Permutation Importance)\n'
             '편향이 적고 표준오차 정보 포함', fontsize=12)
ax.grid(True, alpha=0.3, axis='x')

plt.tight_layout()
plt.savefig('mdi_vs_permutation_breast_cancer.png', dpi=150, bbox_inches='tight')
plt.show()
print("  [시각화] MDI vs 순열 중요도 비교 (Breast Cancer) 저장 완료")


# ============================================================
# 5. MDI와 순열 중요도의 순위 상관 분석
# ============================================================

print(f"\n[4] MDI와 순열 중요도의 순위 상관")

from scipy.stats import spearmanr

rho, p_value = spearmanr(mdi_bc, perm_bc.importances_mean)
print(f"  Spearman 순위 상관: rho={rho:.4f}, p-value={p_value:.6f}")
print(f"  -> 두 방법의 순위가 {'유사함' if rho > 0.7 else '다소 차이 있음'}")

# 산점도
fig, ax = plt.subplots(figsize=(8, 8))
ax.scatter(mdi_bc, perm_bc.importances_mean, s=50, alpha=0.7,
           edgecolors='black', linewidths=0.5)
for i in range(len(bc_features)):
    if mdi_bc[i] > 0.03 or perm_bc.importances_mean[i] > 0.02:
        ax.annotate(bc_features[i], (mdi_bc[i], perm_bc.importances_mean[i]),
                    fontsize=7, alpha=0.8)
ax.set_xlabel('MDI (지니 중요도)', fontsize=12)
ax.set_ylabel('순열 중요도', fontsize=12)
ax.set_title(f'MDI vs 순열 중요도 산점도\n'
             f'(Spearman rho={rho:.3f})', fontsize=14)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('mdi_vs_permutation_scatter.png', dpi=150, bbox_inches='tight')
plt.show()
print("  [시각화] MDI vs 순열 중요도 산점도 저장 완료")


# ============================================================
# 6. 요약
# ============================================================

print("\n" + "=" * 70)
print("  분석 요약")
print("=" * 70)
print("""
  [핵심 결론]

  1. MDI(지니 중요도)의 편향:
     - 카디널리티가 높은 변수(연속형, 고유값 많음)를 과대평가한다.
     - 모든 변수가 무관해도, 연속형 변수가 높은 중요도를 보인다.
     - 이는 CART의 변수 선택 편향이 랜덤 포레스트에 전이되기 때문이다.

  2. 순열 중요도의 장점:
     - 카디널리티 편향이 없다.
     - 표준오차를 제공하여 중요도의 불확실성을 파악할 수 있다.
     - 모델에 구애받지 않는(model-agnostic) 방법이다.

  3. 상관 변수 존재 시:
     - 순열 중요도도 상관 변수 간에 중요도가 분산될 수 있다.
     - 이 경우 조건부 순열 중요도(Strobl et al.)가 더 정확하다.

  [실무 권장사항]
  - sklearn의 feature_importances_ (MDI)만 사용하지 말 것.
  - permutation_importance()와 함께 비교하여 해석할 것.
  - 변수 유형과 상관 구조를 고려하여 중요도를 해석할 것.
""")
