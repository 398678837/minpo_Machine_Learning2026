# -*- coding: utf-8 -*-
"""
01_naive_bayes_scratch.py
가우시안 나이브 베이즈(GaussianNB)를 밑바닥부터 구현하고 sklearn과 비교한다.

구현 내용:
1. 사전확률(prior) 계산
2. 우도(likelihood) 계산 (가우시안 분포 가정)
3. 사후확률(posterior) 계산 및 분류
4. 로그 확률을 사용한 수치 안정성 처리
5. sklearn GaussianNB와 성능 비교

데이터: sklearn load_iris() (3 클래스, 4 특성)
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris, load_wine
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.naive_bayes import GaussianNB as SklearnGaussianNB
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import seaborn as sns


# ============================================================
# 1. 가우시안 나이브 베이즈 분류기 구현
# ============================================================

class GaussianNBScratch:
    """
    가우시안 나이브 베이즈 분류기 (밑바닥 구현)

    가정:
    - 각 특성은 클래스가 주어졌을 때 정규분포(가우시안)를 따른다.
    - 특성들은 클래스가 주어졌을 때 조건부 독립이다.

    분류 규칙:
    c_hat = argmax_c [ log P(c) + sum_i log P(x_i | c) ]
    여기서 P(x_i | c) = N(x_i; mu_{c,i}, sigma^2_{c,i})
    """

    def __init__(self):
        self.classes = None      # 클래스 레이블 배열
        self.priors = None       # 각 클래스의 사전확률 P(c)
        self.means = None        # 각 클래스, 각 특성의 평균 (mu)
        self.variances = None    # 각 클래스, 각 특성의 분산 (sigma^2)
        self.n_classes = 0       # 클래스 수
        self.n_features = 0      # 특성 수

    def fit(self, X, y):
        """
        학습 데이터로부터 사전확률, 평균, 분산을 추정한다.

        매개변수:
            X: numpy 배열, 학습 특성 (N x d)
            y: numpy 배열, 학습 레이블 (N,)
        """
        X = np.array(X)
        y = np.array(y)

        self.classes = np.unique(y)
        self.n_classes = len(self.classes)
        self.n_features = X.shape[1]

        # 각 클래스별 통계량 계산
        self.priors = np.zeros(self.n_classes)
        self.means = np.zeros((self.n_classes, self.n_features))
        self.variances = np.zeros((self.n_classes, self.n_features))

        for idx, c in enumerate(self.classes):
            X_c = X[y == c]  # 클래스 c에 속하는 데이터

            # 사전확률: P(c) = N_c / N
            self.priors[idx] = X_c.shape[0] / X.shape[0]

            # 평균: mu_{c,i} = (1/N_c) * sum(x_i) for class c
            self.means[idx] = X_c.mean(axis=0)

            # 분산: sigma^2_{c,i} = (1/N_c) * sum((x_i - mu)^2)
            # 수치 안정성을 위해 작은 값(epsilon) 추가
            self.variances[idx] = X_c.var(axis=0) + 1e-9

        return self

    def _gaussian_log_likelihood(self, x, mean, var):
        """
        가우시안 분포의 로그 확률밀도를 계산한다.

        log P(x | mu, sigma^2) = -0.5 * log(2*pi*sigma^2) - (x - mu)^2 / (2*sigma^2)

        매개변수:
            x: 관측값 (d,)
            mean: 평균 (d,)
            var: 분산 (d,)
        반환값:
            float, 로그 우도의 합 (모든 특성에 대해)
        """
        log_likelihood = -0.5 * np.log(2 * np.pi * var) - ((x - mean) ** 2) / (2 * var)
        return np.sum(log_likelihood)  # 독립 가정에 의한 합 (로그 공간)

    def _compute_log_posterior(self, x):
        """
        각 클래스에 대한 로그 사후확률을 계산한다 (정규화하지 않은 값).

        log P(c | x) ∝ log P(c) + sum_i log P(x_i | c)

        매개변수:
            x: 단일 데이터 포인트 (d,)
        반환값:
            numpy 배열, 각 클래스의 (비정규화) 로그 사후확률 (n_classes,)
        """
        log_posteriors = np.zeros(self.n_classes)

        for idx in range(self.n_classes):
            # log P(c)
            log_prior = np.log(self.priors[idx])

            # sum_i log P(x_i | c)
            log_likelihood = self._gaussian_log_likelihood(
                x, self.means[idx], self.variances[idx]
            )

            # log P(c | x) ∝ log P(c) + log P(x | c)
            log_posteriors[idx] = log_prior + log_likelihood

        return log_posteriors

    def predict(self, X):
        """
        새로운 데이터에 대해 클래스를 예측한다.

        각 데이터 포인트에 대해 로그 사후확률이 가장 큰 클래스를 선택한다.

        매개변수:
            X: numpy 배열, 예측할 데이터 (M x d)
        반환값:
            numpy 배열, 예측된 클래스 레이블 (M,)
        """
        X = np.array(X)
        predictions = []
        for x in X:
            log_posteriors = self._compute_log_posterior(x)
            predicted_class = self.classes[np.argmax(log_posteriors)]
            predictions.append(predicted_class)
        return np.array(predictions)

    def predict_proba(self, X):
        """
        각 클래스에 대한 사후확률을 계산한다.

        로그 사후확률을 softmax로 정규화하여 확률로 변환한다.

        매개변수:
            X: numpy 배열, 데이터 (M x d)
        반환값:
            numpy 배열, 각 클래스의 사후확률 (M x n_classes)
        """
        X = np.array(X)
        probabilities = []
        for x in X:
            log_posteriors = self._compute_log_posterior(x)

            # 수치 안정성을 위한 log-sum-exp trick
            max_log = np.max(log_posteriors)
            log_posteriors_shifted = log_posteriors - max_log
            posteriors = np.exp(log_posteriors_shifted)
            posteriors /= np.sum(posteriors)  # 정규화 (합이 1이 되도록)

            probabilities.append(posteriors)
        return np.array(probabilities)

    def score(self, X, y):
        """정확도를 계산한다."""
        predictions = self.predict(X)
        return np.mean(predictions == y)

    def get_params(self):
        """학습된 파라미터를 반환한다."""
        return {
            'classes': self.classes,
            'priors': self.priors,
            'means': self.means,
            'variances': self.variances
        }


# ============================================================
# 2. 메인 실행
# ============================================================

def main():
    print("=" * 70)
    print("가우시안 나이브 베이즈 밑바닥 구현 및 sklearn 비교")
    print("=" * 70)

    np.random.seed(42)

    # --------------------------------------------------------
    # 2.1 Iris 데이터셋 실험
    # --------------------------------------------------------
    print("\n" + "=" * 50)
    print("[실험 1] Iris 데이터셋")
    print("=" * 50)

    iris = load_iris()
    X_iris, y_iris = iris.data, iris.target

    print(f"  데이터 형태: {X_iris.shape}")
    print(f"  클래스: {iris.target_names}")

    X_train, X_test, y_train, y_test = train_test_split(
        X_iris, y_iris, test_size=0.3, random_state=42, stratify=y_iris
    )

    # 직접 구현
    my_gnb = GaussianNBScratch()
    my_gnb.fit(X_train, y_train)
    my_pred = my_gnb.predict(X_test)
    my_acc = accuracy_score(y_test, my_pred)

    # sklearn
    sk_gnb = SklearnGaussianNB()
    sk_gnb.fit(X_train, y_train)
    sk_pred = sk_gnb.predict(X_test)
    sk_acc = accuracy_score(y_test, sk_pred)

    print(f"\n  [직접 구현] 정확도: {my_acc:.4f}")
    print(f"  [sklearn]  정확도: {sk_acc:.4f}")
    print(f"  예측 일치율: {np.mean(my_pred == sk_pred):.4f}")

    # 학습된 파라미터 비교
    params = my_gnb.get_params()
    print(f"\n  --- 학습된 파라미터 ---")
    print(f"  사전확률 P(c):")
    for c, p in zip(iris.target_names, params['priors']):
        print(f"    {c}: {p:.4f}")

    print(f"\n  클래스별 평균 (일부 특성):")
    for c_idx, c_name in enumerate(iris.target_names):
        print(f"    {c_name}: sepal_l={params['means'][c_idx, 0]:.2f}, "
              f"sepal_w={params['means'][c_idx, 1]:.2f}, "
              f"petal_l={params['means'][c_idx, 2]:.2f}, "
              f"petal_w={params['means'][c_idx, 3]:.2f}")

    # 확률 추정 비교
    my_proba = my_gnb.predict_proba(X_test[:5])
    sk_proba = sk_gnb.predict_proba(X_test[:5])

    print(f"\n  --- 사후확률 비교 (처음 5개 샘플) ---")
    print(f"  {'샘플':>5s} {'직접 구현':>30s} {'sklearn':>30s}")
    for i in range(5):
        my_str = "[" + ", ".join([f"{p:.3f}" for p in my_proba[i]]) + "]"
        sk_str = "[" + ", ".join([f"{p:.3f}" for p in sk_proba[i]]) + "]"
        print(f"  {i:5d} {my_str:>30s} {sk_str:>30s}")

    # --------------------------------------------------------
    # 2.2 Wine 데이터셋 실험
    # --------------------------------------------------------
    print("\n" + "=" * 50)
    print("[실험 2] Wine 데이터셋")
    print("=" * 50)

    wine = load_wine()
    X_wine, y_wine = wine.data, wine.target

    print(f"  데이터 형태: {X_wine.shape}")
    print(f"  클래스: {wine.target_names}")

    X_train_w, X_test_w, y_train_w, y_test_w = train_test_split(
        X_wine, y_wine, test_size=0.3, random_state=42, stratify=y_wine
    )

    # 직접 구현
    my_gnb_w = GaussianNBScratch()
    my_gnb_w.fit(X_train_w, y_train_w)
    my_acc_w = my_gnb_w.score(X_test_w, y_test_w)

    # sklearn
    sk_gnb_w = SklearnGaussianNB()
    sk_gnb_w.fit(X_train_w, y_train_w)
    sk_acc_w = sk_gnb_w.score(X_test_w, y_test_w)

    print(f"\n  [직접 구현] 정확도: {my_acc_w:.4f}")
    print(f"  [sklearn]  정확도: {sk_acc_w:.4f}")

    # 상세 보고서
    my_pred_w = my_gnb_w.predict(X_test_w)
    print(f"\n  분류 보고서 (직접 구현):")
    print(classification_report(y_test_w, my_pred_w, target_names=wine.target_names))

    # --------------------------------------------------------
    # 2.3 시각화
    # --------------------------------------------------------
    print("[시각화] 결과 그래프 생성 중...")

    fig, axes = plt.subplots(2, 2, figsize=(14, 12))

    # (a) Iris - 클래스별 특성 분포 (가우시안 피팅)
    ax = axes[0, 0]
    feature_idx = 2  # petal length
    feature_name = iris.feature_names[feature_idx]

    for c_idx, c_name in enumerate(iris.target_names):
        X_c = X_train[y_train == c_idx, feature_idx]
        mu = params['means'][c_idx, feature_idx]
        sigma = np.sqrt(params['variances'][c_idx, feature_idx])

        # 히스토그램
        ax.hist(X_c, bins=15, alpha=0.3, density=True,
                label=f'{c_name} (데이터)')

        # 추정된 가우시안 분포
        x_range = np.linspace(X_c.min() - 1, X_c.max() + 1, 200)
        pdf = (1 / (np.sqrt(2 * np.pi) * sigma)) * \
              np.exp(-0.5 * ((x_range - mu) / sigma) ** 2)
        ax.plot(x_range, pdf, linewidth=2, label=f'{c_name} (N({mu:.1f}, {sigma:.1f}^2))')

    ax.set_xlabel(feature_name, fontsize=11)
    ax.set_ylabel('밀도 (Density)', fontsize=11)
    ax.set_title(f'(a) Iris: 클래스별 {feature_name} 분포\n(가우시안 피팅)', fontsize=12)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # (b) 혼동 행렬 (Iris)
    ax = axes[0, 1]
    cm_iris = confusion_matrix(y_test, my_pred)
    sns.heatmap(cm_iris, annot=True, fmt='d', cmap='Blues', ax=ax,
                xticklabels=iris.target_names, yticklabels=iris.target_names)
    ax.set_xlabel('예측 (Predicted)', fontsize=11)
    ax.set_ylabel('실제 (Actual)', fontsize=11)
    ax.set_title(f'(b) Iris 혼동 행렬\n(직접 구현, 정확도: {my_acc:.4f})', fontsize=12)

    # (c) Wine 데이터셋 - 특성별 클래스 평균 비교
    ax = axes[1, 0]
    params_w = my_gnb_w.get_params()
    n_features_show = min(8, len(wine.feature_names))
    x_pos = np.arange(n_features_show)
    width = 0.25
    colors = ['steelblue', 'coral', 'forestgreen']

    for c_idx in range(3):
        ax.bar(x_pos + c_idx * width, params_w['means'][c_idx, :n_features_show],
               width=width, color=colors[c_idx], alpha=0.7,
               label=wine.target_names[c_idx])

    ax.set_xticks(x_pos + width)
    ax.set_xticklabels([f.replace('/', '\n') for f in wine.feature_names[:n_features_show]],
                       fontsize=7, rotation=30, ha='right')
    ax.set_ylabel('평균값', fontsize=11)
    ax.set_title('(c) Wine: 클래스별 특성 평균 비교', fontsize=12)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3, axis='y')

    # (d) 정확도 비교
    ax = axes[1, 1]
    datasets = ['Iris', 'Wine']
    my_accs = [my_acc, my_acc_w]
    sk_accs = [sk_acc, sk_acc_w]
    x_pos = np.arange(len(datasets))
    width = 0.3

    bars1 = ax.bar(x_pos - width / 2, my_accs, width, color='steelblue',
                   alpha=0.8, label='직접 구현')
    bars2 = ax.bar(x_pos + width / 2, sk_accs, width, color='coral',
                   alpha=0.8, label='sklearn')

    for bar, acc in zip(bars1, my_accs):
        ax.text(bar.get_x() + bar.get_width() / 2., bar.get_height() + 0.005,
                f'{acc:.4f}', ha='center', va='bottom', fontsize=10)
    for bar, acc in zip(bars2, sk_accs):
        ax.text(bar.get_x() + bar.get_width() / 2., bar.get_height() + 0.005,
                f'{acc:.4f}', ha='center', va='bottom', fontsize=10)

    ax.set_xticks(x_pos)
    ax.set_xticklabels(datasets, fontsize=12)
    ax.set_ylabel('정확도 (Accuracy)', fontsize=11)
    ax.set_title('(d) 직접 구현 vs sklearn 정확도 비교', fontsize=12)
    ax.set_ylim(0.85, 1.02)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')

    plt.suptitle('가우시안 나이브 베이즈 밑바닥 구현 결과',
                 fontsize=14, fontweight='bold', y=1.01)
    plt.tight_layout()
    plt.savefig('D:/26년1학기/기계학습/7장/구현소스/01_gnb_scratch_results.png',
                dpi=150, bbox_inches='tight')
    plt.show()

    print("  그래프 저장 완료: 01_gnb_scratch_results.png")
    print("\n" + "=" * 70)
    print("실행 완료")
    print("=" * 70)


if __name__ == "__main__":
    main()
