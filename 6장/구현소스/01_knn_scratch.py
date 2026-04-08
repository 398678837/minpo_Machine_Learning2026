# -*- coding: utf-8 -*-
"""
01_knn_scratch.py
KNN(K-Nearest Neighbors) 알고리즘을 밑바닥부터 구현하고 sklearn과 비교한다.

구현 내용:
1. 유클리드 거리 / 맨해튼 거리 기반 KNN
2. 균일 가중치 / 거리 가중치 KNN
3. 교차 검증 기반 최적 K 선택
4. sklearn KNeighborsClassifier와 성능 비교

데이터: sklearn load_wine() (3 클래스, 13 특성)
"""

import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, classification_report


# ============================================================
# 1. 거리 함수 구현
# ============================================================

def euclidean_distance(x1, x2):
    """
    유클리드 거리 계산 (L2 노름)
    d(x1, x2) = sqrt(sum((x1_i - x2_i)^2))

    매개변수:
        x1: numpy 배열, 첫 번째 데이터 포인트
        x2: numpy 배열, 두 번째 데이터 포인트
    반환값:
        float, 두 포인트 간의 유클리드 거리
    """
    return np.sqrt(np.sum((x1 - x2) ** 2))


def manhattan_distance(x1, x2):
    """
    맨해튼 거리 계산 (L1 노름)
    d(x1, x2) = sum(|x1_i - x2_i|)

    매개변수:
        x1: numpy 배열, 첫 번째 데이터 포인트
        x2: numpy 배열, 두 번째 데이터 포인트
    반환값:
        float, 두 포인트 간의 맨해튼 거리
    """
    return np.sum(np.abs(x1 - x2))


# ============================================================
# 2. KNN 분류기 구현
# ============================================================

class KNNClassifier:
    """
    K-최근접 이웃 분류기 (밑바닥 구현)

    매개변수:
        k (int): 이웃의 수 (기본값: 5)
        distance_metric (str): 거리 메트릭 ('euclidean' 또는 'manhattan')
        weights (str): 가중치 방법 ('uniform' 또는 'distance')
    """

    def __init__(self, k=5, distance_metric='euclidean', weights='uniform'):
        self.k = k
        self.weights = weights

        # 거리 함수 선택
        if distance_metric == 'euclidean':
            self.distance_func = euclidean_distance
        elif distance_metric == 'manhattan':
            self.distance_func = manhattan_distance
        else:
            raise ValueError(f"지원하지 않는 거리 메트릭: {distance_metric}")

        self.distance_metric = distance_metric
        self.X_train = None
        self.y_train = None

    def fit(self, X, y):
        """
        학습 데이터를 저장한다 (게으른 학습).
        KNN은 명시적인 학습 과정이 없으며, 데이터를 그대로 저장한다.

        매개변수:
            X: numpy 배열, 학습 특성 (N x d)
            y: numpy 배열, 학습 레이블 (N,)
        """
        self.X_train = np.array(X)
        self.y_train = np.array(y)
        return self

    def predict(self, X):
        """
        새로운 데이터에 대해 클래스를 예측한다.

        매개변수:
            X: numpy 배열, 예측할 데이터 (M x d)
        반환값:
            numpy 배열, 예측된 클래스 레이블 (M,)
        """
        X = np.array(X)
        predictions = [self._predict_single(x) for x in X]
        return np.array(predictions)

    def _predict_single(self, x):
        """
        단일 데이터 포인트에 대해 클래스를 예측한다.

        과정:
        1. 모든 학습 데이터와의 거리를 계산한다
        2. 거리가 가장 가까운 K개의 이웃을 선택한다
        3. 가중 투표로 클래스를 결정한다

        매개변수:
            x: numpy 배열, 단일 데이터 포인트 (d,)
        반환값:
            예측된 클래스 레이블
        """
        # 1단계: 모든 학습 데이터와의 거리 계산
        distances = [self.distance_func(x, x_train) for x_train in self.X_train]
        distances = np.array(distances)

        # 2단계: 가장 가까운 K개의 이웃 인덱스 추출
        k_indices = np.argsort(distances)[:self.k]
        k_labels = self.y_train[k_indices]
        k_distances = distances[k_indices]

        # 3단계: 가중 투표
        if self.weights == 'uniform':
            # 균일 가중치: 단순 다수결
            counter = Counter(k_labels)
            return counter.most_common(1)[0][0]

        elif self.weights == 'distance':
            # 거리 가중치: 거리에 반비례하는 가중치
            # 거리가 0인 경우(완전히 동일한 포인트) 처리
            weights = np.where(k_distances == 0, 1e10, 1.0 / k_distances)

            # 각 클래스별 가중치 합 계산
            class_weights = {}
            for label, weight in zip(k_labels, weights):
                class_weights[label] = class_weights.get(label, 0) + weight

            # 가중치 합이 가장 큰 클래스 반환
            return max(class_weights, key=class_weights.get)

    def score(self, X, y):
        """
        정확도를 계산한다.

        매개변수:
            X: numpy 배열, 테스트 특성
            y: numpy 배열, 테스트 레이블
        반환값:
            float, 정확도 (0.0 ~ 1.0)
        """
        predictions = self.predict(X)
        return np.mean(predictions == y)


# ============================================================
# 3. 교차 검증 기반 최적 K 탐색
# ============================================================

def find_best_k(X_train, y_train, X_val, y_val, k_range, distance_metric='euclidean', weights='uniform'):
    """
    검증 데이터를 사용하여 최적의 K값을 탐색한다.

    매개변수:
        X_train: 학습 특성
        y_train: 학습 레이블
        X_val: 검증 특성
        y_val: 검증 레이블
        k_range: K값 후보 범위 (iterable)
        distance_metric: 거리 메트릭
        weights: 가중치 방법
    반환값:
        (최적 K, 각 K에 대한 정확도 리스트)
    """
    scores = []
    for k in k_range:
        knn = KNNClassifier(k=k, distance_metric=distance_metric, weights=weights)
        knn.fit(X_train, y_train)
        acc = knn.score(X_val, y_val)
        scores.append(acc)
        print(f"  K={k:2d} -> 정확도: {acc:.4f}")

    best_k = k_range[np.argmax(scores)]
    return best_k, scores


# ============================================================
# 4. 메인 실행
# ============================================================

def main():
    print("=" * 70)
    print("KNN 분류기 밑바닥 구현 및 sklearn 비교")
    print("=" * 70)

    # --------------------------------------------------------
    # 4.1 데이터 준비
    # --------------------------------------------------------
    print("\n[1] 데이터 로드 및 전처리")
    wine = load_wine()
    X, y = wine.data, wine.target

    print(f"  데이터 형태: {X.shape}")
    print(f"  클래스 수: {len(np.unique(y))}")
    print(f"  클래스별 샘플 수: {dict(Counter(y))}")

    # 학습/테스트 분할
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # 스케일링 (KNN은 거리 기반이므로 반드시 필요)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    print(f"  학습 데이터: {X_train_scaled.shape[0]}개")
    print(f"  테스트 데이터: {X_test_scaled.shape[0]}개")

    # --------------------------------------------------------
    # 4.2 최적 K 탐색 (유클리드 + 균일 가중치)
    # --------------------------------------------------------
    print("\n[2] 최적 K 탐색 (유클리드 거리, 균일 가중치)")
    k_range = list(range(1, 21))
    best_k_euc, scores_euc = find_best_k(
        X_train_scaled, y_train, X_test_scaled, y_test,
        k_range, distance_metric='euclidean', weights='uniform'
    )
    print(f"\n  >> 최적 K (유클리드, 균일): {best_k_euc}")

    # --------------------------------------------------------
    # 4.3 다양한 설정 비교
    # --------------------------------------------------------
    print("\n[3] 다양한 KNN 설정 비교 (K={best_k_euc})")
    print("-" * 60)

    configs = [
        ("유클리드 + 균일 가중치", 'euclidean', 'uniform'),
        ("유클리드 + 거리 가중치", 'euclidean', 'distance'),
        ("맨해튼 + 균일 가중치", 'manhattan', 'uniform'),
        ("맨해튼 + 거리 가중치", 'manhattan', 'distance'),
    ]

    results = {}
    for name, metric, weight in configs:
        knn = KNNClassifier(k=best_k_euc, distance_metric=metric, weights=weight)
        knn.fit(X_train_scaled, y_train)
        acc = knn.score(X_test_scaled, y_test)
        results[name] = acc
        print(f"  {name:30s} -> 정확도: {acc:.4f}")

    # --------------------------------------------------------
    # 4.4 sklearn과 비교
    # --------------------------------------------------------
    print("\n[4] sklearn KNeighborsClassifier와 비교")
    print("-" * 60)

    # sklearn - 유클리드 + 균일
    sklearn_knn_uniform = KNeighborsClassifier(
        n_neighbors=best_k_euc, metric='euclidean', weights='uniform'
    )
    sklearn_knn_uniform.fit(X_train_scaled, y_train)
    sklearn_acc_uniform = sklearn_knn_uniform.score(X_test_scaled, y_test)

    # sklearn - 유클리드 + 거리
    sklearn_knn_distance = KNeighborsClassifier(
        n_neighbors=best_k_euc, metric='euclidean', weights='distance'
    )
    sklearn_knn_distance.fit(X_train_scaled, y_train)
    sklearn_acc_distance = sklearn_knn_distance.score(X_test_scaled, y_test)

    # 직접 구현
    my_knn_uniform = KNNClassifier(k=best_k_euc, distance_metric='euclidean', weights='uniform')
    my_knn_uniform.fit(X_train_scaled, y_train)
    my_acc_uniform = my_knn_uniform.score(X_test_scaled, y_test)

    my_knn_distance = KNNClassifier(k=best_k_euc, distance_metric='euclidean', weights='distance')
    my_knn_distance.fit(X_train_scaled, y_train)
    my_acc_distance = my_knn_distance.score(X_test_scaled, y_test)

    print(f"  {'구현':20s} {'균일 가중치':>12s} {'거리 가중치':>12s}")
    print(f"  {'직접 구현':20s} {my_acc_uniform:12.4f} {my_acc_distance:12.4f}")
    print(f"  {'sklearn':20s} {sklearn_acc_uniform:12.4f} {sklearn_acc_distance:12.4f}")

    # --------------------------------------------------------
    # 4.5 상세 분류 보고서 (최적 설정)
    # --------------------------------------------------------
    print(f"\n[5] 상세 분류 보고서 (직접 구현, K={best_k_euc}, 유클리드, 거리 가중치)")
    print("-" * 60)
    best_knn = KNNClassifier(k=best_k_euc, distance_metric='euclidean', weights='distance')
    best_knn.fit(X_train_scaled, y_train)
    y_pred = best_knn.predict(X_test_scaled)
    print(classification_report(y_test, y_pred, target_names=wine.target_names))

    # --------------------------------------------------------
    # 4.6 시각화
    # --------------------------------------------------------
    print("\n[6] 시각화 생성 중...")

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # (a) K값에 따른 정확도 (유클리드)
    axes[0].plot(k_range, scores_euc, 'o-', color='steelblue', linewidth=2, markersize=6)
    axes[0].axvline(x=best_k_euc, color='red', linestyle='--', alpha=0.7,
                    label=f'Best K={best_k_euc}')
    axes[0].set_xlabel('K (이웃 수)', fontsize=12)
    axes[0].set_ylabel('정확도 (Accuracy)', fontsize=12)
    axes[0].set_title('(a) K값에 따른 정확도 (유클리드)', fontsize=13)
    axes[0].set_xticks(k_range)
    axes[0].grid(True, alpha=0.3)
    axes[0].legend(fontsize=11)

    # (b) 맨해튼 거리 K값 탐색
    _, scores_man = find_best_k(
        X_train_scaled, y_train, X_test_scaled, y_test,
        k_range, distance_metric='manhattan', weights='uniform'
    )
    axes[1].plot(k_range, scores_euc, 'o-', color='steelblue', linewidth=2,
                 markersize=6, label='유클리드 (L2)')
    axes[1].plot(k_range, scores_man, 's--', color='coral', linewidth=2,
                 markersize=6, label='맨해튼 (L1)')
    axes[1].set_xlabel('K (이웃 수)', fontsize=12)
    axes[1].set_ylabel('정확도 (Accuracy)', fontsize=12)
    axes[1].set_title('(b) 유클리드 vs. 맨해튼 거리', fontsize=13)
    axes[1].set_xticks(k_range)
    axes[1].grid(True, alpha=0.3)
    axes[1].legend(fontsize=11)

    # (c) 다양한 설정의 정확도 비교
    config_names = list(results.keys())
    config_accs = list(results.values())
    colors = ['steelblue', 'royalblue', 'coral', 'salmon']

    bars = axes[2].barh(config_names, config_accs, color=colors, height=0.5)
    for bar, acc in zip(bars, config_accs):
        axes[2].text(acc + 0.002, bar.get_y() + bar.get_height() / 2,
                     f'{acc:.4f}', va='center', fontsize=10)
    axes[2].set_xlabel('정확도 (Accuracy)', fontsize=12)
    axes[2].set_title(f'(c) KNN 설정별 정확도 비교 (K={best_k_euc})', fontsize=13)
    axes[2].set_xlim(0.8, 1.02)
    axes[2].grid(True, alpha=0.3, axis='x')

    plt.tight_layout()
    plt.savefig('D:/26년1학기/기계학습/6장/구현소스/01_knn_results.png', dpi=150, bbox_inches='tight')
    plt.show()

    print("\n  결과 그래프가 01_knn_results.png로 저장되었다.")
    print("\n" + "=" * 70)
    print("실행 완료")
    print("=" * 70)


if __name__ == "__main__":
    main()
