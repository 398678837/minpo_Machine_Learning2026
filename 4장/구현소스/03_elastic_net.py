# -*- coding: utf-8 -*-
"""
03_elastic_net.py
=================
엘라스틱 넷(Elastic Net) 구현 및 Ridge/Lasso/Elastic Net 종합 비교

4장 선형 회귀 - 정규화 기법 3: L1 + L2 혼합 정규화

핵심 수식:
    min_w (1/2n)||y - Xw||^2 + lambda * [alpha * ||w||_1 + (1-alpha)/2 * ||w||^2]

내용:
  1. Elastic Net 좌표 하강법 직접 구현
  2. 상관된 특성에서 Ridge vs Lasso vs Elastic Net 비교
  3. 세 방법의 정규화 경로(coefficient path) 종합 시각화
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.linear_model import RidgeCV, LassoCV, ElasticNetCV
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
# 1. 연성 임계값 연산자
# ============================================================
def soft_threshold(z, gamma):
    """연성 임계값 연산자: S(z, gamma) = sign(z) * max(|z| - gamma, 0)"""
    return np.sign(z) * np.maximum(np.abs(z) - gamma, 0.0)


# ============================================================
# 2. Elastic Net 좌표 하강법 직접 구현
# ============================================================
class ElasticNetFromScratch:
    """
    Elastic Net 좌표 하강법 구현 (Zou & Hastie, 2005; Friedman et al., 2010)

    최적화 문제:
        min_w (1/2n)||y - Xw||^2 + lambda * [alpha * ||w||_1 + (1-alpha)/2 * ||w||^2]

    좌표 하강 업데이트 규칙:
        w_j = S(rho_j, alpha * lambda) / (X_j'X_j/n + lambda * (1 - alpha))

    여기서:
        rho_j = X_j' * r_j / n  (r_j는 j번째 변수를 제외한 부분 잔차)
        S()는 연성 임계값 연산자

    특수 경우:
        alpha = 1: 순수 Lasso (L1만)
        alpha = 0: 순수 Ridge (L2만)
        0 < alpha < 1: Elastic Net
    """

    def __init__(self, alpha=1.0, l1_ratio=0.5, max_iter=1000, tol=1e-6):
        """
        Parameters
        ----------
        alpha : float
            전체 정규화 강도 (lambda)
        l1_ratio : float, 0~1
            L1 패널티의 비율 (sklearn 관례에서 alpha에 해당)
            l1_ratio=1 -> 순수 Lasso
            l1_ratio=0 -> 순수 Ridge
        max_iter : int
            최대 반복 횟수
        tol : float
            수렴 판정 기준
        """
        self.alpha = alpha
        self.l1_ratio = l1_ratio
        self.max_iter = max_iter
        self.tol = tol
        self.coef_ = None
        self.intercept_ = None
        self.n_iter_ = 0

    def fit(self, X, y):
        """좌표 하강법으로 Elastic Net 학습"""
        n_samples, n_features = X.shape

        # 중심화
        self.X_mean_ = np.mean(X, axis=0)
        self.y_mean_ = np.mean(y)
        X_c = X - self.X_mean_
        y_c = y - self.y_mean_

        # L1, L2 강도 분리
        l1_penalty = self.alpha * self.l1_ratio        # alpha * alpha_ratio
        l2_penalty = self.alpha * (1 - self.l1_ratio)  # alpha * (1 - alpha_ratio)

        # 각 특성의 L2 노름 제곱 / n (사전 계산)
        col_norms_sq = np.sum(X_c ** 2, axis=0) / n_samples

        # 계수 초기화
        w = np.zeros(n_features)
        residual = y_c.copy()

        # 좌표 하강법 반복
        for iteration in range(self.max_iter):
            w_old = w.copy()

            for j in range(n_features):
                # 부분 잔차에 현재 변수 기여 복원
                residual += X_c[:, j] * w[j]

                # rho_j = X_j' * r_j / n
                rho_j = X_c[:, j].T @ residual / n_samples

                # Elastic Net 업데이트:
                # w_j = S(rho_j, l1_penalty) / (X_j'X_j/n + l2_penalty)
                denominator = col_norms_sq[j] + l2_penalty
                if denominator > 0:
                    w[j] = soft_threshold(rho_j, l1_penalty) / denominator
                else:
                    w[j] = 0.0

                # 잔차 업데이트
                residual -= X_c[:, j] * w[j]

            # 수렴 확인
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
# 3. 상관된 특성을 가진 데이터 생성
#    - Elastic Net의 그룹화 효과(Grouping Effect)를 보여주기 위함
#    - Zou & Hastie (2005)의 시뮬레이션과 유사
# ============================================================
def generate_correlated_data(n_samples=200, noise_std=1.0):
    """
    상관된 특성 그룹이 있는 희소 회귀 데이터 생성

    구조:
    - 그룹 1 (x0, x1, x2): 높은 상관관계, 모두 y에 영향
    - 그룹 2 (x3, x4): 높은 상관관계, 모두 y에 영향
    - 독립 변수 (x5~x14): y에 영향 없는 노이즈 변수
    """
    # 잠재 변수(latent variable) 생성
    z1 = np.random.randn(n_samples)  # 그룹 1의 공통 요인
    z2 = np.random.randn(n_samples)  # 그룹 2의 공통 요인

    # 그룹 1: z1 기반 + 약간의 독립적 노이즈
    x0 = z1 + 0.1 * np.random.randn(n_samples)
    x1 = z1 + 0.1 * np.random.randn(n_samples)
    x2 = z1 + 0.15 * np.random.randn(n_samples)

    # 그룹 2: z2 기반 + 약간의 독립적 노이즈
    x3 = z2 + 0.1 * np.random.randn(n_samples)
    x4 = z2 + 0.1 * np.random.randn(n_samples)

    # 독립적 노이즈 변수 (불필요)
    X_noise = np.random.randn(n_samples, 10)

    X = np.column_stack([x0, x1, x2, x3, x4, X_noise])

    # 진정한 계수: 그룹 1과 그룹 2의 변수만 효과가 있음
    beta_true = np.zeros(15)
    beta_true[0:3] = [2.0, 2.0, 2.0]  # 그룹 1 (상관된 변수들이 모두 중요)
    beta_true[3:5] = [-1.5, -1.5]      # 그룹 2 (상관된 변수들이 모두 중요)

    y = X @ beta_true + noise_std * np.random.randn(n_samples)

    feature_names = [f'x{i}' for i in range(15)]
    group_labels = (['그룹1'] * 3 + ['그룹2'] * 2 + ['노이즈'] * 10)

    return X, y, beta_true, feature_names, group_labels


print("=" * 60)
print(" Elastic Net 구현 및 Ridge/Lasso/Elastic Net 비교")
print("=" * 60)

X, y, beta_true, feature_names, group_labels = generate_correlated_data(
    n_samples=200, noise_std=1.0)

print(f"\n데이터 크기: X={X.shape}, y={y.shape}")
print(f"진정한 비영 계수 수: {np.sum(beta_true != 0)}")
print(f"그룹 1 (x0,x1,x2) 계수: {beta_true[0:3]}")
print(f"그룹 2 (x3,x4) 계수: {beta_true[3:5]}")

# 상관계수 확인
print(f"\n그룹 1 상관계수:")
print(f"  x0-x1: {np.corrcoef(X[:, 0], X[:, 1])[0, 1]:.4f}")
print(f"  x0-x2: {np.corrcoef(X[:, 0], X[:, 2])[0, 1]:.4f}")
print(f"그룹 2 상관계수:")
print(f"  x3-x4: {np.corrcoef(X[:, 3], X[:, 4])[0, 1]:.4f}")

# 특성 표준화
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)


# ============================================================
# 4. 직접 구현 vs sklearn 비교 (Elastic Net)
# ============================================================
print("\n" + "=" * 60)
print(" Elastic Net: 직접 구현 vs sklearn 비교")
print("=" * 60)

alpha_test = 0.1
l1_ratio_test = 0.5

# 직접 구현
enet_scratch = ElasticNetFromScratch(alpha=alpha_test,
                                     l1_ratio=l1_ratio_test,
                                     max_iter=5000, tol=1e-7)
enet_scratch.fit(X_scaled, y)

# sklearn
enet_sklearn = ElasticNet(alpha=alpha_test, l1_ratio=l1_ratio_test,
                          max_iter=5000, tol=1e-7)
enet_sklearn.fit(X_scaled, y)

print(f"\nalpha={alpha_test}, l1_ratio={l1_ratio_test}")
print(f"직접 구현 반복 횟수: {enet_scratch.n_iter_}")
print(f"sklearn 반복 횟수: {enet_sklearn.n_iter_}")

print(f"\n{'변수':<6} {'직접 구현':>12} {'sklearn':>12} {'실제':>8} {'그룹':>6}")
print("-" * 50)
for i in range(len(enet_scratch.coef_)):
    print(f"  w{i:<3} {enet_scratch.coef_[i]:>12.6f} {enet_sklearn.coef_[i]:>12.6f} "
          f"{beta_true[i]:>8.1f} {group_labels[i]:>6}")

print(f"\n계수 최대 차이: {np.max(np.abs(enet_scratch.coef_ - enet_sklearn.coef_)):.2e}")


# ============================================================
# 5. Ridge vs Lasso vs Elastic Net 비교
#    - 상관된 특성에서의 그룹화 효과(Grouping Effect) 비교
# ============================================================
print("\n" + "=" * 60)
print(" Ridge vs Lasso vs Elastic Net 비교 (상관된 특성)")
print("=" * 60)

# 교차 검증으로 각 방법의 최적 매개변수 선택
alphas_grid = np.logspace(-3, 1, 50)

# Ridge CV
ridge_cv = RidgeCV(alphas=alphas_grid, cv=5,
                   scoring='neg_mean_squared_error')
ridge_cv.fit(X_scaled, y)

# Lasso CV
lasso_cv = LassoCV(alphas=alphas_grid, cv=5, max_iter=5000)
lasso_cv.fit(X_scaled, y)

# Elastic Net CV (l1_ratio = 0.5)
enet_cv = ElasticNetCV(alphas=alphas_grid, l1_ratio=0.5, cv=5, max_iter=5000)
enet_cv.fit(X_scaled, y)

# 결과 비교
methods = {
    'Ridge': ridge_cv,
    'Lasso': lasso_cv,
    'Elastic Net': enet_cv
}

print(f"\n{'방법':<15} {'최적 alpha':>12} {'R^2':>8} {'MSE':>8} {'비영 계수 수':>12}")
print("-" * 60)
for name, model in methods.items():
    y_pred = model.predict(X_scaled)
    mse = mean_squared_error(y, y_pred)
    r2 = r2_score(y, y_pred)
    n_nonzero = np.sum(np.abs(model.coef_) > 1e-10)
    alpha_val = model.alpha_ if hasattr(model, 'alpha_') else model.alpha_
    print(f"{name:<15} {alpha_val:>12.6f} {r2:>8.4f} {mse:>8.4f} {n_nonzero:>12}")

# 상관된 변수 그룹의 계수 비교 (그룹화 효과)
print(f"\n--- 그룹화 효과(Grouping Effect) 비교 ---")
print(f"  상관된 변수 그룹의 계수가 유사한지 확인")
print(f"\n{'변수':<6} {'실제':>8} {'Ridge':>10} {'Lasso':>10} {'ElasticNet':>12} {'그룹':>6}")
print("-" * 58)
for i in range(min(8, len(beta_true))):
    print(f"  w{i:<3} {beta_true[i]:>8.1f} {ridge_cv.coef_[i]:>10.4f} "
          f"{lasso_cv.coef_[i]:>10.4f} {enet_cv.coef_[i]:>12.4f} {group_labels[i]:>6}")

# 그룹 내 계수 분산 (그룹화 효과 정량 평가)
print(f"\n--- 그룹 내 계수 분산 (작을수록 그룹화 효과 강함) ---")
for name, model in methods.items():
    g1_var = np.var(model.coef_[0:3])
    g2_var = np.var(model.coef_[3:5])
    print(f"  {name:<15} 그룹1 분산: {g1_var:.6f}, 그룹2 분산: {g2_var:.6f}")

print(f"\n  -> Elastic Net이 그룹 내 계수를 유사하게 유지 (Zou & Hastie, 2005)")


# ============================================================
# 6. 세 방법의 정규화 경로 종합 시각화
# ============================================================
print("\n" + "=" * 60)
print(" 정규화 경로 종합 비교 시각화")
print("=" * 60)

alphas_path = np.logspace(-3, 1.5, 100)

# 각 방법의 경로 계산
ridge_path = []
lasso_path = []
enet_path = []

for alpha in alphas_path:
    # Ridge
    ridge_model = Ridge(alpha=alpha)
    ridge_model.fit(X_scaled, y)
    ridge_path.append(ridge_model.coef_.copy())

    # Lasso
    lasso_model = Lasso(alpha=alpha, max_iter=5000, tol=1e-6)
    lasso_model.fit(X_scaled, y)
    lasso_path.append(lasso_model.coef_.copy())

    # Elastic Net
    enet_model = ElasticNet(alpha=alpha, l1_ratio=0.5, max_iter=5000, tol=1e-6)
    enet_model.fit(X_scaled, y)
    enet_path.append(enet_model.coef_.copy())

ridge_path = np.array(ridge_path)
lasso_path = np.array(lasso_path)
enet_path = np.array(enet_path)

print("정규화 경로 계산 완료")

# 시각화: 3개의 서브플롯
fig, axes = plt.subplots(1, 3, figsize=(20, 6))

paths = [ridge_path, lasso_path, enet_path]
titles = ['Ridge 회귀 (L2)', 'Lasso 회귀 (L1)', 'Elastic Net (L1+L2)']
colors_group = ['#e41a1c', '#ff7f00', '#fdbf6f',  # 그룹 1 (빨간 계열)
                '#377eb8', '#4daf4a',                # 그룹 2 (파란, 초록)
                ] + ['gray'] * 10                    # 노이즈 (회색)

for idx, (path, title) in enumerate(zip(paths, titles)):
    ax = axes[idx]
    for j in range(path.shape[1]):
        if j < 5:  # 중요한 변수만 레이블 표시
            label = f'{feature_names[j]} ({group_labels[j]})'
            linewidth = 2.0
            alpha_line = 1.0
        else:
            label = None
            linewidth = 0.7
            alpha_line = 0.3

        ax.plot(np.log10(alphas_path), path[:, j],
                color=colors_group[j], linewidth=linewidth,
                alpha=alpha_line, label=label)

    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax.set_xlabel('log10(lambda)', fontsize=12)
    ax.set_ylabel('회귀 계수 값', fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.legend(fontsize=8, loc='upper right')
    ax.grid(True, alpha=0.3)

plt.suptitle('Ridge vs Lasso vs Elastic Net 정규화 경로 비교\n'
             '(상관된 특성 그룹에서의 행동 차이)',
             fontsize=15, y=1.02)
plt.tight_layout()
plt.savefig('comparison_regularization_paths.png', dpi=150, bbox_inches='tight')
plt.show()
print("그래프 저장: comparison_regularization_paths.png")


# ============================================================
# 7. L1/L2 혼합 비율(l1_ratio)에 따른 효과 시각화
# ============================================================
print("\n" + "=" * 60)
print(" L1/L2 혼합 비율에 따른 효과")
print("=" * 60)

l1_ratios = [0.1, 0.3, 0.5, 0.7, 0.9]
alpha_fixed = 0.05  # 고정된 전체 정규화 강도

fig, axes = plt.subplots(1, len(l1_ratios), figsize=(20, 5))

for idx, l1_ratio in enumerate(l1_ratios):
    ax = axes[idx]

    enet = ElasticNet(alpha=alpha_fixed, l1_ratio=l1_ratio,
                      max_iter=5000, tol=1e-6)
    enet.fit(X_scaled, y)

    # 계수를 막대 그래프로
    n_vars = 8  # 처음 8개 변수만 표시
    bar_colors = ['#e41a1c' if i < 3 else '#377eb8' if i < 5 else 'gray'
                  for i in range(n_vars)]

    bars = ax.barh(range(n_vars), enet.coef_[:n_vars], color=bar_colors)
    ax.set_yticks(range(n_vars))
    ax.set_yticklabels([f'w{i}' for i in range(n_vars)])
    ax.axvline(x=0, color='black', linewidth=0.5)
    ax.set_title(f'l1_ratio={l1_ratio}', fontsize=12)
    ax.set_xlabel('계수 값', fontsize=10)

    n_nonzero = np.sum(np.abs(enet.coef_) > 1e-10)
    ax.text(0.05, 0.95, f'비영계수: {n_nonzero}',
            transform=ax.transAxes, fontsize=9, verticalalignment='top')

plt.suptitle(f'Elastic Net: L1/L2 비율에 따른 계수 변화 (alpha={alpha_fixed})\n'
             f'빨강=그룹1, 파랑=그룹2, 회색=노이즈',
             fontsize=13, y=1.05)
plt.tight_layout()
plt.savefig('elastic_net_l1_ratio_effect.png', dpi=150, bbox_inches='tight')
plt.show()
print("그래프 저장: elastic_net_l1_ratio_effect.png")


# ============================================================
# 8. 제약 영역 시각화 (L1, L2, Elastic Net)
# ============================================================
print("\n" + "=" * 60)
print(" L1, L2, Elastic Net 제약 영역 시각화")
print("=" * 60)

fig, axes = plt.subplots(1, 3, figsize=(18, 6))

theta = np.linspace(0, 2 * np.pi, 1000)

# L2 제약 (원): |beta|_2^2 <= 1  ->  beta1^2 + beta2^2 = 1
b1_l2 = np.cos(theta)
b2_l2 = np.sin(theta)

# L1 제약 (마름모): |beta|_1 <= 1  ->  |beta1| + |beta2| = 1
b1_l1 = np.array([1, 0, -1, 0, 1])
b2_l1 = np.array([0, 1, 0, -1, 0])

# Elastic Net 제약: alpha*|beta|_1 + (1-alpha)*|beta|_2^2 <= 1
# 다양한 alpha 값에 대해 수치적으로 계산
def elastic_net_boundary(alpha_mix, n_points=500):
    """Elastic Net 제약 영역의 경계를 수치적으로 계산"""
    angles = np.linspace(0, 2 * np.pi, n_points)
    b1_list = []
    b2_list = []
    for angle in angles:
        # 방향 벡터
        d1, d2 = np.cos(angle), np.sin(angle)
        # t * d 가 제약을 만족하는 최대 t 를 이분법으로 찾음
        lo, hi = 0.0, 5.0
        for _ in range(100):
            mid = (lo + hi) / 2
            penalty = alpha_mix * (abs(mid * d1) + abs(mid * d2)) + \
                      (1 - alpha_mix) * (mid * d1) ** 2 + \
                      (1 - alpha_mix) * (mid * d2) ** 2
            if penalty < 1:
                lo = mid
            else:
                hi = mid
        t = (lo + hi) / 2
        b1_list.append(t * d1)
        b2_list.append(t * d2)
    return np.array(b1_list), np.array(b2_list)

# 그래프 1: L2 (Ridge)
ax1 = axes[0]
ax1.fill(b1_l2, b2_l2, alpha=0.3, color='blue')
ax1.plot(b1_l2, b2_l2, 'b-', linewidth=2)
ax1.set_title('L2 제약 (Ridge)\n$\\beta_1^2 + \\beta_2^2 \\leq t$', fontsize=13)
ax1.set_xlabel('$\\beta_1$', fontsize=12)
ax1.set_ylabel('$\\beta_2$', fontsize=12)
ax1.set_aspect('equal')
ax1.grid(True, alpha=0.3)
ax1.axhline(y=0, color='gray', linewidth=0.5)
ax1.axvline(x=0, color='gray', linewidth=0.5)

# 그래프 2: L1 (Lasso)
ax2 = axes[1]
ax2.fill(b1_l1, b2_l1, alpha=0.3, color='red')
ax2.plot(b1_l1, b2_l1, 'r-', linewidth=2)
ax2.set_title('L1 제약 (Lasso)\n$|\\beta_1| + |\\beta_2| \\leq t$', fontsize=13)
ax2.set_xlabel('$\\beta_1$', fontsize=12)
ax2.set_ylabel('$\\beta_2$', fontsize=12)
ax2.set_aspect('equal')
ax2.grid(True, alpha=0.3)
ax2.axhline(y=0, color='gray', linewidth=0.5)
ax2.axvline(x=0, color='gray', linewidth=0.5)
# 꼭짓점 강조
ax2.plot([1, 0, -1, 0], [0, 1, 0, -1], 'ro', markersize=8)
ax2.annotate('희소 해가 나오는\n꼭짓점', xy=(1, 0), xytext=(0.5, 0.6),
             fontsize=9, arrowprops=dict(arrowstyle='->', color='red'),
             color='red')

# 그래프 3: Elastic Net (L1+L2)
ax3 = axes[2]

# 여러 alpha 비율에 대한 경계
for alpha_mix, color, label in [(0.3, '#ff7f0e', 'alpha=0.3'),
                                 (0.5, '#2ca02c', 'alpha=0.5'),
                                 (0.7, '#d62728', 'alpha=0.7')]:
    b1_en, b2_en = elastic_net_boundary(alpha_mix)
    ax3.plot(b1_en, b2_en, color=color, linewidth=2, label=label)

# L1과 L2도 참고로 표시
ax3.plot(b1_l2, b2_l2, 'b--', linewidth=1, alpha=0.5, label='L2 (Ridge)')
ax3.plot(b1_l1, b2_l1, 'r--', linewidth=1, alpha=0.5, label='L1 (Lasso)')

ax3.set_title('Elastic Net 제약\n$\\alpha|\\beta|_1 + (1-\\alpha)|\\beta|_2^2 \\leq t$',
              fontsize=13)
ax3.set_xlabel('$\\beta_1$', fontsize=12)
ax3.set_ylabel('$\\beta_2$', fontsize=12)
ax3.set_aspect('equal')
ax3.grid(True, alpha=0.3)
ax3.axhline(y=0, color='gray', linewidth=0.5)
ax3.axvline(x=0, color='gray', linewidth=0.5)
ax3.legend(fontsize=9)

plt.suptitle('정규화 제약 영역 비교: L1 (마름모) vs L2 (원) vs Elastic Net (둥근 마름모)',
             fontsize=14, y=1.02)
plt.tight_layout()
plt.savefig('constraint_regions.png', dpi=150, bbox_inches='tight')
plt.show()
print("그래프 저장: constraint_regions.png")


# ============================================================
# 9. 최종 종합 비교 요약
# ============================================================
print("\n" + "=" * 60)
print(" 최종 종합 비교 요약")
print("=" * 60)

print(f"""
+------------------+----------+----------+--------------+
|       방법       |  패널티  | 변수선택 |  그룹화 효과 |
+------------------+----------+----------+--------------+
| Ridge (L2)       |  ||w||^2 |    X     |      O       |
| Lasso (L1)       |  ||w||_1 |    O     |      X       |
| Elastic Net      | L1 + L2  |    O     |      O       |
+------------------+----------+----------+--------------+

Ridge 회귀:
  - 닫힌 형태 해: w = (X'X + lambda*I)^(-1) X'y
  - 모든 계수를 축소하지만 0으로 만들지는 않음
  - 다중공선성에 강건

Lasso 회귀:
  - 좌표 하강법 + 연성 임계값으로 풀이
  - 일부 계수를 정확히 0으로 만듦 (변수 선택)
  - 상관된 변수 중 하나만 선택하는 경향

Elastic Net:
  - L1과 L2의 장점을 결합
  - 변수 선택 + 그룹화 효과
  - 상관된 변수들의 계수를 유사하게 유지
""")

print("=" * 60)
print(" 완료!")
print("=" * 60)
