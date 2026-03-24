"""
01_numpy_linear_algebra.py
NumPy를 활용한 선형대수 구현

목적: 행렬 분해(LU, QR, SVD), 연립방정식 풀기, 고유값 분해 등
      핵심 선형대수 연산을 NumPy로 구현하고, ML에서의 활용 예시를 보인다.

주요 개념:
  - LU 분해: 가우스 소거법의 행렬 표현
  - QR 분해: 그램-슈미트 정규 직교화
  - SVD (특이값 분해): 차원 축소의 수학적 기반
  - 고유값/고유벡터: PCA의 핵심
  - 연립방정식: 선형 회귀의 정규방정식
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import linalg as la

# ============================================================
# 한글 폰트 설정 (Windows)
# ============================================================
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

np.set_printoptions(precision=4, suppress=True)  # 출력 깔끔하게


# ============================================================
# 1. LU 분해 (LU Decomposition)
# ============================================================
print("=" * 60)
print("  1. LU 분해 (LU Decomposition)")
print("=" * 60)
print("  A = P @ L @ U")
print("  P: 치환 행렬, L: 하삼각 행렬, U: 상삼각 행렬")
print("  용도: 연립방정식 풀기, 행렬식 계산, 역행렬 계산")

A = np.array([[2, 1, 1],
              [4, 3, 3],
              [8, 7, 9]], dtype=float)

print(f"\n원본 행렬 A:\n{A}")

# SciPy의 LU 분해
P, L, U = la.lu(A)

print(f"\n치환 행렬 P:\n{P}")
print(f"\n하삼각 행렬 L:\n{L}")
print(f"\n상삼각 행렬 U:\n{U}")

# 검증: P @ L @ U = A
복원 = P @ L @ U
print(f"\n검증 (P @ L @ U):\n{복원}")
print(f"원본과 동일한가? {np.allclose(A, 복원)}")


# ============================================================
# 2. QR 분해 (QR Decomposition)
# ============================================================
print("\n" + "=" * 60)
print("  2. QR 분해 (QR Decomposition)")
print("=" * 60)
print("  A = Q @ R")
print("  Q: 직교 행렬 (Q^T @ Q = I), R: 상삼각 행렬")
print("  용도: 최소제곱법, 고유값 알고리즘, 수치적 안정성")

A_qr = np.array([[1, 1, 0],
                 [1, 0, 1],
                 [0, 1, 1]], dtype=float)

print(f"\n원본 행렬 A:\n{A_qr}")

Q, R = np.linalg.qr(A_qr)

print(f"\n직교 행렬 Q:\n{Q}")
print(f"\n상삼각 행렬 R:\n{R}")

# 검증
print(f"\n검증 (Q @ R):\n{Q @ R}")
print(f"원본과 동일한가? {np.allclose(A_qr, Q @ R)}")

# Q의 직교성 검증: Q^T @ Q = I
print(f"\nQ^T @ Q (단위행렬이어야 함):\n{Q.T @ Q}")
print(f"직교 행렬인가? {np.allclose(Q.T @ Q, np.eye(3))}")


# ============================================================
# 3. SVD (특이값 분해, Singular Value Decomposition)
# ============================================================
print("\n" + "=" * 60)
print("  3. SVD (특이값 분해)")
print("=" * 60)
print("  A = U @ Sigma @ V^T")
print("  U: 왼쪽 특이벡터, Sigma: 특이값 대각행렬, V^T: 오른쪽 특이벡터")
print("  용도: 차원 축소(PCA), 데이터 압축, 추천 시스템, 잠재 의미 분석")

# 데이터 행렬 (5개 샘플, 3개 특성)
A_svd = np.array([[1, 2, 0],
                  [0, 1, 1],
                  [2, 0, 1],
                  [1, 1, 1],
                  [3, 2, 1]], dtype=float)

print(f"\n데이터 행렬 A ({A_svd.shape[0]}x{A_svd.shape[1]}):\n{A_svd}")

U, s, Vt = np.linalg.svd(A_svd, full_matrices=False)

print(f"\nU ({U.shape}):\n{U}")
print(f"\n특이값 (Sigma): {s}")
print(f"\nV^T ({Vt.shape}):\n{Vt}")

# 검증: A = U @ diag(s) @ V^T
Sigma = np.diag(s)
복원_svd = U @ Sigma @ Vt
print(f"\n검증 (U @ Sigma @ V^T):\n{복원_svd}")
print(f"원본과 동일한가? {np.allclose(A_svd, 복원_svd)}")

# --- SVD를 활용한 차원 축소 (k개의 주요 특이값만 사용) ---
print(f"\n[SVD를 활용한 차원 축소 - 상위 2개 특이값]")
k = 2
A_근사 = U[:, :k] @ np.diag(s[:k]) @ Vt[:k, :]
print(f"근사 행렬 (rank-{k}):\n{A_근사}")

# 근사 오차
오차 = np.linalg.norm(A_svd - A_근사, 'fro')
원본_노름 = np.linalg.norm(A_svd, 'fro')
print(f"\n프로베니우스 노름 오차: {오차:.4f}")
print(f"상대 오차: {오차 / 원본_노름 * 100:.2f}%")
print(f"정보 보존 비율: {(1 - 오차 / 원본_노름) * 100:.2f}%")

# 각 특이값의 에너지(분산 설명력)
에너지 = s ** 2 / np.sum(s ** 2) * 100
누적_에너지 = np.cumsum(에너지)
print(f"\n특이값별 설명 비율: {에너지}")
print(f"누적 설명 비율: {누적_에너지}")


# ============================================================
# 4. 고유값 분해 (Eigendecomposition)
# ============================================================
print("\n" + "=" * 60)
print("  4. 고유값 분해 (Eigendecomposition)")
print("=" * 60)
print("  A @ v = lambda * v")
print("  lambda: 고유값, v: 고유벡터")
print("  용도: PCA (주성분 분석), 스펙트럴 클러스터링, 안정성 분석")

# 대칭 행렬 (공분산 행렬 예시)
공분산행렬 = np.array([[4, 2, 1],
                      [2, 3, 1],
                      [1, 1, 2]], dtype=float)

print(f"\n공분산 행렬:\n{공분산행렬}")

고유값, 고유벡터 = np.linalg.eigh(공분산행렬)  # eigh: 대칭 행렬용 (더 안정적)

print(f"\n고유값: {고유값}")
print(f"\n고유벡터 (열 벡터):\n{고유벡터}")

# 검증: A @ v = lambda * v
for i in range(len(고유값)):
    좌변 = 공분산행렬 @ 고유벡터[:, i]
    우변 = 고유값[i] * 고유벡터[:, i]
    print(f"\n고유값 {고유값[i]:.4f}:")
    print(f"  A @ v = {좌변}")
    print(f"  lambda * v = {우변}")
    print(f"  동일한가? {np.allclose(좌변, 우변)}")

# --- PCA 시뮬레이션 ---
print(f"\n[PCA 시뮬레이션: 고유값 기반 주성분 선택]")
분산_설명비율 = 고유값 / np.sum(고유값) * 100
print(f"각 주성분의 분산 설명 비율: {분산_설명비율}")
print(f"누적: {np.cumsum(분산_설명비율)}")
print(f"-> 상위 2개 주성분으로 {np.cumsum(분산_설명비율)[-2]:.1f}%의 분산 설명 가능")


# ============================================================
# 5. 연립방정식 풀기 (Solving Linear Systems)
# ============================================================
print("\n" + "=" * 60)
print("  5. 연립방정식 풀기 (Ax = b)")
print("=" * 60)
print("  선형회귀의 정규방정식: (X^T X) beta = X^T y")

# 간단한 연립방정식
# 2x + y = 5
# x + 3y = 7
A_sys = np.array([[2, 1],
                  [1, 3]], dtype=float)
b_sys = np.array([5, 7], dtype=float)

print(f"\n연립방정식:")
print(f"  2x + y = 5")
print(f"  x + 3y = 7")

x_해 = np.linalg.solve(A_sys, b_sys)
print(f"\n해: x = {x_해[0]:.4f}, y = {x_해[1]:.4f}")

# 검증
print(f"검증 (A @ x): {A_sys @ x_해}")
print(f"b: {b_sys}")
print(f"동일한가? {np.allclose(A_sys @ x_해, b_sys)}")


# --- 선형회귀의 정규방정식 (Normal Equation) ---
print(f"\n[선형회귀 정규방정식 예시]")
print(f"  beta = (X^T X)^(-1) X^T y")

# 학습 데이터 생성
np.random.seed(42)
n_samples = 50
X_원본 = np.random.uniform(0, 10, (n_samples, 1))
노이즈 = np.random.normal(0, 1, (n_samples, 1))
y = 3 * X_원본 + 2 + 노이즈  # y = 3x + 2 + 노이즈

# 설계 행렬 (절편 항 추가)
ones = np.ones((n_samples, 1))
X = np.hstack([ones, X_원본])  # [1, x]

print(f"\n데이터 크기: {n_samples}개 샘플")
print(f"설계 행렬 X shape: {X.shape}")

# 방법 1: 역행렬 사용 (수치적으로 불안정)
beta_inv = np.linalg.inv(X.T @ X) @ X.T @ y
print(f"\n방법 1 (역행렬): beta = {beta_inv.flatten()}")

# 방법 2: solve 사용 (수치적으로 안정)
beta_solve = np.linalg.solve(X.T @ X, X.T @ y)
print(f"방법 2 (solve):  beta = {beta_solve.flatten()}")

# 방법 3: lstsq 사용 (최소제곱법, 가장 안정적)
beta_lstsq, 잔차, 랭크, 특이값 = np.linalg.lstsq(X, y, rcond=None)
print(f"방법 3 (lstsq):  beta = {beta_lstsq.flatten()}")

print(f"\n참값: 절편=2, 기울기=3")
print(f"추정값: 절편={beta_lstsq[0, 0]:.4f}, 기울기={beta_lstsq[1, 0]:.4f}")


# ============================================================
# 6. 시각화
# ============================================================
fig, axes = plt.subplots(2, 3, figsize=(16, 10))

# (1) SVD 특이값 에너지
axes[0, 0].bar(range(1, len(s) + 1), 에너지, color='#3498db', edgecolor='black')
axes[0, 0].plot(range(1, len(s) + 1), 누적_에너지, 'ro-', linewidth=2, label='누적')
axes[0, 0].set_title('SVD: 특이값별 설명 비율', fontsize=12, fontweight='bold')
axes[0, 0].set_xlabel('특이값 번호')
axes[0, 0].set_ylabel('설명 비율 (%)')
axes[0, 0].legend()
axes[0, 0].set_ylim(0, 105)

# (2) 고유값 분석
axes[0, 1].bar(range(1, len(고유값) + 1), 고유값[::-1], color='#2ecc71', edgecolor='black')
axes[0, 1].set_title('고유값 분해: 고유값 크기', fontsize=12, fontweight='bold')
axes[0, 1].set_xlabel('주성분 번호')
axes[0, 1].set_ylabel('고유값')

# (3) PCA 분산 설명 비율
정렬_분산 = np.sort(분산_설명비율)[::-1]
누적_정렬 = np.cumsum(정렬_분산)
axes[0, 2].bar(range(1, len(정렬_분산) + 1), 정렬_분산, color='#f39c12',
               edgecolor='black', alpha=0.7, label='개별')
axes[0, 2].plot(range(1, len(정렬_분산) + 1), 누적_정렬, 'ro-', linewidth=2, label='누적')
axes[0, 2].axhline(y=90, color='gray', linestyle='--', alpha=0.5, label='90% 기준선')
axes[0, 2].set_title('PCA: 주성분별 분산 설명 비율', fontsize=12, fontweight='bold')
axes[0, 2].set_xlabel('주성분 번호')
axes[0, 2].set_ylabel('분산 설명 비율 (%)')
axes[0, 2].legend(fontsize=9)

# (4) 선형회귀 결과
axes[1, 0].scatter(X_원본, y, alpha=0.6, color='#3498db', label='데이터')
x_선 = np.linspace(0, 10, 100).reshape(-1, 1)
X_선 = np.hstack([np.ones((100, 1)), x_선])
y_예측 = X_선 @ beta_lstsq
axes[1, 0].plot(x_선, y_예측, 'r-', linewidth=2,
                label=f'회귀선: y={beta_lstsq[1, 0]:.2f}x+{beta_lstsq[0, 0]:.2f}')
axes[1, 0].set_title('정규방정식을 이용한 선형회귀', fontsize=12, fontweight='bold')
axes[1, 0].set_xlabel('x')
axes[1, 0].set_ylabel('y')
axes[1, 0].legend()

# (5) 행렬 분해 히트맵 - 원본 vs SVD 근사
im1 = axes[1, 1].imshow(A_svd, cmap='viridis', aspect='auto')
axes[1, 1].set_title('원본 행렬 A', fontsize=12, fontweight='bold')
plt.colorbar(im1, ax=axes[1, 1])
for i in range(A_svd.shape[0]):
    for j in range(A_svd.shape[1]):
        axes[1, 1].text(j, i, f'{A_svd[i, j]:.1f}', ha='center', va='center', color='white')

im2 = axes[1, 2].imshow(A_근사, cmap='viridis', aspect='auto')
axes[1, 2].set_title(f'SVD 근사 (rank-{k})', fontsize=12, fontweight='bold')
plt.colorbar(im2, ax=axes[1, 2])
for i in range(A_근사.shape[0]):
    for j in range(A_근사.shape[1]):
        axes[1, 2].text(j, i, f'{A_근사[i, j]:.1f}', ha='center', va='center', color='white')

plt.suptitle('NumPy 선형대수: 행렬 분해와 ML 활용',
             fontsize=15, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('D:/26년1학기/기계학습/3장/구현소스/numpy_linear_algebra_결과.png',
            dpi=150, bbox_inches='tight')
plt.show()

print("\n" + "=" * 60)
print("  핵심 정리: 선형대수와 기계학습의 관계")
print("=" * 60)
print("""
| 선형대수 연산   | ML 활용                          |
|----------------|----------------------------------|
| SVD            | PCA 차원 축소, 추천 시스템, LSA   |
| 고유값 분해     | PCA, 스펙트럴 클러스터링          |
| QR 분해        | 최소제곱법의 수치적 안정 풀이      |
| LU 분해        | 연립방정식 효율적 풀이             |
| 정규방정식      | 선형 회귀 파라미터 추정            |
| 행렬곱 (@ 연산) | 신경망 순전파, 커널 계산           |
| 역행렬         | 선형 회귀 (수치적으로 비추천)      |
| 노름           | 정규화 (L1, L2 규제)              |
""")
