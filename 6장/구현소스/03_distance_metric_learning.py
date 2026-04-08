# -*- coding: utf-8 -*-
"""
03_distance_metric_learning.py
Weinberger & Saul (2009)의 거리 메트릭 학습 아이디어를 단순화하여 구현한다.

구현 내용:
1. 유클리드 거리 KNN (기본)
2. 마할라노비스 거리 학습 (단순화된 LMNN 아이디어 기반)
3. 공분산 기반 마할라노비스 거리 (각 클래스의 공분산 활용)
4. 유클리드 vs 학습된 메트릭 성능 비교 (Wine 데이터)
5. 변환된 특성 공간 시각화

데이터: sklearn load_wine() (3 클래스, 13 특성)
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.decomposition import PCA
from collections import Counter


# ============================================================
# 1. 마할라노비스 거리 관련 함수
# ============================================================

def mahalanobis_distance(x1, x2, M):
    """
    마할라노비스 거리 계산
    d_M(x1, x2) = sqrt((x1 - x2)^T M (x1 - x2))

    매개변수:
        x1: 첫 번째 데이터 포인트 (d,)
        x2: 두 번째 데이터 포인트 (d,)
        M: 양의 반정치 행렬 (d x d)
    반환값:
        float, 마할라노비스 거리
    """
    diff = x1 - x2
    return np.sqrt(diff @ M @ diff)


def compute_class_scatter_matrices(X, y):
    """
    클래스 내 산포 행렬(S_W)과 클래스 간 산포 행렬(S_B)을 계산한다.
    Fisher의 판별 분석(LDA)에서 사용하는 행렬이다.

    매개변수:
        X: 데이터 (N x d)
        y: 레이블 (N,)
    반환값:
        (S_W, S_B) - 클래스 내/간 산포 행렬
    """
    classes = np.unique(y)
    d = X.shape[1]
    overall_mean = np.mean(X, axis=0)

    S_W = np.zeros((d, d))  # 클래스 내 산포 행렬 (Within-class)
    S_B = np.zeros((d, d))  # 클래스 간 산포 행렬 (Between-class)

    for c in classes:
        X_c = X[y == c]
        n_c = X_c.shape[0]
        mean_c = np.mean(X_c, axis=0)

        # 클래스 내 산포
        diff_c = X_c - mean_c
        S_W += diff_c.T @ diff_c

        # 클래스 간 산포
        diff_mean = (mean_c - overall_mean).reshape(-1, 1)
        S_B += n_c * (diff_mean @ diff_mean.T)

    return S_W, S_B


# ============================================================
# 2. 단순 메트릭 학습 알고리즘
# ============================================================

def learn_covariance_metric(X, y):
    """
    공분산 기반 마할라노비스 메트릭 학습

    클래스 내 공분산 행렬의 역행렬을 메트릭 행렬 M으로 사용한다.
    이는 각 클래스의 분산 구조를 고려한 거리를 정의한다.

    M = S_W^{-1} (클래스 내 산포 행렬의 역행렬)

    매개변수:
        X: 학습 데이터 (N x d)
        y: 레이블 (N,)
    반환값:
        M: 메트릭 행렬 (d x d)
    """
    S_W, S_B = compute_class_scatter_matrices(X, y)

    # 정규화 (수치 안정성을 위해 작은 값 추가)
    reg = 1e-4 * np.eye(S_W.shape[0])
    M = np.linalg.inv(S_W + reg)

    # 양의 반정치성 보장 (음의 고유값 제거)
    eigenvalues, eigenvectors = np.linalg.eigh(M)
    eigenvalues = np.maximum(eigenvalues, 0)
    M = eigenvectors @ np.diag(eigenvalues) @ eigenvectors.T

    return M


def learn_lda_metric(X, y, n_components=None):
    """
    LDA(선형 판별 분석) 기반 메트릭 학습

    Fisher의 기준: J(W) = W^T S_B W / (W^T S_W W) 를 최대화하는 W를 찾고,
    M = W W^T로 메트릭 행렬을 구성한다.

    매개변수:
        X: 학습 데이터 (N x d)
        y: 레이블 (N,)
        n_components: 사용할 판별 차원 수 (기본값: 클래스수 - 1)
    반환값:
        M: 메트릭 행렬 (d x d)
        W: 변환 행렬 (d x n_components)
    """
    S_W, S_B = compute_class_scatter_matrices(X, y)
    n_classes = len(np.unique(y))

    if n_components is None:
        n_components = n_classes - 1

    # S_W^{-1} S_B의 고유값 분해
    reg = 1e-4 * np.eye(S_W.shape[0])
    mat = np.linalg.inv(S_W + reg) @ S_B

    eigenvalues, eigenvectors = np.linalg.eigh(mat)

    # 가장 큰 고유값에 대응하는 고유벡터 선택
    idx = np.argsort(eigenvalues)[::-1][:n_components]
    W = eigenvectors[:, idx].real

    # 메트릭 행렬: M = W W^T
    M = W @ W.T

    return M, W


def learn_simplified_lmnn(X, y, k=3, learning_rate=1e-5, n_iterations=200, mu=0.5):
    """
    단순화된 LMNN (Large Margin Nearest Neighbor) 메트릭 학습

    Weinberger & Saul (2009)의 아이디어를 단순화하여 구현한다.
    - 목적: 같은 클래스 이웃은 가깝게, 다른 클래스 포인트는 멀리
    - 최적화: 그래디언트 하강법으로 M을 학습

    매개변수:
        X: 학습 데이터 (N x d)
        y: 레이블 (N,)
        k: 타깃 이웃 수
        learning_rate: 학습률
        n_iterations: 반복 횟수
        mu: pull/push 손실의 트레이드오프 (0~1)
    반환값:
        M: 학습된 메트릭 행렬 (d x d)
        losses: 각 반복에서의 손실값 리스트
    """
    N, d = X.shape
    M = np.eye(d)  # 단위 행렬로 초기화 (유클리드 거리로 시작)

    # 1단계: 타깃 이웃 선정 (같은 클래스 내에서 유클리드 거리 기준 K개)
    target_neighbors = {}
    for i in range(N):
        same_class_mask = y == y[i]
        same_class_indices = np.where(same_class_mask)[0]
        same_class_indices = same_class_indices[same_class_indices != i]

        if len(same_class_indices) == 0:
            target_neighbors[i] = []
            continue

        distances = np.array([np.sum((X[i] - X[j]) ** 2) for j in same_class_indices])
        k_actual = min(k, len(same_class_indices))
        nearest_idx = same_class_indices[np.argsort(distances)[:k_actual]]
        target_neighbors[i] = nearest_idx.tolist()

    losses = []

    # 2단계: 그래디언트 하강법으로 M 학습
    for iteration in range(n_iterations):
        grad = np.zeros((d, d))
        total_loss = 0.0

        # 소규모 배치로 계산 (효율성을 위해 일부 샘플만 사용)
        batch_size = min(50, N)
        batch_indices = np.random.choice(N, batch_size, replace=False)

        for i in batch_indices:
            for j in target_neighbors[i]:
                diff_ij = (X[i] - X[j]).reshape(-1, 1)
                d_ij_sq = float(diff_ij.T @ M @ diff_ij)

                # Pull 손실: 같은 클래스 이웃을 가깝게
                pull_grad = diff_ij @ diff_ij.T
                grad += (1 - mu) * pull_grad
                total_loss += (1 - mu) * d_ij_sq

                # Push 손실: 다른 클래스의 침입자를 멀리
                diff_class_mask = y != y[i]
                diff_class_indices = np.where(diff_class_mask)[0]

                # 계산 효율을 위해 가까운 다른 클래스 포인트만 고려
                for l in np.random.choice(diff_class_indices,
                                          min(5, len(diff_class_indices)),
                                          replace=False):
                    diff_il = (X[i] - X[l]).reshape(-1, 1)
                    d_il_sq = float(diff_il.T @ M @ diff_il)

                    # 힌지 손실: max(0, 1 + d_ij^2 - d_il^2)
                    margin = 1.0 + d_ij_sq - d_il_sq
                    if margin > 0:
                        push_grad = pull_grad - diff_il @ diff_il.T
                        grad += mu * push_grad
                        total_loss += mu * margin

        # M 업데이트
        M -= learning_rate * grad / batch_size

        # 양의 반정치성 보장 (투영)
        eigenvalues, eigenvectors = np.linalg.eigh(M)
        eigenvalues = np.maximum(eigenvalues, 0)
        M = eigenvectors @ np.diag(eigenvalues) @ eigenvectors.T

        losses.append(total_loss / batch_size)

        if (iteration + 1) % 50 == 0:
            print(f"    반복 {iteration+1}/{n_iterations}, 손실: {losses[-1]:.4f}")

    return M, losses


# ============================================================
# 3. 학습된 메트릭으로 KNN 분류
# ============================================================

def knn_with_metric(X_train, y_train, X_test, y_test, M, k=5):
    """
    학습된 마할라노비스 메트릭으로 KNN 분류를 수행한다.

    M = L^T L로 분해하여, 변환된 공간 Z = L X에서 유클리드 KNN을 수행한다.
    이는 원래 공간에서 마할라노비스 거리를 사용하는 것과 동일하다.

    매개변수:
        X_train, y_train: 학습 데이터
        X_test, y_test: 테스트 데이터
        M: 메트릭 행렬 (d x d)
        k: 이웃 수
    반환값:
        정확도
    """
    # M = L^T L 분해 (양의 반정치 행렬의 Cholesky-like 분해)
    eigenvalues, eigenvectors = np.linalg.eigh(M)
    eigenvalues = np.maximum(eigenvalues, 0)
    L = np.diag(np.sqrt(eigenvalues)) @ eigenvectors.T

    # 변환된 공간에서 KNN 수행
    X_train_transformed = X_train @ L.T
    X_test_transformed = X_test @ L.T

    knn = KNeighborsClassifier(n_neighbors=k, metric='euclidean')
    knn.fit(X_train_transformed, y_train)
    y_pred = knn.predict(X_test_transformed)

    return accuracy_score(y_test, y_pred), X_train_transformed, X_test_transformed


# ============================================================
# 4. 메인 실행
# ============================================================

def main():
    print("=" * 70)
    print("거리 메트릭 학습 (Distance Metric Learning)")
    print("Weinberger & Saul (2009) 아이디어 기반 구현")
    print("=" * 70)

    np.random.seed(42)

    # --------------------------------------------------------
    # 4.1 데이터 준비
    # --------------------------------------------------------
    print("\n[1] 데이터 로드 및 전처리 (Wine 데이터)")
    wine = load_wine()
    X, y = wine.data, wine.target

    print(f"  데이터 형태: {X.shape}")
    print(f"  클래스: {np.unique(y)} ({len(np.unique(y))}개)")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    print(f"  학습: {X_train_s.shape[0]}개, 테스트: {X_test_s.shape[0]}개")

    # --------------------------------------------------------
    # 4.2 기본 유클리드 KNN
    # --------------------------------------------------------
    print("\n[2] 기본 유클리드 KNN")
    print("-" * 50)

    k = 5
    knn_euc = KNeighborsClassifier(n_neighbors=k, metric='euclidean')
    knn_euc.fit(X_train_s, y_train)
    acc_euc = knn_euc.score(X_test_s, y_test)
    print(f"  유클리드 KNN (K={k}) 정확도: {acc_euc:.4f}")

    # --------------------------------------------------------
    # 4.3 공분산 기반 마할라노비스 메트릭
    # --------------------------------------------------------
    print("\n[3] 공분산 기반 마할라노비스 메트릭 학습")
    print("-" * 50)

    M_cov = learn_covariance_metric(X_train_s, y_train)
    acc_cov, X_train_cov, X_test_cov = knn_with_metric(
        X_train_s, y_train, X_test_s, y_test, M_cov, k=k
    )
    print(f"  공분산 기반 마할라노비스 KNN 정확도: {acc_cov:.4f}")

    # --------------------------------------------------------
    # 4.4 LDA 기반 메트릭
    # --------------------------------------------------------
    print("\n[4] LDA 기반 메트릭 학습")
    print("-" * 50)

    M_lda, W_lda = learn_lda_metric(X_train_s, y_train)
    acc_lda, X_train_lda, X_test_lda = knn_with_metric(
        X_train_s, y_train, X_test_s, y_test, M_lda, k=k
    )
    print(f"  LDA 기반 메트릭 KNN 정확도: {acc_lda:.4f}")

    # --------------------------------------------------------
    # 4.5 단순 LMNN 메트릭
    # --------------------------------------------------------
    print("\n[5] 단순화된 LMNN 메트릭 학습")
    print("-" * 50)

    M_lmnn, losses = learn_simplified_lmnn(
        X_train_s, y_train, k=3, learning_rate=1e-5,
        n_iterations=200, mu=0.5
    )
    acc_lmnn, X_train_lmnn, X_test_lmnn = knn_with_metric(
        X_train_s, y_train, X_test_s, y_test, M_lmnn, k=k
    )
    print(f"  LMNN 메트릭 KNN 정확도: {acc_lmnn:.4f}")

    # --------------------------------------------------------
    # 4.6 결과 비교
    # --------------------------------------------------------
    print("\n[6] 전체 결과 비교")
    print("=" * 50)

    methods = ['유클리드 (기본)', '공분산 마할라노비스', 'LDA 기반', '단순 LMNN']
    accuracies = [acc_euc, acc_cov, acc_lda, acc_lmnn]

    for method, acc in zip(methods, accuracies):
        improvement = (acc - acc_euc) / acc_euc * 100
        marker = "(기준)" if method == '유클리드 (기본)' else f"({improvement:+.1f}%)"
        print(f"  {method:25s}: {acc:.4f} {marker}")

    # --------------------------------------------------------
    # 4.7 시각화
    # --------------------------------------------------------
    print("\n[7] 시각화 생성 중...")

    fig, axes = plt.subplots(2, 2, figsize=(14, 12))

    # PCA로 2D 시각화용 데이터 준비
    pca = PCA(n_components=2)

    colors = ['steelblue', 'coral', 'forestgreen']
    class_names = wine.target_names

    # (a) 원래 공간 (유클리드)
    ax = axes[0, 0]
    X_pca = pca.fit_transform(X_train_s)
    for c in range(3):
        mask = y_train == c
        ax.scatter(X_pca[mask, 0], X_pca[mask, 1],
                   c=colors[c], alpha=0.6, s=40, label=class_names[c])
    ax.set_title(f'(a) 유클리드 공간 (PCA 2D)\n정확도: {acc_euc:.4f}', fontsize=12)
    ax.set_xlabel('PC1', fontsize=10)
    ax.set_ylabel('PC2', fontsize=10)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    # (b) 공분산 메트릭 공간
    ax = axes[0, 1]
    X_cov_pca = pca.fit_transform(X_train_cov)
    for c in range(3):
        mask = y_train == c
        ax.scatter(X_cov_pca[mask, 0], X_cov_pca[mask, 1],
                   c=colors[c], alpha=0.6, s=40, label=class_names[c])
    ax.set_title(f'(b) 공분산 마할라노비스 공간\n정확도: {acc_cov:.4f}', fontsize=12)
    ax.set_xlabel('변환된 축 1', fontsize=10)
    ax.set_ylabel('변환된 축 2', fontsize=10)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    # (c) LDA 공간
    ax = axes[1, 0]
    # LDA 변환 공간 (W^T X)
    X_lda_proj = X_train_s @ W_lda
    for c in range(3):
        mask = y_train == c
        ax.scatter(X_lda_proj[mask, 0], X_lda_proj[mask, 1],
                   c=colors[c], alpha=0.6, s=40, label=class_names[c])
    ax.set_title(f'(c) LDA 판별 공간\n정확도: {acc_lda:.4f}', fontsize=12)
    ax.set_xlabel('LD1', fontsize=10)
    ax.set_ylabel('LD2', fontsize=10)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    # (d) 정확도 비교 막대 그래프
    ax = axes[1, 1]
    bar_colors = ['steelblue', 'coral', 'forestgreen', 'purple']
    bars = ax.bar(methods, accuracies, color=bar_colors, width=0.6, alpha=0.8)
    for bar, acc in zip(bars, accuracies):
        ax.text(bar.get_x() + bar.get_width() / 2., bar.get_height() + 0.005,
                f'{acc:.4f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
    ax.set_ylabel('정확도 (Accuracy)', fontsize=12)
    ax.set_title('(d) 거리 메트릭별 KNN 정확도 비교', fontsize=12)
    ax.set_ylim(0.8, 1.05)
    ax.grid(True, alpha=0.3, axis='y')
    ax.tick_params(axis='x', rotation=15)

    plt.suptitle('거리 메트릭 학습에 따른 KNN 성능 비교\n(Wine 데이터셋)',
                 fontsize=14, fontweight='bold', y=1.01)
    plt.tight_layout()
    plt.savefig('D:/26년1학기/기계학습/6장/구현소스/03_metric_learning.png',
                dpi=150, bbox_inches='tight')
    plt.show()

    # LMNN 손실 곡선
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    ax2.plot(range(1, len(losses) + 1), losses, '-', color='purple', linewidth=2)
    ax2.set_xlabel('반복 (Iteration)', fontsize=12)
    ax2.set_ylabel('손실 (Loss)', fontsize=12)
    ax2.set_title('단순 LMNN 학습 손실 곡선', fontsize=13)
    ax2.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('D:/26년1학기/기계학습/6장/구현소스/03_lmnn_loss.png',
                dpi=150, bbox_inches='tight')
    plt.show()

    print("  그래프 저장 완료: 03_metric_learning.png, 03_lmnn_loss.png")
    print("\n" + "=" * 70)
    print("실행 완료")
    print("=" * 70)


if __name__ == "__main__":
    main()
