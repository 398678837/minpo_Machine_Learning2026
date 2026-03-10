# ============================================================
# 01_bias_variance_tradeoff.py
# 편향-분산 트레이드오프 (Bias-Variance Tradeoff) 시각화
#
# 참고 논문: Pedro Domingos (2012) "A Few Useful Things to
#           Know About Machine Learning"
#
# 이 코드는 다양한 복잡도의 다항 회귀 모델을 학습하여
# 편향(Bias), 분산(Variance), 총 오류(Total Error)를
# 시각화하고, 과소적합/과적합 영역을 보여준다.
# ============================================================

import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.metrics import mean_squared_error

# --- 한글 폰트 설정 ---
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# --- 시드 고정 (재현성) ---
np.random.seed(42)


# ============================================================
# 1. 실제 함수 (True Function) 정의
# ============================================================
def true_function(x):
    """
    실제 데이터 생성 함수 (ground truth).
    비선형 관계를 가진 함수로, 다항 회귀의 적합성을 테스트하기에 적합하다.
    """
    return np.sin(1.5 * np.pi * x)


# ============================================================
# 2. 합성 데이터 생성 함수
# ============================================================
def generate_data(n_samples=30, noise_std=0.3):
    """
    합성 데이터 생성.

    Parameters
    ----------
    n_samples : int
        생성할 데이터 포인트 수
    noise_std : float
        가우시안 노이즈의 표준편차

    Returns
    -------
    X : ndarray, shape (n_samples,)
        입력 변수
    y : ndarray, shape (n_samples,)
        출력 변수 (실제 함수 + 노이즈)
    """
    X = np.sort(np.random.uniform(0, 1, n_samples))
    y = true_function(X) + np.random.normal(0, noise_std, n_samples)
    return X, y


# ============================================================
# 3. 편향-분산 계산
# ============================================================
def compute_bias_variance(degrees, n_datasets=200, n_samples=30,
                          noise_std=0.3, n_test=100):
    """
    여러 다항식 차수에 대해 편향^2, 분산, 총 오류를 계산한다.

    원리:
    - 동일한 분포에서 n_datasets개의 학습 데이터셋을 생성
    - 각 데이터셋으로 모델을 학습
    - 고정된 테스트 포인트에서 예측값의 편향과 분산을 계산

    편향-분산 분해 (Bias-Variance Decomposition):
        E[(y - f_hat(x))^2] = Bias^2(f_hat(x)) + Var(f_hat(x)) + sigma^2

    Parameters
    ----------
    degrees : list of int
        테스트할 다항식 차수 리스트
    n_datasets : int
        반복 생성할 데이터셋 수 (평균을 내기 위함)
    n_samples : int
        각 데이터셋의 샘플 수
    noise_std : float
        노이즈 표준편차
    n_test : int
        테스트 포인트 수

    Returns
    -------
    bias_squared : dict
        각 차수별 평균 편향^2
    variance : dict
        각 차수별 평균 분산
    total_error : dict
        각 차수별 평균 총 오류 (MSE)
    """
    # 고정된 테스트 포인트
    X_test = np.linspace(0, 1, n_test)
    y_true = true_function(X_test)
    noise_var = noise_std ** 2  # 비가약 오류 (irreducible error)

    bias_squared = {}
    variance = {}
    total_error = {}

    for degree in degrees:
        # 각 데이터셋에서의 예측값을 저장할 배열
        # shape: (n_datasets, n_test)
        predictions = np.zeros((n_datasets, n_test))

        for i in range(n_datasets):
            # 새로운 학습 데이터 생성
            X_train, y_train = generate_data(n_samples, noise_std)

            # 다항 회귀 모델 학습
            model = make_pipeline(
                PolynomialFeatures(degree, include_bias=True),
                LinearRegression()
            )
            model.fit(X_train.reshape(-1, 1), y_train)

            # 테스트 포인트에서 예측
            predictions[i, :] = model.predict(X_test.reshape(-1, 1))

        # 편향^2 계산: (평균 예측 - 실제값)^2의 평균
        mean_prediction = predictions.mean(axis=0)  # 각 테스트 포인트에서의 평균 예측
        bias_sq = np.mean((mean_prediction - y_true) ** 2)

        # 분산 계산: 예측값의 분산의 평균
        var = np.mean(predictions.var(axis=0))

        # 총 오류 (MSE): 편향^2 + 분산 + 노이즈
        total = bias_sq + var + noise_var

        bias_squared[degree] = bias_sq
        variance[degree] = var
        total_error[degree] = total

        print(f"  차수 {degree:2d}: Bias²={bias_sq:.4f}, "
              f"Var={var:.4f}, Noise={noise_var:.4f}, "
              f"Total={total:.4f}")

    return bias_squared, variance, total_error


# ============================================================
# 4. 시각화 1: 다양한 복잡도의 모델 적합 결과
# ============================================================
def plot_model_fits(degrees):
    """
    다양한 차수의 다항 회귀 적합 결과를 시각화한다.
    과소적합(저차수)과 과적합(고차수)을 직관적으로 보여준다.
    """
    X_train, y_train = generate_data(n_samples=30, noise_std=0.3)
    X_plot = np.linspace(0, 1, 200)

    fig, axes = plt.subplots(2, 3, figsize=(18, 11))
    axes = axes.flatten()

    for idx, degree in enumerate(degrees):
        ax = axes[idx]

        # 모델 학습
        model = make_pipeline(
            PolynomialFeatures(degree, include_bias=True),
            LinearRegression()
        )
        model.fit(X_train.reshape(-1, 1), y_train)
        y_pred = model.predict(X_plot.reshape(-1, 1))

        # 학습 MSE 계산
        train_pred = model.predict(X_train.reshape(-1, 1))
        train_mse = mean_squared_error(y_train, train_pred)

        # 시각화
        ax.scatter(X_train, y_train, color='steelblue', s=30,
                   alpha=0.7, label='학습 데이터', zorder=3)
        ax.plot(X_plot, true_function(X_plot), 'g--', linewidth=2,
                label='실제 함수 $f(x)$', alpha=0.7)
        ax.plot(X_plot, y_pred, 'r-', linewidth=2,
                label=f'다항식 (차수={degree})')

        # 상태 표시
        if degree <= 2:
            status = "과소적합 (Underfitting)"
            color = '#FF6B6B'
        elif degree <= 5:
            status = "적절한 적합 (Good Fit)"
            color = '#51CF66'
        else:
            status = "과적합 (Overfitting)"
            color = '#FF6B6B'

        ax.set_title(f'다항식 차수 = {degree}\n'
                     f'{status}\n학습 MSE = {train_mse:.4f}',
                     fontsize=11, fontweight='bold',
                     color=color if degree <= 2 or degree > 5 else 'black')
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_ylim(-2, 2)
        ax.legend(fontsize=8, loc='upper right')
        ax.grid(True, alpha=0.3)

    # 마지막 subplot에 설명 추가
    ax_info = axes[5]
    ax_info.axis('off')
    info_text = (
        "편향-분산 트레이드오프 (Bias-Variance Tradeoff)\n\n"
        "모델 복잡도가 증가하면:\n"
        "  - 편향(Bias) 감소: 더 유연한 함수 표현 가능\n"
        "  - 분산(Variance) 증가: 데이터에 민감해짐\n\n"
        "최적의 모델 복잡도:\n"
        "  편향²과 분산의 합이 최소인 지점\n\n"
        "Domingos (2012):\n"
        "  'Overfitting has many faces'\n"
        "  '과적합은 다양한 형태로 나타난다'"
    )
    ax_info.text(0.1, 0.5, info_text, transform=ax_info.transAxes,
                 fontsize=12, verticalalignment='center',
                 bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow',
                           alpha=0.8),
                 family='Malgun Gothic')

    plt.suptitle('다항 회귀의 모델 복잡도에 따른 적합 결과',
                 fontsize=16, fontweight='bold', y=1.01)
    plt.tight_layout()
    plt.savefig('01_model_fits.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("[저장 완료] 01_model_fits.png")


# ============================================================
# 5. 시각화 2: 편향-분산 트레이드오프 곡선
# ============================================================
def plot_bias_variance_tradeoff(degrees, bias_sq, var, total):
    """
    편향^2, 분산, 총 오류를 모델 복잡도(다항식 차수)에 따라 플롯한다.
    """
    deg_list = sorted(degrees)
    bias_vals = [bias_sq[d] for d in deg_list]
    var_vals = [var[d] for d in deg_list]
    total_vals = [total[d] for d in deg_list]
    noise_val = 0.3 ** 2  # 비가약 오류

    fig, ax = plt.subplots(figsize=(10, 7))

    ax.plot(deg_list, bias_vals, 'b-o', linewidth=2, markersize=8,
            label='편향² (Bias²)', zorder=3)
    ax.plot(deg_list, var_vals, 'r-s', linewidth=2, markersize=8,
            label='분산 (Variance)', zorder=3)
    ax.plot(deg_list, total_vals, 'k-^', linewidth=2.5, markersize=9,
            label='총 오류 (Total Error)', zorder=3)
    ax.axhline(y=noise_val, color='gray', linestyle='--', linewidth=1.5,
               label=f'비가약 오류 (σ²={noise_val:.2f})', alpha=0.7)

    # 최적 지점 표시
    optimal_degree = deg_list[np.argmin(total_vals)]
    optimal_error = min(total_vals)
    ax.axvline(x=optimal_degree, color='green', linestyle=':', linewidth=2,
               alpha=0.7, label=f'최적 복잡도 (차수={optimal_degree})')
    ax.scatter([optimal_degree], [optimal_error], color='green', s=200,
               zorder=5, marker='*', edgecolor='black', linewidth=1)

    # 영역 표시
    ax.axvspan(deg_list[0], optimal_degree, alpha=0.08, color='blue',
               label='과소적합 영역')
    ax.axvspan(optimal_degree, deg_list[-1], alpha=0.08, color='red',
               label='과적합 영역')

    ax.set_xlabel('모델 복잡도 (다항식 차수)', fontsize=13)
    ax.set_ylabel('오류 (Error)', fontsize=13)
    ax.set_title('편향-분산 트레이드오프 (Bias-Variance Tradeoff)\n'
                 'Domingos (2012) - Overfitting Has Many Faces',
                 fontsize=14, fontweight='bold')
    ax.legend(fontsize=10, loc='upper center',
              bbox_to_anchor=(0.5, -0.12), ncol=3)
    ax.set_xticks(deg_list)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(bottom=0)

    plt.tight_layout()
    plt.savefig('01_bias_variance_tradeoff.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("[저장 완료] 01_bias_variance_tradeoff.png")


# ============================================================
# 6. 시각화 3: 여러 데이터셋에서의 예측 불안정성 비교
# ============================================================
def plot_prediction_variability():
    """
    저복잡도 vs 고복잡도 모델에서
    여러 데이터셋에 대한 예측의 변동(분산)을 시각화한다.
    """
    fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))
    X_plot = np.linspace(0, 1, 200)

    model_configs = [
        (1, '차수 1 (높은 편향, 낮은 분산)'),
        (5, '차수 5 (적절한 균형)'),
        (15, '차수 15 (낮은 편향, 높은 분산)')
    ]

    for ax, (degree, title) in zip(axes, model_configs):
        # 여러 데이터셋으로 학습한 결과를 겹쳐 그리기
        for i in range(30):
            X_train, y_train = generate_data(n_samples=30, noise_std=0.3)
            model = make_pipeline(
                PolynomialFeatures(degree, include_bias=True),
                LinearRegression()
            )
            model.fit(X_train.reshape(-1, 1), y_train)
            y_pred = model.predict(X_plot.reshape(-1, 1))

            # 예측값 클리핑 (시각화를 위해 극단값 제한)
            y_pred = np.clip(y_pred, -3, 3)
            ax.plot(X_plot, y_pred, 'r-', alpha=0.15, linewidth=0.8)

        ax.plot(X_plot, true_function(X_plot), 'g-', linewidth=3,
                label='실제 함수', zorder=5)
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_ylim(-3, 3)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)

    plt.suptitle('모델 복잡도에 따른 예측의 변동성 (빨간 선 = 서로 다른 학습 데이터의 결과)',
                 fontsize=13, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig('01_prediction_variability.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("[저장 완료] 01_prediction_variability.png")


# ============================================================
# 메인 실행
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("편향-분산 트레이드오프 (Bias-Variance Tradeoff) 시뮬레이션")
    print("참고: Domingos (2012) 'A Few Useful Things to Know")
    print("      About Machine Learning'")
    print("=" * 60)

    # 테스트할 다항식 차수 목록
    degrees = [1, 3, 5, 10, 15]

    # --- 시각화 1: 모델 적합 결과 ---
    print("\n[1/3] 다양한 복잡도의 모델 적합 결과 시각화...")
    plot_model_fits(degrees)

    # --- 편향-분산 계산 ---
    # 더 세밀한 차수 범위로 계산
    fine_degrees = list(range(1, 16))
    print(f"\n[2/3] 편향-분산 계산 (차수 1~15, 200개 데이터셋 반복)...")
    bias_sq, var, total = compute_bias_variance(
        fine_degrees, n_datasets=200, n_samples=30, noise_std=0.3
    )

    # --- 시각화 2: 편향-분산 트레이드오프 곡선 ---
    print("\n편향-분산 트레이드오프 곡선 시각화...")
    plot_bias_variance_tradeoff(fine_degrees, bias_sq, var, total)

    # --- 시각화 3: 예측 변동성 비교 ---
    print("\n[3/3] 예측 변동성 비교 시각화...")
    plot_prediction_variability()

    # --- 결과 요약 ---
    print("\n" + "=" * 60)
    print("실행 결과 요약")
    print("=" * 60)
    optimal_degree = min(total, key=total.get)
    print(f"\n최적 다항식 차수: {optimal_degree}")
    print(f"  - Bias²: {bias_sq[optimal_degree]:.4f}")
    print(f"  - Variance: {var[optimal_degree]:.4f}")
    print(f"  - Total Error: {total[optimal_degree]:.4f}")
    print(f"\n핵심 교훈 (Domingos, 2012):")
    print(f"  1. 과적합은 다양한 형태로 나타난다")
    print(f"  2. 일반화 성능이 학습 성능보다 중요하다")
    print(f"  3. 모델 복잡도의 균형이 핵심이다")
    print(f"\n[완료] 생성된 파일:")
    print(f"  - 01_model_fits.png")
    print(f"  - 01_bias_variance_tradeoff.png")
    print(f"  - 01_prediction_variability.png")
