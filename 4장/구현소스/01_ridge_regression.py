# -*- coding: utf-8 -*-
"""
01_ridge_regression.py
======================
릿지 회귀(Ridge Regression) 직접 구현 및 sklearn 비교

4장 선형 회귀 - 정규화 기법 1: L2 정규화 (릿지 회귀)

핵심 수식: w = (X'X + λI)^(-1) X'y

내용:
  1. 릿지 회귀 닫힌 형태(closed-form) 해 직접 구현
  2. sklearn의 Ridge와 결과 비교
  3. 정규화 경로(regularization path) 시각화
  4. 교차 검증을 통한 최적 lambda 선택
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import Ridge, RidgeCV
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
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
# 1. 데이터 생성
#    - 다중공선성(multicollinearity)이 있는 데이터를 생성하여
#      릿지 회귀의 효과를 명확히 보여줌
# ============================================================
def generate_data(n_samples=200, n_features=10, noise_std=1.0):
    """다중공선성이 있는 회귀 데이터 생성"""
    # 기본 독립 특성 5개 생성
    X_base = np.random.randn(n_samples, 5)

    # 나머지 5개 특성은 기존 특성의 선형 결합 + 약간의 노이즈 (다중공선성 유도)
    X_corr = np.column_stack([
        X_base[:, 0] + 0.1 * np.random.randn(n_samples),   # x0과 높은 상관
        X_base[:, 1] + 0.1 * np.random.randn(n_samples),   # x1과 높은 상관
        X_base[:, 2] + 0.15 * np.random.randn(n_samples),  # x2와 높은 상관
        X_base[:, 0] + X_base[:, 1] + 0.2 * np.random.randn(n_samples),  # x0+x1
        0.5 * X_base[:, 3] + 0.5 * X_base[:, 4] + 0.1 * np.random.randn(n_samples)
    ])

    X = np.column_stack([X_base, X_corr])

    # 진정한 계수 (일부는 0)
    beta_true = np.array([3.0, -2.0, 1.5, 0.0, 0.5,
                          0.0, 0.0, 0.0, 0.0, 0.0])

    # 반응 변수 생성
    y = X @ beta_true + noise_std * np.random.randn(n_samples)

    return X, y, beta_true


print("=" * 60)
print(" 릿지 회귀(Ridge Regression) 직접 구현")
print("=" * 60)

X, y, beta_true = generate_data(n_samples=200, n_features=10)
print(f"\n데이터 크기: X={X.shape}, y={y.shape}")
print(f"진정한 계수: {beta_true}")

# 특성 표준화 (릿지 회귀에서 중요)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)


# ============================================================
# 2. 릿지 회귀 직접 구현 (closed-form solution)
# ============================================================
class RidgeRegressionFromScratch:
    """
    릿지 회귀 직접 구현

    최적화 문제:
        min_w ||y - Xw||^2 + lambda * ||w||^2

    닫힌 형태 해:
        w = (X'X + lambda * I)^(-1) X'y
    """

    def __init__(self, alpha=1.0):
        """
        Parameters
        ----------
        alpha : float
            정규화 강도 (lambda). 클수록 계수가 더 많이 축소됨.
        """
        self.alpha = alpha
        self.coef_ = None
        self.intercept_ = None

    def fit(self, X, y):
        """
        릿지 회귀 학습

        Parameters
        ----------
        X : ndarray, shape (n_samples, n_features)
            입력 특성 행렬
        y : ndarray, shape (n_samples,)
            타겟 벡터
        """
        n_samples, n_features = X.shape

        # 절편 처리: X에 1 벡터 추가하지 않고, y를 중심화(centering)하여 처리
        # (sklearn과 동일한 방식)
        self.X_mean_ = np.mean(X, axis=0)
        self.y_mean_ = np.mean(y)

        # 중심화
        X_centered = X - self.X_mean_
        y_centered = y - self.y_mean_

        # 닫힌 형태 해: w = (X'X + alpha * I)^(-1) X'y
        # X'X 계산
        XtX = X_centered.T @ X_centered

        # 정규화 항 추가: X'X + alpha * I
        identity = np.eye(n_features)
        regularized = XtX + self.alpha * identity

        # X'y 계산
        Xty = X_centered.T @ y_centered

        # 선형 시스템 풀기 (역행렬보다 수치적으로 안정적)
        self.coef_ = np.linalg.solve(regularized, Xty)

        # 절편 계산
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
# 3. 직접 구현 vs sklearn 비교
# ============================================================
print("\n" + "=" * 60)
print(" 직접 구현 vs sklearn 비교")
print("=" * 60)

alpha_test = 1.0

# 직접 구현
ridge_scratch = RidgeRegressionFromScratch(alpha=alpha_test)
ridge_scratch.fit(X_scaled, y)

# sklearn
ridge_sklearn = Ridge(alpha=alpha_test)
ridge_sklearn.fit(X_scaled, y)

print(f"\n정규화 강도 (alpha/lambda): {alpha_test}")
print(f"\n{'변수':<6} {'직접 구현':>12} {'sklearn':>12} {'차이':>12}")
print("-" * 48)
for i in range(len(ridge_scratch.coef_)):
    diff = abs(ridge_scratch.coef_[i] - ridge_sklearn.coef_[i])
    print(f"  w{i:<3} {ridge_scratch.coef_[i]:>12.6f} {ridge_sklearn.coef_[i]:>12.6f} {diff:>12.2e}")

print(f"\n절편: 직접={ridge_scratch.intercept_:.6f}, sklearn={ridge_sklearn.intercept_:.6f}")
print(f"계수 최대 차이: {np.max(np.abs(ridge_scratch.coef_ - ridge_sklearn.coef_)):.2e}")


# ============================================================
# 4. 정규화 경로 (Regularization Path) 시각화
#    - lambda 값에 따른 계수 변화를 보여줌
#    - Hoerl & Kennard(1970)의 "릿지 트레이스(Ridge Trace)"
# ============================================================
print("\n" + "=" * 60)
print(" 정규화 경로 (Regularization Path) 계산")
print("=" * 60)

# lambda 값의 범위 설정 (로그 스케일)
alphas = np.logspace(-2, 4, 200)
coefs_path = []

for alpha in alphas:
    ridge = RidgeRegressionFromScratch(alpha=alpha)
    ridge.fit(X_scaled, y)
    coefs_path.append(ridge.coef_.copy())

coefs_path = np.array(coefs_path)  # shape: (n_alphas, n_features)

print(f"계산 완료: {len(alphas)}개의 lambda 값에 대한 계수 경로")

# 정규화 경로 시각화
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# 그래프 1: 정규화 경로 (x축: log(lambda))
ax1 = axes[0]
for j in range(coefs_path.shape[1]):
    label = f'w{j} (실제={beta_true[j]:.1f})'
    ax1.plot(np.log10(alphas), coefs_path[:, j], label=label, linewidth=1.5)

ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax1.set_xlabel('log10(lambda)', fontsize=12)
ax1.set_ylabel('회귀 계수 값', fontsize=12)
ax1.set_title('릿지 회귀 정규화 경로 (Ridge Trace)', fontsize=14)
ax1.legend(fontsize=8, loc='upper right', ncol=2)
ax1.grid(True, alpha=0.3)

# 그래프 2: 계수의 L2 노름 vs lambda
l2_norms = np.sqrt(np.sum(coefs_path ** 2, axis=1))
ax2 = axes[1]
ax2.plot(np.log10(alphas), l2_norms, 'b-', linewidth=2)
ax2.set_xlabel('log10(lambda)', fontsize=12)
ax2.set_ylabel('||w||_2 (계수의 L2 노름)', fontsize=12)
ax2.set_title('정규화 강도에 따른 계수 크기 변화', fontsize=14)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('ridge_regularization_path.png', dpi=150, bbox_inches='tight')
plt.show()
print("그래프 저장: ridge_regularization_path.png")


# ============================================================
# 5. 교차 검증을 통한 최적 lambda 선택
# ============================================================
print("\n" + "=" * 60)
print(" 교차 검증을 통한 최적 lambda 선택")
print("=" * 60)

# 교차 검증 대상 lambda 값들
alpha_candidates = np.logspace(-2, 4, 100)

# 방법 1: 직접 교차 검증 구현
cv_scores_mean = []
cv_scores_std = []

for alpha in alpha_candidates:
    ridge = Ridge(alpha=alpha)
    # 5-fold 교차 검증, 음의 MSE를 사용 (sklearn 관례)
    scores = cross_val_score(ridge, X_scaled, y, cv=5,
                             scoring='neg_mean_squared_error')
    cv_scores_mean.append(-scores.mean())  # 양수로 변환
    cv_scores_std.append(scores.std())

cv_scores_mean = np.array(cv_scores_mean)
cv_scores_std = np.array(cv_scores_std)

# 최적 lambda
best_idx = np.argmin(cv_scores_mean)
best_alpha_manual = alpha_candidates[best_idx]
best_mse = cv_scores_mean[best_idx]

print(f"최적 lambda (직접 CV): {best_alpha_manual:.4f}")
print(f"최소 CV MSE: {best_mse:.4f}")

# 방법 2: sklearn의 RidgeCV 사용
ridge_cv = RidgeCV(alphas=alpha_candidates, cv=5,
                   scoring='neg_mean_squared_error')
ridge_cv.fit(X_scaled, y)

print(f"최적 lambda (RidgeCV): {ridge_cv.alpha_:.4f}")

# 교차 검증 곡선 시각화
fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(np.log10(alpha_candidates), cv_scores_mean, 'b-', linewidth=2,
        label='평균 CV MSE')
ax.fill_between(np.log10(alpha_candidates),
                cv_scores_mean - cv_scores_std,
                cv_scores_mean + cv_scores_std,
                alpha=0.2, color='blue', label='+-1 표준편차')
ax.axvline(x=np.log10(best_alpha_manual), color='red', linestyle='--',
           linewidth=2, label=f'최적 lambda={best_alpha_manual:.4f}')
ax.set_xlabel('log10(lambda)', fontsize=12)
ax.set_ylabel('교차 검증 MSE', fontsize=12)
ax.set_title('릿지 회귀 교차 검증 곡선', fontsize=14)
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('ridge_cross_validation.png', dpi=150, bbox_inches='tight')
plt.show()
print("그래프 저장: ridge_cross_validation.png")


# ============================================================
# 6. 최적 lambda에서의 최종 모델 평가
# ============================================================
print("\n" + "=" * 60)
print(" 최적 lambda에서의 최종 모델")
print("=" * 60)

# 최적 lambda로 모델 학습
ridge_final = RidgeRegressionFromScratch(alpha=best_alpha_manual)
ridge_final.fit(X_scaled, y)

y_pred = ridge_final.predict(X_scaled)
mse = mean_squared_error(y, y_pred)
r2 = r2_score(y, y_pred)

print(f"\n최적 lambda: {best_alpha_manual:.4f}")
print(f"MSE: {mse:.4f}")
print(f"R^2: {r2:.4f}")
print(f"\n{'변수':<6} {'추정 계수':>12} {'실제 계수':>12}")
print("-" * 36)
for i in range(len(ridge_final.coef_)):
    print(f"  w{i:<3} {ridge_final.coef_[i]:>12.4f} {beta_true[i]:>12.4f}")

# ============================================================
# 7. OLS vs 릿지 회귀 비교 (다중공선성 효과)
# ============================================================
print("\n" + "=" * 60)
print(" OLS vs 릿지 회귀 비교 (다중공선성 효과)")
print("=" * 60)

# OLS (lambda = 0)
from numpy.linalg import lstsq
X_centered = X_scaled - np.mean(X_scaled, axis=0)
y_centered = y - np.mean(y)
coef_ols, _, _, _ = lstsq(X_centered, y_centered, rcond=None)

# X'X의 조건수(condition number) 확인
XtX = X_centered.T @ X_centered
cond_number = np.linalg.cond(XtX)
print(f"\nX'X의 조건수: {cond_number:.2f}")
print("  (조건수가 크면 다중공선성이 심함 -> OLS가 불안정)")

# X'X + lambda*I의 조건수
regularized = XtX + best_alpha_manual * np.eye(X_scaled.shape[1])
cond_regularized = np.linalg.cond(regularized)
print(f"(X'X + lambda*I)의 조건수: {cond_regularized:.2f}")
print(f"  -> 릿지 정규화로 조건수가 {cond_number/cond_regularized:.1f}배 감소")

print(f"\n{'변수':<6} {'OLS':>12} {'릿지':>12} {'실제':>12}")
print("-" * 48)
for i in range(len(coef_ols)):
    print(f"  w{i:<3} {coef_ols[i]:>12.4f} {ridge_final.coef_[i]:>12.4f} {beta_true[i]:>12.4f}")

print(f"\nOLS 계수의 L2 노름: {np.linalg.norm(coef_ols):.4f}")
print(f"릿지 계수의 L2 노름: {np.linalg.norm(ridge_final.coef_):.4f}")
print(f"  -> 릿지 회귀가 계수를 축소하여 더 안정적인 추정 제공")

print("\n" + "=" * 60)
print(" 완료!")
print("=" * 60)
