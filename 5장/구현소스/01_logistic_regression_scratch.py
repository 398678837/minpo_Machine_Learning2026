# -*- coding: utf-8 -*-
"""
01_logistic_regression_scratch.py
로지스틱 회귀를 밑바닥부터 구현하고 sklearn과 비교

핵심 구현 내용:
1. 시그모이드 함수
2. 이진 교차 엔트로피(로그 손실) 비용 함수
3. 경사하강법을 통한 파라미터 학습
4. sklearn LogisticRegression과 성능 비교
5. 결정 경계(Decision Boundary) 시각화
6. 비용 함수 수렴 곡선

참고 논문: Cox (1958) "The Regression Analysis of Binary Sequences"
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.decomposition import PCA


# ============================================================
# 1. 핵심 함수 구현
# ============================================================

def sigmoid(z):
    """
    시그모이드(로지스틱) 함수

    수식: sigma(z) = 1 / (1 + exp(-z))

    Cox(1958)가 제안한 로짓 변환의 역함수이다.
    임의의 실수값 z를 (0, 1) 범위의 확률값으로 변환한다.

    수치 안정성을 위해 np.clip으로 오버플로를 방지한다.
    """
    # 수치 안정성: z가 너무 크거나 작으면 exp에서 오버플로 발생 가능
    z = np.clip(z, -500, 500)
    return 1.0 / (1.0 + np.exp(-z))


def compute_cost(X, y, weights, bias):
    """
    이진 교차 엔트로피(Binary Cross Entropy) / 로그 손실(Log Loss) 계산

    수식: J(w, b) = -(1/m) * sum[ y*log(y_hat) + (1-y)*log(1-y_hat) ]

    이 비용 함수는 Cox(1958)의 음의 로그 우도(negative log-likelihood)와 동일하다.
    MLE(최대우도추정)에서 우도를 최대화하는 것은 이 비용 함수를 최소화하는 것과 같다.

    매개변수:
        X: 입력 특성 행렬 (m, n)
        y: 실제 레이블 벡터 (m,)
        weights: 가중치 벡터 (n,)
        bias: 편향 스칼라

    반환:
        cost: 스칼라 비용 값
    """
    m = X.shape[0]  # 표본 수

    # 선형 결합: z = X @ w + b
    z = np.dot(X, weights) + bias

    # 시그모이드 함수 적용: 확률 예측
    y_hat = sigmoid(z)

    # 수치 안정성: log(0) 방지
    epsilon = 1e-15
    y_hat = np.clip(y_hat, epsilon, 1 - epsilon)

    # 이진 교차 엔트로피 계산
    cost = -(1.0 / m) * np.sum(
        y * np.log(y_hat) + (1 - y) * np.log(1 - y_hat)
    )

    return cost


def compute_gradients(X, y, weights, bias):
    """
    비용 함수에 대한 그래디언트(기울기) 계산

    수식:
        dJ/dw = (1/m) * X^T @ (y_hat - y)
        dJ/db = (1/m) * sum(y_hat - y)

    이 그래디언트는 Cox(1958)의 스코어 방정식에서 유도된다.
    MLE의 스코어 함수: dL/dbeta = X^T(y - p)의 부호를 반전한 것이다.
    (최대화 -> 최소화 변환 시 부호 반전)

    매개변수:
        X: 입력 특성 행렬 (m, n)
        y: 실제 레이블 벡터 (m,)
        weights: 가중치 벡터 (n,)
        bias: 편향 스칼라

    반환:
        dw: 가중치 그래디언트 벡터 (n,)
        db: 편향 그래디언트 스칼라
    """
    m = X.shape[0]

    # 예측 확률 계산
    z = np.dot(X, weights) + bias
    y_hat = sigmoid(z)

    # 오차: 예측값 - 실제값
    error = y_hat - y

    # 가중치 그래디언트: (1/m) * X^T @ error
    dw = (1.0 / m) * np.dot(X.T, error)

    # 편향 그래디언트: (1/m) * sum(error)
    db = (1.0 / m) * np.sum(error)

    return dw, db


def logistic_regression_gd(X, y, learning_rate=0.1, n_iterations=1000, verbose=True):
    """
    경사하강법(Gradient Descent)을 사용한 로지스틱 회귀 학습

    Cox(1958)는 뉴턴-랩슨 방법을 제안했으나,
    여기서는 더 직관적인 경사하강법을 사용한다.
    경사하강법은 뉴턴-랩슨의 특수한 경우(2차 미분을 단위 행렬로 근사)로 볼 수 있다.

    매개변수:
        X: 입력 특성 행렬 (m, n)
        y: 실제 레이블 벡터 (m,)
        learning_rate: 학습률 (보폭 크기)
        n_iterations: 반복 횟수
        verbose: 학습 과정 출력 여부

    반환:
        weights: 학습된 가중치 벡터
        bias: 학습된 편향
        cost_history: 반복별 비용 기록
    """
    m, n = X.shape

    # 파라미터 초기화 (0으로 시작)
    weights = np.zeros(n)
    bias = 0.0

    # 비용 기록을 위한 리스트
    cost_history = []

    for i in range(n_iterations):
        # 비용 계산
        cost = compute_cost(X, y, weights, bias)
        cost_history.append(cost)

        # 그래디언트 계산
        dw, db = compute_gradients(X, y, weights, bias)

        # 파라미터 업데이트: w = w - lr * dw
        weights -= learning_rate * dw
        bias -= learning_rate * db

        # 100회마다 진행 상황 출력
        if verbose and (i % 100 == 0 or i == n_iterations - 1):
            print(f"  반복 {i:5d}/{n_iterations} | 비용: {cost:.6f}")

    return weights, bias, cost_history


def predict(X, weights, bias, threshold=0.5):
    """
    학습된 파라미터를 사용하여 예측 수행

    매개변수:
        X: 입력 특성 행렬
        weights: 학습된 가중치
        bias: 학습된 편향
        threshold: 분류 임계값 (기본값 0.5)

    반환:
        predictions: 예측 클래스 (0 또는 1)
        probabilities: 예측 확률
    """
    z = np.dot(X, weights) + bias
    probabilities = sigmoid(z)
    predictions = (probabilities >= threshold).astype(int)
    return predictions, probabilities


# ============================================================
# 2. 시그모이드 함수 시각화
# ============================================================

print("=" * 70)
print("1단계: 시그모이드 함수 시각화")
print("=" * 70)

z_values = np.linspace(-10, 10, 300)
sigmoid_values = sigmoid(z_values)

plt.figure(figsize=(10, 6))
plt.plot(z_values, sigmoid_values, 'b-', linewidth=2.5,
         label=r'$\sigma(z) = \frac{1}{1+e^{-z}}$')
plt.axhline(y=0.5, color='r', linestyle='--', alpha=0.7, label='임계값 = 0.5')
plt.axvline(x=0, color='gray', linestyle='--', alpha=0.5)

# 주요 포인트 표시
plt.scatter([0], [0.5], color='red', s=100, zorder=5)
plt.annotate('(0, 0.5)', xy=(0, 0.5), xytext=(1, 0.35),
             fontsize=11, arrowprops=dict(arrowstyle='->', color='red'))

plt.xlabel('z (선형 결합값)', fontsize=13)
plt.ylabel(r'$\sigma(z)$ (확률)', fontsize=13)
plt.title('시그모이드 함수 (Sigmoid Function)', fontsize=15)
plt.legend(fontsize=12, loc='upper left')
plt.grid(True, alpha=0.3)
plt.ylim(-0.05, 1.05)
plt.tight_layout()
plt.savefig('sigmoid_function.png', dpi=150, bbox_inches='tight')
plt.show()
print("[저장 완료] sigmoid_function.png\n")


# ============================================================
# 3. 로그 손실 함수 시각화
# ============================================================

print("=" * 70)
print("2단계: 로그 손실(이진 교차 엔트로피) 함수 시각화")
print("=" * 70)

y_hat_values = np.linspace(0.001, 0.999, 300)

# y=1일 때 손실: -log(y_hat)
loss_when_y1 = -np.log(y_hat_values)
# y=0일 때 손실: -log(1 - y_hat)
loss_when_y0 = -np.log(1 - y_hat_values)

plt.figure(figsize=(10, 6))
plt.plot(y_hat_values, loss_when_y1, 'b-', linewidth=2.5,
         label=r'y=1: $-\log(\hat{y})$')
plt.plot(y_hat_values, loss_when_y0, 'r-', linewidth=2.5,
         label=r'y=0: $-\log(1-\hat{y})$')

plt.xlabel(r'예측 확률 $\hat{y}$', fontsize=13)
plt.ylabel('손실 (Loss)', fontsize=13)
plt.title('로그 손실 함수 (Log Loss / Binary Cross Entropy)', fontsize=15)
plt.legend(fontsize=12)
plt.grid(True, alpha=0.3)
plt.ylim(0, 5)
plt.tight_layout()
plt.savefig('log_loss_function.png', dpi=150, bbox_inches='tight')
plt.show()
print("[저장 완료] log_loss_function.png\n")


# ============================================================
# 4. 유방암 데이터로 학습 및 비교
# ============================================================

print("=" * 70)
print("3단계: Breast Cancer 데이터셋으로 학습 및 sklearn 비교")
print("=" * 70)

# 데이터 로드
data = load_breast_cancer()
X_full = data.data
y_full = data.target
feature_names = data.feature_names

print(f"데이터 크기: {X_full.shape}")
print(f"클래스 분포: 악성(0)={np.sum(y_full == 0)}, 양성(1)={np.sum(y_full == 1)}")
print(f"특성 수: {len(feature_names)}")
print()

# 학습/테스트 분리
X_train_full, X_test_full, y_train, y_test = train_test_split(
    X_full, y_full, test_size=0.2, random_state=42, stratify=y_full
)

# 특성 표준화 (경사하강법 수렴을 위해 필수)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_full)
X_test_scaled = scaler.transform(X_test_full)

# --- 직접 구현한 로지스틱 회귀 ---
print("[직접 구현] 경사하강법으로 로지스틱 회귀 학습 시작...")
weights_scratch, bias_scratch, cost_history = logistic_regression_gd(
    X_train_scaled, y_train,
    learning_rate=0.1,
    n_iterations=1000,
    verbose=True
)

pred_scratch, prob_scratch = predict(X_test_scaled, weights_scratch, bias_scratch)
acc_scratch = accuracy_score(y_test, pred_scratch)
print(f"\n[직접 구현] 정확도: {acc_scratch:.4f} ({acc_scratch*100:.2f}%)")

# --- sklearn 로지스틱 회귀 ---
print("\n[sklearn] LogisticRegression 학습...")
model_sklearn = LogisticRegression(max_iter=1000, random_state=42)
model_sklearn.fit(X_train_scaled, y_train)
pred_sklearn = model_sklearn.predict(X_test_scaled)
acc_sklearn = accuracy_score(y_test, pred_sklearn)
print(f"[sklearn] 정확도: {acc_sklearn:.4f} ({acc_sklearn*100:.2f}%)")

# --- 결과 비교 ---
print("\n" + "=" * 50)
print("성능 비교 결과")
print("=" * 50)
print(f"  직접 구현 (경사하강법): {acc_scratch:.4f}")
print(f"  sklearn (L-BFGS):      {acc_sklearn:.4f}")
print(f"  차이:                   {abs(acc_scratch - acc_sklearn):.4f}")

# 파라미터 비교 (상위 5개 특성)
print("\n가중치 비교 (상위 5개 특성):")
print(f"{'특성':<30s} {'직접구현':>10s} {'sklearn':>10s}")
print("-" * 52)
for i in range(5):
    print(f"{feature_names[i]:<30s} {weights_scratch[i]:>10.4f} {model_sklearn.coef_[0][i]:>10.4f}")


# ============================================================
# 5. 비용 함수 수렴 곡선
# ============================================================

print("\n" + "=" * 70)
print("4단계: 비용 함수 수렴 곡선 시각화")
print("=" * 70)

plt.figure(figsize=(10, 6))
plt.plot(range(len(cost_history)), cost_history, 'b-', linewidth=1.5)
plt.xlabel('반복 횟수 (Iteration)', fontsize=13)
plt.ylabel('비용 (Cost / Log Loss)', fontsize=13)
plt.title('경사하강법 비용 함수 수렴 곡선', fontsize=15)
plt.grid(True, alpha=0.3)

# 초기/최종 비용 표시
plt.annotate(f'초기 비용: {cost_history[0]:.4f}',
             xy=(0, cost_history[0]),
             xytext=(100, cost_history[0] - 0.05),
             fontsize=11, arrowprops=dict(arrowstyle='->', color='red'))
plt.annotate(f'최종 비용: {cost_history[-1]:.4f}',
             xy=(len(cost_history)-1, cost_history[-1]),
             xytext=(len(cost_history)-300, cost_history[-1] + 0.1),
             fontsize=11, arrowprops=dict(arrowstyle='->', color='green'))

plt.tight_layout()
plt.savefig('cost_convergence.png', dpi=150, bbox_inches='tight')
plt.show()
print("[저장 완료] cost_convergence.png\n")


# ============================================================
# 6. 2D 결정 경계 시각화 (PCA 사용)
# ============================================================

print("=" * 70)
print("5단계: 2D 결정 경계 시각화 (PCA로 2차원 축소)")
print("=" * 70)

# PCA로 2차원 축소
pca = PCA(n_components=2)
X_train_2d = pca.fit_transform(X_train_scaled)
X_test_2d = pca.transform(X_test_scaled)

print(f"PCA 설명 분산 비율: {pca.explained_variance_ratio_}")
print(f"총 설명 분산: {pca.explained_variance_ratio_.sum():.4f}")

# 2D 데이터로 직접 구현 로지스틱 회귀 학습
print("\n[직접 구현] 2D 데이터로 학습...")
weights_2d, bias_2d, cost_history_2d = logistic_regression_gd(
    X_train_2d, y_train,
    learning_rate=0.1,
    n_iterations=1000,
    verbose=False
)
pred_2d, _ = predict(X_test_2d, weights_2d, bias_2d)
acc_2d = accuracy_score(y_test, pred_2d)
print(f"[직접 구현] 2D 정확도: {acc_2d:.4f}")

# 2D sklearn 비교
model_2d = LogisticRegression(max_iter=1000, random_state=42)
model_2d.fit(X_train_2d, y_train)
acc_2d_sklearn = accuracy_score(y_test, model_2d.predict(X_test_2d))
print(f"[sklearn]   2D 정확도: {acc_2d_sklearn:.4f}")

# 결정 경계 시각화
fig, axes = plt.subplots(1, 2, figsize=(16, 7))

for ax_idx, (title, w, b) in enumerate([
    ("직접 구현 (경사하강법)", weights_2d, bias_2d),
    ("sklearn LogisticRegression", model_2d.coef_[0], model_2d.intercept_[0])
]):
    ax = axes[ax_idx]

    # 메시 그리드 생성
    x_min, x_max = X_train_2d[:, 0].min() - 1, X_train_2d[:, 0].max() + 1
    y_min, y_max = X_train_2d[:, 1].min() - 1, X_train_2d[:, 1].max() + 1
    xx, yy = np.meshgrid(
        np.linspace(x_min, x_max, 300),
        np.linspace(y_min, y_max, 300)
    )

    # 메시의 각 점에서 예측 확률 계산
    grid_points = np.c_[xx.ravel(), yy.ravel()]
    z_grid = np.dot(grid_points, w) + b
    prob_grid = sigmoid(z_grid).reshape(xx.shape)

    # 확률 등고선 표시
    contour = ax.contourf(xx, yy, prob_grid, levels=50, cmap='RdYlBu', alpha=0.8)
    plt.colorbar(contour, ax=ax, label='P(양성)')

    # 결정 경계 (확률 = 0.5인 선)
    ax.contour(xx, yy, prob_grid, levels=[0.5], colors='black', linewidths=2)

    # 데이터 포인트 표시
    colors = ['red', 'blue']
    labels = ['악성 (0)', '양성 (1)']
    for cls in [0, 1]:
        mask = y_train == cls
        ax.scatter(X_train_2d[mask, 0], X_train_2d[mask, 1],
                   c=colors[cls], alpha=0.5, s=30, label=labels[cls],
                   edgecolors='black', linewidth=0.3)

    ax.set_xlabel('PC1', fontsize=12)
    ax.set_ylabel('PC2', fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.legend(loc='upper right', fontsize=10)

plt.suptitle('로지스틱 회귀 결정 경계 비교 (Breast Cancer - PCA 2D)', fontsize=16, y=1.02)
plt.tight_layout()
plt.savefig('decision_boundary_comparison.png', dpi=150, bbox_inches='tight')
plt.show()
print("[저장 완료] decision_boundary_comparison.png\n")


# ============================================================
# 7. 학습률에 따른 수렴 비교
# ============================================================

print("=" * 70)
print("6단계: 학습률에 따른 수렴 비교")
print("=" * 70)

learning_rates = [0.01, 0.05, 0.1, 0.5, 1.0]
plt.figure(figsize=(10, 6))

for lr in learning_rates:
    _, _, history = logistic_regression_gd(
        X_train_scaled, y_train,
        learning_rate=lr,
        n_iterations=500,
        verbose=False
    )
    plt.plot(range(len(history)), history, linewidth=1.5, label=f'lr={lr}')

plt.xlabel('반복 횟수 (Iteration)', fontsize=13)
plt.ylabel('비용 (Cost)', fontsize=13)
plt.title('학습률(Learning Rate)에 따른 수렴 속도 비교', fontsize=15)
plt.legend(fontsize=11)
plt.grid(True, alpha=0.3)
plt.ylim(0, 1.0)
plt.tight_layout()
plt.savefig('learning_rate_comparison.png', dpi=150, bbox_inches='tight')
plt.show()
print("[저장 완료] learning_rate_comparison.png\n")


# ============================================================
# 8. 최종 요약
# ============================================================

print("=" * 70)
print("최종 요약")
print("=" * 70)
print(f"""
로지스틱 회귀 직접 구현 결과:
  - 시그모이드 함수: sigma(z) = 1/(1+exp(-z))
  - 비용 함수: 이진 교차 엔트로피 (Binary Cross Entropy)
  - 최적화: 경사하강법 (Gradient Descent)

성능 비교 (Breast Cancer 데이터셋):
  - 직접 구현: {acc_scratch:.4f} ({acc_scratch*100:.2f}%)
  - sklearn:   {acc_sklearn:.4f} ({acc_sklearn*100:.2f}%)

결론:
  직접 구현한 로지스틱 회귀가 sklearn과 유사한 성능을 달성하였다.
  미세한 차이는 최적화 알고리즘의 차이(경사하강법 vs L-BFGS)와
  정규화(sklearn은 기본 L2 정규화 적용) 때문이다.
""")
