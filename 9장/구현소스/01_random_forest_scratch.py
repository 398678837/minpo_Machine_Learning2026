"""
01_random_forest_scratch.py
랜덤 포레스트를 처음부터(from scratch) 구현하고 sklearn과 비교

핵심 구현 내용:
1. 부트스트랩 샘플링 (Bootstrap Sampling)
2. 랜덤 특성 선택 (Random Feature Selection)
3. 의사결정나무 구축 (기본 CART)
4. 다수결 투표 / 평균 (Majority Voting / Averaging)
5. OOB 오류 추정 (Out-of-Bag Error Estimation)
6. sklearn RandomForestClassifier와 비교

데이터셋: Iris (sklearn 내장)
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from collections import Counter


# ============================================================
# 1. 의사결정나무 노드 및 트리 (기본 구현)
# ============================================================

class TreeNode:
    """의사결정나무의 노드"""
    def __init__(self, feature_idx=None, threshold=None,
                 left=None, right=None, value=None):
        self.feature_idx = feature_idx
        self.threshold = threshold
        self.left = left
        self.right = right
        self.value = value  # 리프 노드의 예측값


class SimpleDecisionTree:
    """
    간단한 의사결정나무 분류기
    - 지니 불순도 기반
    - 이진 분할만 지원
    - 랜덤 특성 선택 지원 (max_features 파라미터)
    """

    def __init__(self, max_depth=None, min_samples_split=2,
                 max_features=None):
        """
        Parameters
        ----------
        max_depth : int or None
            최대 트리 깊이
        min_samples_split : int
            분할 최소 샘플 수
        max_features : int or None
            각 분할에서 고려할 최대 특성 수 (랜덤 포레스트의 핵심)
        """
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.max_features = max_features
        self.root = None

    def _gini(self, y):
        """지니 불순도 계산"""
        if len(y) == 0:
            return 0.0
        counter = Counter(y)
        total = len(y)
        return 1.0 - sum((c / total) ** 2 for c in counter.values())

    def _best_split(self, X, y, feature_indices):
        """
        주어진 특성 후보에서 최적 분할을 찾는다.

        Parameters
        ----------
        X : numpy.ndarray
            데이터
        y : numpy.ndarray
            레이블
        feature_indices : list
            고려할 특성 인덱스 (랜덤 선택된 부분집합)

        Returns
        -------
        tuple : (best_feature, best_threshold, best_gain)
        """
        best_gain = -1
        best_feature = None
        best_threshold = None
        parent_gini = self._gini(y)
        n = len(y)

        for feat_idx in feature_indices:
            thresholds = np.unique(X[:, feat_idx])
            for threshold in thresholds:
                left_mask = X[:, feat_idx] <= threshold
                right_mask = ~left_mask

                n_left = np.sum(left_mask)
                n_right = np.sum(right_mask)

                if n_left == 0 or n_right == 0:
                    continue

                # 가중 지니 불순도 감소 (정보 이득)
                gain = parent_gini - (
                    (n_left / n) * self._gini(y[left_mask]) +
                    (n_right / n) * self._gini(y[right_mask])
                )

                if gain > best_gain:
                    best_gain = gain
                    best_feature = feat_idx
                    best_threshold = threshold

        return best_feature, best_threshold, best_gain

    def _build_tree(self, X, y, depth):
        """재귀적으로 트리를 구축한다."""
        n_samples, n_features = X.shape
        n_classes = len(set(y))

        # 정지 조건
        if (n_classes == 1 or
            (self.max_depth is not None and depth >= self.max_depth) or
            n_samples < self.min_samples_split):
            return TreeNode(value=Counter(y).most_common(1)[0][0])

        # 랜덤 특성 선택 (핵심: 랜덤 포레스트의 "랜덤")
        if self.max_features is not None:
            feature_indices = np.random.choice(
                n_features, size=min(self.max_features, n_features),
                replace=False
            )
        else:
            feature_indices = np.arange(n_features)

        # 최적 분할 탐색
        best_feat, best_thresh, best_gain = self._best_split(
            X, y, feature_indices
        )

        if best_gain <= 0 or best_feat is None:
            return TreeNode(value=Counter(y).most_common(1)[0][0])

        # 분할 수행
        left_mask = X[:, best_feat] <= best_thresh
        right_mask = ~left_mask

        left_child = self._build_tree(X[left_mask], y[left_mask], depth + 1)
        right_child = self._build_tree(X[right_mask], y[right_mask], depth + 1)

        return TreeNode(
            feature_idx=best_feat,
            threshold=best_thresh,
            left=left_child,
            right=right_child
        )

    def fit(self, X, y):
        """트리를 학습한다."""
        self.root = self._build_tree(X, y, depth=0)
        return self

    def _predict_one(self, x, node):
        """단일 샘플 예측"""
        if node.value is not None:
            return node.value
        if x[node.feature_idx] <= node.threshold:
            return self._predict_one(x, node.left)
        else:
            return self._predict_one(x, node.right)

    def predict(self, X):
        """배치 예측"""
        return np.array([self._predict_one(x, self.root) for x in X])


# ============================================================
# 2. 랜덤 포레스트 (Scratch 구현)
# ============================================================

class RandomForestFromScratch:
    """
    랜덤 포레스트 분류기를 처음부터 구현한 클래스

    Breiman (2001)의 알고리즘:
    1. 부트스트랩 샘플링
    2. 각 노드에서 랜덤 특성 선택
    3. 다수결 투표로 예측
    4. OOB 오류 추정
    """

    def __init__(self, n_estimators=100, max_depth=None,
                 min_samples_split=2, max_features='sqrt',
                 random_state=None):
        """
        Parameters
        ----------
        n_estimators : int
            트리의 수
        max_depth : int or None
            각 트리의 최대 깊이
        min_samples_split : int
            분할 최소 샘플 수
        max_features : str or int
            'sqrt': sqrt(n_features), 'log2': log2(n_features), int: 직접 지정
        random_state : int or None
            랜덤 시드
        """
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.max_features = max_features
        self.random_state = random_state
        self.trees = []
        self.oob_indices = []  # 각 트리의 OOB 샘플 인덱스
        self.oob_score_ = None
        self.feature_importances_ = None

    def _get_max_features(self, n_features):
        """max_features 값을 계산한다."""
        if self.max_features == 'sqrt':
            return int(np.sqrt(n_features))
        elif self.max_features == 'log2':
            return int(np.log2(n_features))
        elif isinstance(self.max_features, int):
            return self.max_features
        else:
            return n_features

    def fit(self, X, y):
        """
        랜덤 포레스트를 학습한다.

        Parameters
        ----------
        X : numpy.ndarray, shape (n_samples, n_features)
        y : numpy.ndarray, shape (n_samples,)
        """
        if self.random_state is not None:
            np.random.seed(self.random_state)

        n_samples, n_features = X.shape
        max_feat = self._get_max_features(n_features)

        self.trees = []
        self.oob_indices = []

        print(f"  랜덤 포레스트 학습 시작 (트리 {self.n_estimators}개, "
              f"max_features={max_feat})")

        for i in range(self.n_estimators):
            # 1단계: 부트스트랩 샘플링 (중복 허용 추출)
            bootstrap_idx = np.random.choice(
                n_samples, size=n_samples, replace=True
            )
            # OOB 샘플 (부트스트랩에 포함되지 않은 샘플)
            oob_idx = np.array(list(set(range(n_samples)) - set(bootstrap_idx)))
            self.oob_indices.append(oob_idx)

            X_boot = X[bootstrap_idx]
            y_boot = y[bootstrap_idx]

            # 2단계: 트리 학습 (랜덤 특성 선택 포함)
            tree = SimpleDecisionTree(
                max_depth=self.max_depth,
                min_samples_split=self.min_samples_split,
                max_features=max_feat
            )
            tree.fit(X_boot, y_boot)
            self.trees.append(tree)

            # 진행 상황 출력 (10개마다)
            if (i + 1) % (self.n_estimators // 5) == 0:
                print(f"    ... {i + 1}/{self.n_estimators} 트리 완료")

        # OOB 오류 추정
        self._compute_oob_score(X, y)

        print(f"  학습 완료! OOB Score: {self.oob_score_:.4f}")
        return self

    def _compute_oob_score(self, X, y):
        """
        OOB(Out-of-Bag) 오류를 추정한다.

        각 샘플에 대해, 해당 샘플이 OOB인 트리들의 다수결 투표로 예측하고,
        실제 레이블과 비교하여 오류율을 계산한다.
        """
        n_samples = len(y)
        oob_predictions = {}  # {샘플 인덱스: [트리별 예측 리스트]}

        for tree_idx, (tree, oob_idx) in enumerate(
            zip(self.trees, self.oob_indices)
        ):
            if len(oob_idx) == 0:
                continue
            preds = tree.predict(X[oob_idx])
            for sample_idx, pred in zip(oob_idx, preds):
                if sample_idx not in oob_predictions:
                    oob_predictions[sample_idx] = []
                oob_predictions[sample_idx].append(pred)

        # 다수결 투표로 OOB 예측
        correct = 0
        total = 0
        for sample_idx, preds in oob_predictions.items():
            majority_vote = Counter(preds).most_common(1)[0][0]
            if majority_vote == y[sample_idx]:
                correct += 1
            total += 1

        self.oob_score_ = correct / total if total > 0 else 0.0

    def predict(self, X):
        """
        다수결 투표로 예측한다.

        Parameters
        ----------
        X : numpy.ndarray

        Returns
        -------
        numpy.ndarray : 예측 레이블
        """
        # 각 트리의 예측을 수집
        all_predictions = np.array([tree.predict(X) for tree in self.trees])

        # 다수결 투표
        final_predictions = np.zeros(X.shape[0], dtype=int)
        for j in range(X.shape[0]):
            votes = all_predictions[:, j]
            final_predictions[j] = Counter(votes).most_common(1)[0][0]

        return final_predictions

    def predict_proba(self, X):
        """
        클래스 확률(투표 비율)을 반환한다.

        Parameters
        ----------
        X : numpy.ndarray

        Returns
        -------
        numpy.ndarray : 클래스별 투표 비율
        """
        all_predictions = np.array([tree.predict(X) for tree in self.trees])
        classes = np.unique(all_predictions)
        n_classes = len(classes)

        probas = np.zeros((X.shape[0], n_classes))
        for j in range(X.shape[0]):
            votes = Counter(all_predictions[:, j])
            for c_idx, c in enumerate(classes):
                probas[j, c_idx] = votes.get(c, 0) / self.n_estimators

        return probas


# ============================================================
# 3. 메인 실행 코드
# ============================================================

if __name__ == "__main__":
    print("=" * 70)
    print("  랜덤 포레스트 Scratch 구현 vs sklearn 비교")
    print("=" * 70)

    # --- 데이터 로드 ---
    iris = load_iris()
    X, y = iris.data, iris.target
    feature_names = iris.feature_names
    target_names = iris.target_names

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )

    print(f"\n[데이터 정보]")
    print(f"  학습: {X_train.shape[0]}개, 테스트: {X_test.shape[0]}개")
    print(f"  특성: {X_train.shape[1]}개, 클래스: {len(target_names)}개")

    # --- Scratch 랜덤 포레스트 학습 ---
    print(f"\n[1] Scratch 랜덤 포레스트 학습")
    rf_scratch = RandomForestFromScratch(
        n_estimators=100,
        max_depth=10,
        max_features='sqrt',
        random_state=42
    )
    rf_scratch.fit(X_train, y_train)

    scratch_train_pred = rf_scratch.predict(X_train)
    scratch_test_pred = rf_scratch.predict(X_test)

    scratch_train_acc = accuracy_score(y_train, scratch_train_pred)
    scratch_test_acc = accuracy_score(y_test, scratch_test_pred)

    print(f"\n  [Scratch RF 성능]")
    print(f"  Train Accuracy: {scratch_train_acc:.4f}")
    print(f"  Test Accuracy:  {scratch_test_acc:.4f}")
    print(f"  OOB Score:      {rf_scratch.oob_score_:.4f}")

    # --- sklearn 랜덤 포레스트 학습 ---
    print(f"\n[2] sklearn RandomForestClassifier 학습")
    rf_sklearn = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        max_features='sqrt',
        oob_score=True,
        random_state=42,
        n_jobs=-1
    )
    rf_sklearn.fit(X_train, y_train)

    sk_train_pred = rf_sklearn.predict(X_train)
    sk_test_pred = rf_sklearn.predict(X_test)

    sk_train_acc = accuracy_score(y_train, sk_train_pred)
    sk_test_acc = accuracy_score(y_test, sk_test_pred)

    print(f"  [sklearn RF 성능]")
    print(f"  Train Accuracy: {sk_train_acc:.4f}")
    print(f"  Test Accuracy:  {sk_test_acc:.4f}")
    print(f"  OOB Score:      {rf_sklearn.oob_score_:.4f}")

    # --- 성능 비교 ---
    print(f"\n[3] 모델 성능 비교")
    print(f"  {'모델':<25} | {'Train':>8} | {'Test':>8} | {'OOB':>8}")
    print(f"  {'-' * 55}")
    print(f"  {'Scratch RF (100 trees)':<25} | {scratch_train_acc:>8.4f} | "
          f"{scratch_test_acc:>8.4f} | {rf_scratch.oob_score_:>8.4f}")
    print(f"  {'sklearn RF (100 trees)':<25} | {sk_train_acc:>8.4f} | "
          f"{sk_test_acc:>8.4f} | {rf_sklearn.oob_score_:>8.4f}")

    # --- OOB 오류 수렴 분석 ---
    print(f"\n[4] OOB 오류 수렴 분석 (트리 수에 따른 변화)")

    tree_counts = [5, 10, 20, 50, 100, 200, 500]
    oob_scores = []
    test_scores_by_n = []

    for n_trees in tree_counts:
        rf_temp = RandomForestClassifier(
            n_estimators=n_trees, max_depth=10,
            max_features='sqrt', oob_score=True,
            random_state=42, n_jobs=-1
        )
        rf_temp.fit(X_train, y_train)
        oob_scores.append(rf_temp.oob_score_)
        test_scores_by_n.append(
            accuracy_score(y_test, rf_temp.predict(X_test))
        )
        print(f"  n_estimators={n_trees:>4}: OOB={rf_temp.oob_score_:.4f}, "
              f"Test={test_scores_by_n[-1]:.4f}")

    # OOB 수렴 시각화
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(tree_counts, oob_scores, 'b-o', linewidth=2, markersize=6,
            label='OOB Score')
    ax.plot(tree_counts, test_scores_by_n, 'r-s', linewidth=2, markersize=6,
            label='Test Accuracy')
    ax.set_xlabel('트리 수 (n_estimators)', fontsize=12)
    ax.set_ylabel('정확도', fontsize=12)
    ax.set_title('트리 수에 따른 OOB Score와 Test Accuracy 수렴', fontsize=14)
    ax.legend(fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.set_xscale('log')
    plt.tight_layout()
    plt.savefig('rf_oob_convergence.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("  [시각화] OOB 수렴 그래프 저장 완료")

    # --- 분류 리포트 ---
    print(f"\n[5] 상세 분류 리포트 (Scratch RF)")
    print(classification_report(
        y_test, scratch_test_pred, target_names=target_names
    ))

    print("\n" + "=" * 70)
    print("  실행 완료")
    print("=" * 70)
