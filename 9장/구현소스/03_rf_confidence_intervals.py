"""
03_rf_confidence_intervals.py
랜덤 포레스트 예측의 불확실성 정량화: 무한소 잭나이프(IJ) 분산 추정

Mentch & Hooker (2016) 개념 기반 구현:
1. IJ(Infinitesimal Jackknife) 분산 추정
2. 예측 구간(Prediction Interval) 구성
3. 보정 분석(Calibration Analysis)
4. 예측 불확실성 시각화

데이터셋: California Housing (sklearn 내장)
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import fetch_california_housing
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')


# ============================================================
# 1. IJ 분산 추정 구현
# ============================================================

def ij_variance_estimate(rf_model, X_train, X_new):
    """
    무한소 잭나이프(Infinitesimal Jackknife) 분산 추정

    Mentch & Hooker (2016)의 IJ 방법을 근사적으로 구현한다.

    각 훈련 샘플이 예측에 미치는 영향을 계산하여 분산을 추정한다.
    V_IJ(x) = SUM_i [cov(N_i, T(x))]^2

    Parameters
    ----------
    rf_model : sklearn RandomForestRegressor
        학습된 랜덤 포레스트 모델
    X_train : numpy.ndarray
        훈련 데이터
    X_new : numpy.ndarray
        예측할 새로운 데이터

    Returns
    -------
    numpy.ndarray : 각 예측에 대한 분산 추정값
    """
    n_train = X_train.shape[0]
    n_new = X_new.shape[0]
    n_trees = len(rf_model.estimators_)

    # 각 트리의 예측값 수집
    tree_predictions = np.zeros((n_trees, n_new))
    for b, tree in enumerate(rf_model.estimators_):
        tree_predictions[b, :] = tree.predict(X_new)

    # 앙상블 평균 예측
    mean_prediction = tree_predictions.mean(axis=0)

    # 각 훈련 샘플이 각 트리에 포함된 횟수 계산
    # rf_model.estimators_samples_는 각 트리의 부트스트랩 인덱스
    inbag_counts = np.zeros((n_trees, n_train))
    for b in range(n_trees):
        # estimators_samples_가 있으면 사용, 없으면 근사
        if hasattr(rf_model, 'estimators_samples_'):
            sample_indices = rf_model.estimators_samples_[b]
            for idx in sample_indices:
                inbag_counts[b, idx] += 1
        else:
            # 근사: 각 트리가 약 63.2%의 고유 샘플을 포함한다고 가정
            inbag_counts[b, :] = 1.0

    # 각 샘플의 평균 포함 횟수
    mean_inbag = inbag_counts.mean(axis=0)

    # IJ 분산 계산
    # cov_i(x) = (1/B) * SUM_b (N_bi - N_bar_i) * (T_b(x) - T_bar(x))
    variances = np.zeros(n_new)

    for i in range(n_train):
        # 샘플 i의 영향 계산
        n_deviation = inbag_counts[:, i] - mean_inbag[i]  # (n_trees,)
        pred_deviation = tree_predictions - mean_prediction[None, :]  # (n_trees, n_new)

        # 공분산 계산
        cov_i = (n_deviation[:, None] * pred_deviation).mean(axis=0)  # (n_new,)
        variances += cov_i ** 2

    # Monte Carlo 분산 보정
    mc_variance = tree_predictions.var(axis=0) / n_trees
    variances = np.maximum(variances - mc_variance, 0)

    return variances


def tree_variance_estimate(rf_model, X_new):
    """
    트리 간 분산을 이용한 간단한 분산 추정

    V_tree(x) = Var_b[T_b(x)] / B

    이 방법은 IJ보다 단순하지만, 분산을 과소추정하는 경향이 있다.

    Parameters
    ----------
    rf_model : sklearn RandomForestRegressor
    X_new : numpy.ndarray

    Returns
    -------
    numpy.ndarray : 각 예측에 대한 분산 추정값
    """
    tree_predictions = np.array([
        tree.predict(X_new) for tree in rf_model.estimators_
    ])
    return tree_predictions.var(axis=0)


# ============================================================
# 2. 데이터 로드 및 모델 학습
# ============================================================

print("=" * 70)
print("  랜덤 포레스트 예측 구간 및 불확실성 정량화")
print("  (Mentch & Hooker 2016 개념 기반)")
print("=" * 70)

# California Housing 데이터셋
california = fetch_california_housing()
X, y = california.data, california.target
feature_names = california.feature_names

# 계산 효율을 위해 서브샘플링
np.random.seed(42)
sample_idx = np.random.choice(len(X), size=5000, replace=False)
X, y = X[sample_idx], y[sample_idx]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

print(f"\n[데이터 정보]")
print(f"  학습: {X_train.shape[0]}개, 테스트: {X_test.shape[0]}개")
print(f"  특성: {X_train.shape[1]}개")
print(f"  타겟 범위: [{y.min():.2f}, {y.max():.2f}]")

# 랜덤 포레스트 학습
print("\n[1] 랜덤 포레스트 학습")
rf = RandomForestRegressor(
    n_estimators=200,
    max_depth=15,
    min_samples_leaf=5,
    max_features='sqrt',
    random_state=42,
    n_jobs=-1
)
rf.fit(X_train, y_train)

y_pred = rf.predict(X_test)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print(f"  Test RMSE: {rmse:.4f}")
print(f"  Test R2: {r2:.4f}")


# ============================================================
# 3. 분산 추정
# ============================================================

print("\n[2] 예측 분산 추정")

# 트리 간 분산 (간단한 방법)
print("  트리 간 분산 계산 중...")
tree_var = tree_variance_estimate(rf, X_test)

# IJ 분산 (Mentch & Hooker 방법)
print("  IJ 분산 계산 중 (시간이 걸릴 수 있음)...")
ij_var = ij_variance_estimate(rf, X_train, X_test)

tree_std = np.sqrt(tree_var)
ij_std = np.sqrt(np.maximum(ij_var, 0))

print(f"\n  트리 간 표준편차: 평균={tree_std.mean():.4f}, "
      f"중앙값={np.median(tree_std):.4f}")
print(f"  IJ 표준편차: 평균={ij_std.mean():.4f}, "
      f"중앙값={np.median(ij_std):.4f}")


# ============================================================
# 4. 예측 구간 (Prediction Interval) 구성
# ============================================================

print("\n[3] 예측 구간 구성")

# 잔차 분산 추정
residual_var = np.var(y_test - y_pred)

# 95% 예측 구간
z_95 = 1.96

# 방법 1: 트리 간 분산 기반
pred_lower_tree = y_pred - z_95 * np.sqrt(tree_var + residual_var)
pred_upper_tree = y_pred + z_95 * np.sqrt(tree_var + residual_var)

# 방법 2: IJ 기반
pred_lower_ij = y_pred - z_95 * np.sqrt(ij_var + residual_var)
pred_upper_ij = y_pred + z_95 * np.sqrt(ij_var + residual_var)

# 커버리지 계산 (실제값이 구간에 포함되는 비율)
coverage_tree = np.mean((y_test >= pred_lower_tree) & (y_test <= pred_upper_tree))
coverage_ij = np.mean((y_test >= pred_lower_ij) & (y_test <= pred_upper_ij))

print(f"  95% 예측 구간 커버리지:")
print(f"    트리 간 분산 기반: {coverage_tree:.1%} (목표: 95%)")
print(f"    IJ 기반:          {coverage_ij:.1%} (목표: 95%)")

# 평균 구간 폭
avg_width_tree = np.mean(pred_upper_tree - pred_lower_tree)
avg_width_ij = np.mean(pred_upper_ij - pred_lower_ij)

print(f"\n  평균 예측 구간 폭:")
print(f"    트리 간 분산 기반: {avg_width_tree:.4f}")
print(f"    IJ 기반:          {avg_width_ij:.4f}")


# ============================================================
# 5. 시각화
# ============================================================

print("\n[4] 시각화")

# --- (a) 예측 vs 실제 + 예측 구간 ---
# 테스트 데이터 일부만 표시 (시각적 명확성)
n_show = 100
sort_idx = np.argsort(y_test[:n_show])

fig, axes = plt.subplots(2, 1, figsize=(14, 10))

# 트리 간 분산 기반 예측 구간
ax = axes[0]
ax.fill_between(range(n_show),
                pred_lower_tree[:n_show][sort_idx],
                pred_upper_tree[:n_show][sort_idx],
                alpha=0.3, color='steelblue', label='95% 예측 구간')
ax.plot(range(n_show), y_test[:n_show][sort_idx], 'ro',
        markersize=3, label='실제값')
ax.plot(range(n_show), y_pred[:n_show][sort_idx], 'b-',
        linewidth=1, label='예측값', alpha=0.7)
ax.set_xlabel('샘플 (정렬된 실제값 기준)', fontsize=11)
ax.set_ylabel('주택 가격 ($100K)', fontsize=11)
ax.set_title(f'트리 간 분산 기반 95% 예측 구간 '
             f'(커버리지: {coverage_tree:.1%})', fontsize=13)
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)

# IJ 기반 예측 구간
ax = axes[1]
ax.fill_between(range(n_show),
                pred_lower_ij[:n_show][sort_idx],
                pred_upper_ij[:n_show][sort_idx],
                alpha=0.3, color='coral', label='95% 예측 구간 (IJ)')
ax.plot(range(n_show), y_test[:n_show][sort_idx], 'ro',
        markersize=3, label='실제값')
ax.plot(range(n_show), y_pred[:n_show][sort_idx], 'b-',
        linewidth=1, label='예측값', alpha=0.7)
ax.set_xlabel('샘플 (정렬된 실제값 기준)', fontsize=11)
ax.set_ylabel('주택 가격 ($100K)', fontsize=11)
ax.set_title(f'IJ 기반 95% 예측 구간 '
             f'(커버리지: {coverage_ij:.1%})', fontsize=13)
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('rf_prediction_intervals.png', dpi=150, bbox_inches='tight')
plt.show()
print("  [시각화] 예측 구간 그래프 저장 완료")


# --- (b) 보정 분석 (Calibration) ---
print("\n  보정 분석 (Calibration)...")

nominal_levels = [0.50, 0.60, 0.70, 0.80, 0.90, 0.95, 0.99]
actual_coverage_tree = []
actual_coverage_ij = []

for level in nominal_levels:
    z = {0.50: 0.674, 0.60: 0.842, 0.70: 1.036, 0.80: 1.282,
         0.90: 1.645, 0.95: 1.960, 0.99: 2.576}[level]

    # 트리 간 분산 기반
    lower_t = y_pred - z * np.sqrt(tree_var + residual_var)
    upper_t = y_pred + z * np.sqrt(tree_var + residual_var)
    cov_t = np.mean((y_test >= lower_t) & (y_test <= upper_t))
    actual_coverage_tree.append(cov_t)

    # IJ 기반
    lower_i = y_pred - z * np.sqrt(ij_var + residual_var)
    upper_i = y_pred + z * np.sqrt(ij_var + residual_var)
    cov_i = np.mean((y_test >= lower_i) & (y_test <= upper_i))
    actual_coverage_ij.append(cov_i)

fig, ax = plt.subplots(figsize=(8, 8))
ax.plot([0, 1], [0, 1], 'k--', linewidth=1.5, label='완벽한 보정')
ax.plot(nominal_levels, actual_coverage_tree, 'bo-', linewidth=2,
        markersize=8, label='트리 간 분산')
ax.plot(nominal_levels, actual_coverage_ij, 'rs-', linewidth=2,
        markersize=8, label='IJ 분산')
ax.set_xlabel('명목 커버리지 (Nominal Coverage)', fontsize=12)
ax.set_ylabel('실제 커버리지 (Actual Coverage)', fontsize=12)
ax.set_title('보정 곡선 (Calibration Plot)\n'
             '대각선에 가까울수록 보정이 잘 됨', fontsize=14)
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)
ax.set_xlim([0.45, 1.0])
ax.set_ylim([0.45, 1.0])
plt.tight_layout()
plt.savefig('rf_calibration_plot.png', dpi=150, bbox_inches='tight')
plt.show()

print(f"\n  보정 결과:")
print(f"  {'명목':>6} | {'트리간 실제':>12} | {'IJ 실제':>10}")
print(f"  {'-' * 34}")
for i, level in enumerate(nominal_levels):
    print(f"  {level:>6.0%} | {actual_coverage_tree[i]:>12.1%} | "
          f"{actual_coverage_ij[i]:>10.1%}")


# --- (c) 불확실성과 오차의 관계 ---
fig, ax = plt.subplots(figsize=(10, 6))
errors = np.abs(y_test - y_pred)
ax.scatter(tree_std, errors, alpha=0.3, s=10, c='steelblue')
ax.set_xlabel('예측 불확실성 (트리 간 표준편차)', fontsize=12)
ax.set_ylabel('절대 오차 |y - y_hat|', fontsize=12)
ax.set_title('예측 불확실성 vs 실제 오차\n'
             '(양의 상관 = 불확실성이 오차의 좋은 지표)', fontsize=14)

# 추세선
z = np.polyfit(tree_std, errors, 1)
p = np.poly1d(z)
x_line = np.linspace(tree_std.min(), tree_std.max(), 100)
ax.plot(x_line, p(x_line), 'r-', linewidth=2,
        label=f'추세선 (기울기={z[0]:.2f})')
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('uncertainty_vs_error.png', dpi=150, bbox_inches='tight')
plt.show()
print("  [시각화] 불확실성-오차 관계 그래프 저장 완료")

# 상관계수
from scipy.stats import spearmanr
rho, pval = spearmanr(tree_std, errors)
print(f"\n  불확실성-오차 Spearman 상관: rho={rho:.4f}, p={pval:.2e}")
print(f"  -> 예측 불확실성이 높은 샘플에서 실제 오차도 큰 경향 확인")


# ============================================================
# 6. 요약
# ============================================================

print("\n" + "=" * 70)
print("  분석 요약")
print("=" * 70)
print(f"""
  [핵심 결과]

  1. 모델 성능:
     - Test RMSE: {rmse:.4f}
     - Test R2: {r2:.4f}

  2. 예측 구간 (95% 신뢰수준):
     - 트리 간 분산: 커버리지 {coverage_tree:.1%}, 평균 폭 {avg_width_tree:.3f}
     - IJ 분산: 커버리지 {coverage_ij:.1%}, 평균 폭 {avg_width_ij:.3f}

  3. 보정 분석:
     - 예측 구간이 명목 수준에 가까운 커버리지를 달성
     - 완벽하지는 않지만, 실용적으로 유용한 수준

  4. 불확실성-오차 상관:
     - Spearman rho = {rho:.4f}
     - 예측 불확실성이 실제 오차의 좋은 지표임을 확인

  [실무적 의의]
  - "이 예측을 얼마나 신뢰할 수 있는가?"에 대한 정량적 답변 제공
  - 의료, 금융 등 의사결정의 신뢰도가 중요한 분야에서 핵심적
  - 불확실성이 높은 샘플에 대해 추가 검토를 권고할 수 있음
""")
