"""
01_decision_tree_scratch.py
의사결정나무를 처음부터(from scratch) 구현하고 sklearn과 비교

핵심 구현 내용:
1. 지니 불순도(Gini Impurity) 계산
2. 엔트로피(Entropy) 계산
3. 정보 이득(Information Gain) 계산
4. 재귀적 트리 분할(Recursive Splitting)
5. 예측(Prediction)
6. sklearn DecisionTreeClassifier와 비교

데이터셋: Iris (sklearn 내장)
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report
from collections import Counter


# ============================================================
# 1. 불순도 측정 함수 (Impurity Measures)
# ============================================================

def gini_impurity(labels):
    """
    지니 불순도를 계산하는 함수
    Gini(t) = 1 - SUM(p_i^2)

    Parameters
    ----------
    labels : array-like
        노드에 속하는 샘플들의 레이블

    Returns
    -------
    float : 지니 불순도 값 (0 ~ 0.5 이진분류 기준)
    """
    if len(labels) == 0:
        return 0.0
    # 각 클래스의 비율 계산
    counter = Counter(labels)
    total = len(labels)
    probabilities = [count / total for count in counter.values()]
    # 지니 불순도: 1 - SUM(p_i^2)
    gini = 1.0 - sum(p ** 2 for p in probabilities)
    return gini


def entropy(labels):
    """
    엔트로피를 계산하는 함수
    Entropy(t) = -SUM(p_i * log2(p_i))

    Parameters
    ----------
    labels : array-like
        노드에 속하는 샘플들의 레이블

    Returns
    -------
    float : 엔트로피 값 (0 ~ log2(C), C는 클래스 수)
    """
    if len(labels) == 0:
        return 0.0
    counter = Counter(labels)
    total = len(labels)
    ent = 0.0
    for count in counter.values():
        p = count / total
        if p > 0:
            ent -= p * np.log2(p)
    return ent


def information_gain(parent_labels, left_labels, right_labels, criterion='gini'):
    """
    정보 이득(Information Gain)을 계산하는 함수
    IG = 부모 불순도 - 가중 평균 자식 불순도

    Parameters
    ----------
    parent_labels : array-like
        부모 노드의 레이블
    left_labels : array-like
        왼쪽 자식 노드의 레이블
    right_labels : array-like
        오른쪽 자식 노드의 레이블
    criterion : str
        불순도 기준 ('gini' 또는 'entropy')

    Returns
    -------
    float : 정보 이득 값
    """
    # 불순도 함수 선택
    impurity_fn = gini_impurity if criterion == 'gini' else entropy

    # 부모 노드의 불순도
    parent_impurity = impurity_fn(parent_labels)

    # 자식 노드의 가중 평균 불순도
    n_total = len(parent_labels)
    n_left = len(left_labels)
    n_right = len(right_labels)

    if n_left == 0 or n_right == 0:
        return 0.0

    weighted_child_impurity = (
        (n_left / n_total) * impurity_fn(left_labels) +
        (n_right / n_total) * impurity_fn(right_labels)
    )

    # 정보 이득 = 부모 불순도 - 자식 불순도
    return parent_impurity - weighted_child_impurity


# ============================================================
# 2. 불순도 시각화
# ============================================================

def plot_impurity_comparison():
    """지니 불순도와 엔트로피를 비교하는 그래프를 그린다."""
    p_values = np.linspace(0.001, 0.999, 200)

    # 이진 분류에서의 지니와 엔트로피
    gini_vals = 2 * p_values * (1 - p_values)
    entropy_vals = -(p_values * np.log2(p_values) +
                     (1 - p_values) * np.log2(1 - p_values))
    # 분류 오류
    error_vals = 1 - np.maximum(p_values, 1 - p_values)

    fig, ax = plt.subplots(1, 1, figsize=(9, 6))
    ax.plot(p_values, gini_vals, 'b-', linewidth=2.5, label='Gini Impurity')
    ax.plot(p_values, entropy_vals, 'r-', linewidth=2.5, label='Entropy (scaled)')
    ax.plot(p_values, error_vals, 'g--', linewidth=2.0, label='Classification Error')
    ax.set_xlabel('p (클래스 1의 비율)', fontsize=13)
    ax.set_ylabel('불순도 (Impurity)', fontsize=13)
    ax.set_title('지니 불순도 vs 엔트로피 vs 분류 오류 비교 (이진 분류)', fontsize=14)
    ax.legend(fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.set_xlim([0, 1])
    plt.tight_layout()
    plt.savefig('impurity_comparison.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("[시각화] 불순도 비교 그래프 저장 완료: impurity_comparison.png")


# ============================================================
# 3. 의사결정나무 노드 클래스
# ============================================================

class DecisionNode:
    """의사결정나무의 노드를 나타내는 클래스"""

    def __init__(self, feature_index=None, threshold=None,
                 left=None, right=None, value=None, info_gain=None,
                 n_samples=None, impurity=None):
        """
        Parameters
        ----------
        feature_index : int
            분할에 사용된 특성의 인덱스
        threshold : float
            분할 임계값
        left : DecisionNode
            왼쪽 자식 노드 (feature <= threshold)
        right : DecisionNode
            오른쪽 자식 노드 (feature > threshold)
        value : int
            리프 노드인 경우 예측 클래스
        info_gain : float
            이 분할의 정보 이득
        n_samples : int
            이 노드의 샘플 수
        impurity : float
            이 노드의 불순도
        """
        self.feature_index = feature_index
        self.threshold = threshold
        self.left = left
        self.right = right
        self.value = value  # 리프 노드의 예측값
        self.info_gain = info_gain
        self.n_samples = n_samples
        self.impurity = impurity


# ============================================================
# 4. 의사결정나무 분류기 (Scratch 구현)
# ============================================================

class DecisionTreeFromScratch:
    """
    의사결정나무 분류기를 처음부터 구현한 클래스

    CART(Classification and Regression Trees) 알고리즘 기반
    - 이진 분할(binary split) 사용
    - 지니 불순도 또는 엔트로피 기준 지원
    """

    def __init__(self, max_depth=None, min_samples_split=2,
                 min_samples_leaf=1, criterion='gini'):
        """
        Parameters
        ----------
        max_depth : int or None
            트리의 최대 깊이 (None이면 제한 없음)
        min_samples_split : int
            내부 노드를 분할하기 위한 최소 샘플 수
        min_samples_leaf : int
            리프 노드의 최소 샘플 수
        criterion : str
            불순도 기준 ('gini' 또는 'entropy')
        """
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.criterion = criterion
        self.root = None
        self.n_features_ = None
        self.feature_importances_ = None

    def fit(self, X, y):
        """
        훈련 데이터로 의사결정나무를 학습한다.

        Parameters
        ----------
        X : numpy.ndarray, shape (n_samples, n_features)
            훈련 데이터 특성
        y : numpy.ndarray, shape (n_samples,)
            훈련 데이터 레이블
        """
        self.n_features_ = X.shape[1]
        # 특성 중요도 초기화
        self.feature_importances_ = np.zeros(self.n_features_)
        # 재귀적으로 트리를 구축
        self.root = self._build_tree(X, y, depth=0)
        # 특성 중요도 정규화
        total_importance = np.sum(self.feature_importances_)
        if total_importance > 0:
            self.feature_importances_ /= total_importance
        return self

    def _build_tree(self, X, y, depth):
        """
        재귀적으로 트리를 구축하는 내부 함수

        Parameters
        ----------
        X : numpy.ndarray
            현재 노드의 데이터
        y : numpy.ndarray
            현재 노드의 레이블
        depth : int
            현재 깊이

        Returns
        -------
        DecisionNode : 구축된 노드
        """
        n_samples = len(y)
        n_classes = len(set(y))

        # 불순도 함수 선택
        impurity_fn = gini_impurity if self.criterion == 'gini' else entropy
        current_impurity = impurity_fn(y)

        # === 정지 조건(Stopping Criteria) 확인 ===
        # 1. 모든 샘플이 같은 클래스인 경우 (순수 노드)
        # 2. 최대 깊이에 도달한 경우
        # 3. 최소 분할 샘플 수 미달
        if (n_classes == 1 or
            (self.max_depth is not None and depth >= self.max_depth) or
            n_samples < self.min_samples_split):
            # 리프 노드 생성: 가장 빈번한 클래스를 예측값으로 설정
            leaf_value = Counter(y).most_common(1)[0][0]
            return DecisionNode(value=leaf_value, n_samples=n_samples,
                                impurity=current_impurity)

        # === 최적 분할 탐색 ===
        best_gain = -1
        best_feature = None
        best_threshold = None
        best_left_idx = None
        best_right_idx = None

        # 모든 특성에 대해 최적 분할점을 탐색
        for feature_idx in range(self.n_features_):
            feature_values = X[:, feature_idx]
            # 고유한 값을 정렬하여 후보 분할점 생성
            thresholds = np.unique(feature_values)

            for threshold in thresholds:
                # 분할 수행
                left_mask = feature_values <= threshold
                right_mask = ~left_mask

                # 최소 리프 샘플 수 확인
                if (np.sum(left_mask) < self.min_samples_leaf or
                    np.sum(right_mask) < self.min_samples_leaf):
                    continue

                # 정보 이득 계산
                left_labels = y[left_mask]
                right_labels = y[right_mask]
                gain = information_gain(y, left_labels, right_labels,
                                        self.criterion)

                # 최적 분할 갱신
                if gain > best_gain:
                    best_gain = gain
                    best_feature = feature_idx
                    best_threshold = threshold
                    best_left_idx = left_mask
                    best_right_idx = right_mask

        # 유효한 분할을 찾지 못한 경우 리프 노드 생성
        if best_gain <= 0 or best_feature is None:
            leaf_value = Counter(y).most_common(1)[0][0]
            return DecisionNode(value=leaf_value, n_samples=n_samples,
                                impurity=current_impurity)

        # 특성 중요도 업데이트 (가중 불순도 감소)
        self.feature_importances_[best_feature] += n_samples * best_gain

        # === 재귀적으로 자식 노드 구축 ===
        left_child = self._build_tree(X[best_left_idx], y[best_left_idx],
                                       depth + 1)
        right_child = self._build_tree(X[best_right_idx], y[best_right_idx],
                                        depth + 1)

        return DecisionNode(
            feature_index=best_feature,
            threshold=best_threshold,
            left=left_child,
            right=right_child,
            info_gain=best_gain,
            n_samples=n_samples,
            impurity=current_impurity
        )

    def predict(self, X):
        """
        새로운 데이터에 대해 예측을 수행한다.

        Parameters
        ----------
        X : numpy.ndarray, shape (n_samples, n_features)
            예측할 데이터

        Returns
        -------
        numpy.ndarray : 예측 레이블
        """
        return np.array([self._predict_single(x, self.root) for x in X])

    def _predict_single(self, x, node):
        """
        단일 샘플에 대해 트리를 탐색하여 예측한다.

        Parameters
        ----------
        x : numpy.ndarray
            단일 샘플의 특성 벡터
        node : DecisionNode
            현재 탐색 중인 노드

        Returns
        -------
        int : 예측 클래스
        """
        # 리프 노드에 도달하면 예측값 반환
        if node.value is not None:
            return node.value

        # 분할 조건에 따라 왼쪽/오른쪽으로 이동
        if x[node.feature_index] <= node.threshold:
            return self._predict_single(x, node.left)
        else:
            return self._predict_single(x, node.right)

    def print_tree(self, node=None, depth=0, feature_names=None):
        """
        트리 구조를 텍스트로 출력한다.

        Parameters
        ----------
        node : DecisionNode
            출력할 노드 (None이면 루트)
        depth : int
            현재 깊이 (들여쓰기용)
        feature_names : list
            특성 이름 목록
        """
        if node is None:
            node = self.root

        indent = "  " * depth

        # 리프 노드
        if node.value is not None:
            print(f"{indent}[리프] 클래스={node.value}, "
                  f"샘플수={node.n_samples}, "
                  f"불순도={node.impurity:.4f}")
            return

        # 내부 노드
        feature_name = (feature_names[node.feature_index]
                        if feature_names else f"X[{node.feature_index}]")
        print(f"{indent}[분할] {feature_name} <= {node.threshold:.4f}")
        print(f"{indent}  정보이득={node.info_gain:.4f}, "
              f"샘플수={node.n_samples}, "
              f"불순도={node.impurity:.4f}")

        # 왼쪽 자식
        print(f"{indent}  ├── 참(True):")
        self.print_tree(node.left, depth + 2, feature_names)

        # 오른쪽 자식
        print(f"{indent}  └── 거짓(False):")
        self.print_tree(node.right, depth + 2, feature_names)


# ============================================================
# 5. 메인 실행 코드
# ============================================================

if __name__ == "__main__":
    print("=" * 70)
    print("  의사결정나무 Scratch 구현 vs sklearn 비교")
    print("=" * 70)

    # --- 불순도 시각화 ---
    print("\n[1] 불순도 함수 비교 시각화")
    plot_impurity_comparison()

    # --- 불순도 계산 예시 ---
    print("\n[2] 불순도 계산 예시")
    pure_node = [0, 0, 0, 0, 0]
    mixed_node = [0, 0, 0, 0, 0, 0, 0, 1, 1, 1]
    max_impure = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1]

    for name, labels in [("순수 노드", pure_node),
                          ("혼합 노드 (7:3)", mixed_node),
                          ("최대 불순 (5:5)", max_impure)]:
        g = gini_impurity(labels)
        e = entropy(labels)
        print(f"  {name}: Gini={g:.4f}, Entropy={e:.4f}")

    # --- 데이터 로드 ---
    print("\n[3] Iris 데이터셋 로드")
    iris = load_iris()
    X, y = iris.data, iris.target
    feature_names = iris.feature_names
    target_names = iris.target_names

    print(f"  데이터 크기: {X.shape}")
    print(f"  클래스: {target_names}")
    print(f"  특성: {feature_names}")

    # --- 학습/테스트 분할 ---
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )
    print(f"\n  학습 데이터: {X_train.shape[0]}개")
    print(f"  테스트 데이터: {X_test.shape[0]}개")

    # --- Scratch 모델 학습 ---
    print("\n[4] Scratch 의사결정나무 학습")
    scratch_tree = DecisionTreeFromScratch(
        max_depth=5,
        min_samples_split=2,
        min_samples_leaf=1,
        criterion='gini'
    )
    scratch_tree.fit(X_train, y_train)

    # 트리 구조 출력
    print("\n  === 트리 구조 ===")
    scratch_tree.print_tree(feature_names=list(feature_names))

    # Scratch 모델 예측
    scratch_train_pred = scratch_tree.predict(X_train)
    scratch_test_pred = scratch_tree.predict(X_test)

    scratch_train_acc = accuracy_score(y_train, scratch_train_pred)
    scratch_test_acc = accuracy_score(y_test, scratch_test_pred)

    print(f"\n  [Scratch 모델 성능]")
    print(f"  Train Accuracy: {scratch_train_acc:.4f}")
    print(f"  Test Accuracy:  {scratch_test_acc:.4f}")

    # --- sklearn 모델 학습 ---
    print("\n[5] sklearn DecisionTreeClassifier 학습")
    sklearn_tree = DecisionTreeClassifier(
        max_depth=5,
        min_samples_split=2,
        min_samples_leaf=1,
        criterion='gini',
        random_state=42
    )
    sklearn_tree.fit(X_train, y_train)

    sklearn_train_pred = sklearn_tree.predict(X_train)
    sklearn_test_pred = sklearn_tree.predict(X_test)

    sklearn_train_acc = accuracy_score(y_train, sklearn_train_pred)
    sklearn_test_acc = accuracy_score(y_test, sklearn_test_pred)

    print(f"  [sklearn 모델 성능]")
    print(f"  Train Accuracy: {sklearn_train_acc:.4f}")
    print(f"  Test Accuracy:  {sklearn_test_acc:.4f}")

    # --- 성능 비교 ---
    print("\n[6] 모델 성능 비교")
    print(f"  {'모델':<20} | {'Train Acc':>10} | {'Test Acc':>10}")
    print(f"  {'-' * 48}")
    print(f"  {'Scratch (Gini)':<20} | {scratch_train_acc:>10.4f} | {scratch_test_acc:>10.4f}")
    print(f"  {'sklearn (Gini)':<20} | {sklearn_train_acc:>10.4f} | {sklearn_test_acc:>10.4f}")

    # Entropy 기준 비교
    scratch_entropy = DecisionTreeFromScratch(
        max_depth=5, criterion='entropy'
    )
    scratch_entropy.fit(X_train, y_train)
    ent_test_acc = accuracy_score(y_test, scratch_entropy.predict(X_test))

    sklearn_entropy = DecisionTreeClassifier(
        max_depth=5, criterion='entropy', random_state=42
    )
    sklearn_entropy.fit(X_train, y_train)
    sk_ent_test_acc = accuracy_score(y_test, sklearn_entropy.predict(X_test))

    print(f"  {'Scratch (Entropy)':<20} | {'':>10} | {ent_test_acc:>10.4f}")
    print(f"  {'sklearn (Entropy)':<20} | {'':>10} | {sk_ent_test_acc:>10.4f}")

    # --- 특성 중요도 비교 ---
    print("\n[7] 특성 중요도 비교")
    print(f"  {'특성':<25} | {'Scratch':>10} | {'sklearn':>10}")
    print(f"  {'-' * 52}")
    for i, name in enumerate(feature_names):
        print(f"  {name:<25} | {scratch_tree.feature_importances_[i]:>10.4f} | "
              f"{sklearn_tree.feature_importances_[i]:>10.4f}")

    # --- 특성 중요도 시각화 ---
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Scratch 모델 중요도
    ax = axes[0]
    sorted_idx = np.argsort(scratch_tree.feature_importances_)
    ax.barh(range(len(feature_names)),
            scratch_tree.feature_importances_[sorted_idx],
            color='steelblue')
    ax.set_yticks(range(len(feature_names)))
    ax.set_yticklabels(np.array(feature_names)[sorted_idx])
    ax.set_xlabel('중요도 (Importance)')
    ax.set_title('Scratch 모델 - 특성 중요도')

    # sklearn 모델 중요도
    ax = axes[1]
    sorted_idx_sk = np.argsort(sklearn_tree.feature_importances_)
    ax.barh(range(len(feature_names)),
            sklearn_tree.feature_importances_[sorted_idx_sk],
            color='coral')
    ax.set_yticks(range(len(feature_names)))
    ax.set_yticklabels(np.array(feature_names)[sorted_idx_sk])
    ax.set_xlabel('중요도 (Importance)')
    ax.set_title('sklearn 모델 - 특성 중요도')

    plt.tight_layout()
    plt.savefig('feature_importance_comparison.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("\n[시각화] 특성 중요도 비교 그래프 저장 완료")

    # --- 상세 분류 리포트 ---
    print("\n[8] 상세 분류 리포트 (Scratch 모델)")
    print(classification_report(
        y_test, scratch_test_pred,
        target_names=target_names
    ))

    print("\n" + "=" * 70)
    print("  실행 완료")
    print("=" * 70)
