# -*- coding: utf-8 -*-
"""
02_lasso_regression.py
======================
Lasso 회귀 좌표 하강법(Coordinate Descent) 직접 구현 및 sklearn 비교

4장 선형 회귀 - 정규화 기법 2: L1 정규화 (Lasso)

핵심 알고리즘: 좌표 하강법 + 연성 임계값 연산자(Soft Thresholding)

내용:
  1. 연성 임계값 연산자 구현
  2. 좌표 하강법을 이용한 Lasso 직접 구현
  3. sklearn의 Lasso와 결과 비교
  4. 정규화 경로 시각화 (변수 선택 효과)
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import Lasso, LassoCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score

# ============================================================
# 한글 폰트 설정 (Windows)
# ============================================================
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# ============================================================
# 시드 고정
# ============================================================
np.random.seed(42)


# ============================================================
# 1. 연성 임계값 연산자 (Soft Thresholding Operator)
#    Tibshirani(1996), Friedman et al.(2010)의 핵심 연산
# ============================================================
def soft_threshold(z, gamma):
    """
    연성 임계값 연산자 (Soft Thresholding Operator)

    S(z, gamma) = sign(z) * max(|z| - gamma, 0)

    Parameters
    ----------
    z : float or ndarray
        입력값 (편미분 = X_j' * r / n, 여기서 r은 부분 잔차)
    gamma : float
        임계값 (= alpha * lambda)

    Returns
    -------
    float or ndarray
        연성 임계값이 적용된 결과

    동작 원리:
    - |z| <= gamma 이면: 0 반환 (계수 제거 -> 변수 선택)
    - z > gamma 이면: z - gamma 반환 (양수 방향 축소)
    - z < -gamma 이면: z + gamma 반환 (음수 방향 축소)
    """
    return np.sign(z) * np.maximum(np.abs(z) - gamma, 0.0)


# ============================================================
# 2. Lasso 회귀 좌표 하강법 직접 구현
# ============================================================
class LassoRegressionFromScratch:
    """
    Lasso 회귀 좌표 하강법(Coordinate Descent) 구현

    최적화 문제:
        min_w  (1/2n) * ||y - Xw||^2 + lambda * ||w||_1

    알고리즘 (Friedman, Hastie, Tibshirani, 2010):
        각 좌표 j에 대해:
            1. 부분 잔차(partial residual) 계산: r_j = y - X_{-j} * w_{-j}
            2. 연성 임계값 적용: w_j = S(X_j' * r_j / n, lambda) / (X_j' * X_j / n)
        모든 좌표에 대해 반복 -> 수렴할 때까지
    """

    def __init__(self, alpha=1.0, max_iter=1000, tol=1e-6):
        """
        Parameters
        ----------
        alpha : float
            정규화 강도 (lambda). 클수록 더 많은 계수가 0이 됨.
        max_iter : int
            최대 반복 횟수
        tol : float
            수렴 판정 기준 (계수 변화의 최대값이 이보다 작으면 수렴)
        """
        self.alpha = alpha
        self.max_iter = max_iter
        self.tol = tol
        self.coef_ = None
        self.intercept_ = None
        self.n_iter_ = 0

    def fit(self, X, y):
        """
        좌표 하강법으로 Lasso 학습

        Parameters
        ----------
        X : ndarray, shape (n_samples, n_features)
            입력 특성 행렬 (표준화 권장)
        y : ndarray, shape (n_samples,)
            타겟 벡터
        """
        n_samples, n_features = X.shape

        # 절편 처리를 위한 중심화
        self.X_mean_ = np.mean(X, axis=0)
        self.y_mean_ = np.mean(y)

        X_centered = X - self.X_mean_
        y_centered = y - self.y_mean_

        # 각 특성의 L2 노름 제곱 (사전 계산으로 효율화)
        # X_j' * X_j / n = 표준화된 특성이면 1
        col_norms_sq = np.sum(X_centered ** 2, axis=0) / n_samples

        # 계수 초기화 (0으로 시작)
        w = np.zeros(n_features)

        # 잔차 초기화
        residual = y_centered.copy()

        # 좌표 하강법 반복
        for iteration in range(self.max_iter):
            w_old = w.copy()

            # 각 좌표(변수)에 대해 업데이트
            for j in range(n_features):
                # 부분 잔차: 현재 변수 j의 기여를 더한 잔차
                # r_j = y - sum_{k != j} X_k * w_k = residual + X_j * w_j
                residual += X_centered[:, j] * w[j]

                # X_j와 부분 잔차의 내적 / n
                rho_j = X_centered[:, j].T @ residual / n_samples

                # 연성 임계값 연산자 적용
                # w_j = S(rho_j, alpha) / (X_j'X_j / n)
                if col_norms_sq[j] > 0:
                    w[j] = soft_threshold(rho_j, self.alpha) / col_norms_sq[j]
                else:
                    w[j] = 0.0

                # 잔차 업데이트: 새 w_j 반영
                residual -= X_centered[:, j] * w[j]

            # 수렴 확인: 계수 변화의 최대값
            max_change = np.max(np.abs(w - w_old))
            if max_change < self.tol:
                self.n_iter_ = iteration + 1
                break
        else:
            self.n_iter_ = self.max_iter

        self.coef_ = w
        self.intercept_ = self.y_mean_ - self.X_mean_ @ self.coef_

        return self

    def predict(self, X):
        """예측 수행"""
        return X @ self.coef_ + self.intercept_

    def score(self, X, y):
        """R^2 점수 계산"""
        y_pred = self.predict(X)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        return 1 - ss_res / ss_tot


# ============================================================
# 3. 데이터 생성 (희소 계수를 가진 모델)
# ============================================================
def generate_sparse_data(n_samples=200, n_features=20, n_informative=5,
                         noise_std=0.5):
    """
    희소한 진정한 계수를 가진 회귀 데이터 생성

    Parameters
    ----------
    n_samples : int
        표본 수
    n_features : int
        총 특성 수
    n_informative : int
        0이 아닌 계수를 가진 특성 수 (나머지는 불필요한 변수)
    noise_std : float
        노이즈 표준편차
    """
    X = np.random.randn(n_samples, n_features)

    # 진정한 계수: 처음 n_informative개만 0이 아님
    beta_true = np.zeros(n_features)
    beta_true[:n_informative] = [3.0, -2.0, 1.5, -1.0, 0.5]

    y = X @ beta_true + noise_std * np.random.randn(n_samples)

    return X, y, beta_true


print("=" * 60)
print(" Lasso 회귀 좌표 하강법 직접 구현")
print("=" * 60)

X, y, beta_true = generate_sparse_data(n_samples=200, n_features=20,
                                       n_informative=5)
print(f"\n데이터 크기: X={X.shape}, y={y.shape}")
print(f"진정한 비영 계수 수: {np.sum(beta_true != 0)}")
print(f"진정한 계수: {beta_true[:8]}... (나머지 0)")

# 특성 표준화
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)


# ============================================================
# 4. 연성 임계값 연산자 시각화
# ============================================================
print("\n" + "=" * 60)
print(" 연성 임계값 연산자 시각화")
print("=" * 60)

z_vals = np.linspace(-5, 5, 1000)
gamma_vals = [0.5, 1.0, 2.0]

fig, ax = plt.subplots(figsize=(8, 6))

# 항등 함수 (축소 없음)
ax.plot(z_vals, z_vals, 'k--', linewidth=1, alpha=0.5, label='축소 없음 (y=z)')

for gamma in gamma_vals:
    st_vals = soft_threshold(z_vals, gamma)
    ax.plot(z_vals, st_vals, linewidth=2, label=f'S(z, {gamma})')

ax.axhline(y=0, color='gray', linewidth=0.5)
ax.axvline(x=0, color='gray', linewidth=0.5)
ax.set_xlabel('z (입력)', fontsize=12)
ax.set_ylabel('S(z, gamma) (출력)', fontsize=12)
ax.set_title('연성 임계값 연산자 (Soft Thresholding)', fontsize=14)
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)
ax.set_aspect('equal')

plt.tight_layout()
plt.savefig('soft_thresholding.png', dpi=150, bbox_inches='tight')
plt.show()
print("그래프 저장: soft_thresholding.png")


# ============================================================
# 5. 직접 구현 vs sklearn 비교
# ============================================================
print("\n" + "=" * 60)
print(" 직접 구현 vs sklearn 비교")
print("=" * 60)

alpha_test = 0.1

# 직접 구현
lasso_scratch = LassoRegressionFromScratch(alpha=alpha_test, max_iter=5000,
                                           tol=1e-7)
lasso_scratch.fit(X_scaled, y)

# sklearn (동일 매개변수)
lasso_sklearn = Lasso(alpha=alpha_test, max_iter=5000, tol=1e-7)
lasso_sklearn.fit(X_scaled, y)

print(f"\n정규화 강도 (alpha/lambda): {alpha_test}")
print(f"직접 구현 반복 횟수: {lasso_scratch.n_iter_}")
print(f"sklearn 반복 횟수: {lasso_sklearn.n_iter_}")

print(f"\n{'변수':<6} {'직접 구현':>12} {'sklearn':>12} {'실제':>8} {'차이':>12}")
print("-" * 56)
for i in range(min(10, len(lasso_scratch.coef_))):
    diff = abs(lasso_scratch.coef_[i] - lasso_sklearn.coef_[i])
    print(f"  w{i:<3} {lasso_scratch.coef_[i]:>12.6f} {lasso_sklearn.coef_[i]:>12.6f} "
          f"{beta_true[i]:>8.1f} {diff:>12.2e}")

print(f"\n계수 최대 차이: {np.max(np.abs(lasso_scratch.coef_ - lasso_sklearn.coef_)):.2e}")

# 0인 계수의 수 비교
n_zero_scratch = np.sum(np.abs(lasso_scratch.coef_) < 1e-10)
n_zero_sklearn = np.sum(np.abs(lasso_sklearn.coef_) < 1e-10)
print(f"\n0인 계수 수 - 직접: {n_zero_scratch}, sklearn: {n_zero_sklearn}, "
      f"실제: {np.sum(beta_true == 0)}")


# ============================================================
# 6. 정규화 경로 (변수 선택 효과 시각화)
# ============================================================
print("\n" + "=" * 60)
print(" 정규화 경로 (Regularization Path) 계산")
print("=" * 60)

# lambda 범위 설정
# lambda_max: 모든 계수가 0이 되는 최소 lambda
lambda_max = np.max(np.abs(X_scaled.T @ (y - np.mean(y)))) / len(y)
alphas = np.logspace(np.log10(lambda_max), np.log10(lambda_max * 0.001), 100)

coefs_path = []
n_nonzero_path = []

for alpha in alphas:
    lasso = LassoRegressionFromScratch(alpha=alpha, max_iter=3000, tol=1e-6)
    lasso.fit(X_scaled, y)
    coefs_path.append(lasso.coef_.copy())
    n_nonzero_path.append(np.sum(np.abs(lasso.coef_) > 1e-10))

coefs_path = np.array(coefs_path)
n_nonzero_path = np.array(n_nonzero_path)

print(f"계산 완료: {len(alphas)}개의 lambda 값에 대한 계수 경로")

# 정규화 경로 시각화
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# 그래프 1: 계수 경로
ax1 = axes[0]
for j in range(coefs_path.shape[1]):
    if beta_true[j] != 0:
        # 중요한 변수는 실선으로
        ax1.plot(np.log10(alphas), coefs_path[:, j],
                 linewidth=2, label=f'w{j} (실제={beta_true[j]:.1f})')
    else:
        # 불필요한 변수는 점선으로
        ax1.plot(np.log10(alphas), coefs_path[:, j],
                 linewidth=0.8, linestyle='--', alpha=0.5)

ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax1.set_xlabel('log10(lambda)', fontsize=12)
ax1.set_ylabel('회귀 계수 값', fontsize=12)
ax1.set_title('Lasso 정규화 경로 (변수 선택 효과)', fontsize=14)
ax1.legend(fontsize=9, loc='upper left')
ax1.grid(True, alpha=0.3)

# 그래프 2: 선택된 변수의 수
ax2 = axes[1]
ax2.plot(np.log10(alphas), n_nonzero_path, 'b-', linewidth=2)
ax2.axhline(y=np.sum(beta_true != 0), color='red', linestyle='--',
            linewidth=2, label=f'실제 비영 계수 수 ({np.sum(beta_true != 0)})')
ax2.set_xlabel('log10(lambda)', fontsize=12)
ax2.set_ylabel('0이 아닌 계수의 수', fontsize=12)
ax2.set_title('lambda에 따른 선택된 변수 수', fontsize=14)
ax2.legend(fontsize=11)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('lasso_regularization_path.png', dpi=150, bbox_inches='tight')
plt.show()
print("그래프 저장: lasso_regularization_path.png")


# ============================================================
# 7. 교차 검증을 통한 최적 lambda 선택
# ============================================================
print("\n" + "=" * 60)
print(" 교차 검증을 통한 최적 lambda 선택")
print("=" * 60)

# sklearn의 LassoCV 사용
lasso_cv = LassoCV(alphas=alphas, cv=5, max_iter=5000)
lasso_cv.fit(X_scaled, y)

print(f"최적 lambda: {lasso_cv.alpha_:.6f}")
print(f"선택된 변수 수: {np.sum(np.abs(lasso_cv.coef_) > 1e-10)}")
print(f"실제 비영 계수 수: {np.sum(beta_true != 0)}")

# 교차 검증 곡선 시각화
fig, ax = plt.subplots(figsize=(10, 6))

# LassoCV의 mse_path_: shape (n_alphas, n_folds)
mse_mean = np.mean(lasso_cv.mse_path_, axis=1)
mse_std = np.std(lasso_cv.mse_path_, axis=1)

ax.plot(np.log10(lasso_cv.alphas_), mse_mean, 'b-', linewidth=2,
        label='평균 CV MSE')
ax.fill_between(np.log10(lasso_cv.alphas_),
                mse_mean - mse_std, mse_mean + mse_std,
                alpha=0.2, color='blue')
ax.axvline(x=np.log10(lasso_cv.alpha_), color='red', linestyle='--',
           linewidth=2, label=f'최적 lambda={lasso_cv.alpha_:.6f}')
ax.set_xlabel('log10(lambda)', fontsize=12)
ax.set_ylabel('교차 검증 MSE', fontsize=12)
ax.set_title('Lasso 교차 검증 곡선', fontsize=14)
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('lasso_cross_validation.png', dpi=150, bbox_inches='tight')
plt.show()
print("그래프 저장: lasso_cross_validation.png")


# ============================================================
# 8. 최종 결과 요약
# ============================================================
print("\n" + "=" * 60)
print(" 최종 결과 요약 (최적 lambda에서의 Lasso)")
print("=" * 60)

y_pred = lasso_cv.predict(X_scaled)
mse = mean_squared_error(y, y_pred)
r2 = r2_score(y, y_pred)

print(f"\nMSE: {mse:.4f}")
print(f"R^2: {r2:.4f}")

print(f"\n{'변수':<6} {'추정 계수':>12} {'실제 계수':>12} {'선택?':>6}")
print("-" * 40)
for i in range(len(lasso_cv.coef_)):
    selected = "O" if abs(lasso_cv.coef_[i]) > 1e-10 else "X"
    print(f"  w{i:<3} {lasso_cv.coef_[i]:>12.4f} {beta_true[i]:>12.4f}    {selected}")

# 올바른 변수 선택 확인
selected_vars = set(np.where(np.abs(lasso_cv.coef_) > 1e-10)[0])
true_vars = set(np.where(beta_true != 0)[0])

print(f"\n실제 중요 변수: {sorted(true_vars)}")
print(f"Lasso가 선택한 변수: {sorted(selected_vars)}")
print(f"정확히 선택된 변수: {sorted(selected_vars & true_vars)}")
print(f"잘못 선택된 변수 (거짓 양성): {sorted(selected_vars - true_vars)}")
print(f"놓친 변수 (거짓 음성): {sorted(true_vars - selected_vars)}")

print("\n" + "=" * 60)
print(" 완료!")
print("=" * 60)
