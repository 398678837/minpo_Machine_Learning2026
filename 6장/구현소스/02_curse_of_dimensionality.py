# -*- coding: utf-8 -*-
"""
02_curse_of_dimensionality.py
Beyer et al. (1999) "When Is Nearest Neighbor Meaningful?" 논문의 핵심 결과를 실험적으로 재현한다.

실험 내용:
1. 차원이 증가할 때 Dmax/Dmin 비율이 1로 수렴하는 현상(거리 집중) 시연
2. 다양한 분포(균일분포, 가우시안분포)에서의 거리 집중 비교
3. L1(맨해튼) vs L2(유클리드) 노름에서의 거리 집중 비교
4. 고차원에서 KNN 분류 성능의 저하 시연
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler


# ============================================================
# 1. 거리 집중 현상 (Distance Concentration) 실험
# ============================================================

def compute_distance_ratio(n_samples=500, dimensions=None, n_trials=20,
                           distribution='uniform', p_norm=2):
    """
    다양한 차원에서 Dmax/Dmin 비율을 계산한다.

    Beyer et al. (1999)의 핵심 결과:
    차원 d -> 무한대일 때, (Dmax - Dmin) / Dmin -> 0
    즉, Dmax/Dmin -> 1

    매개변수:
        n_samples: 데이터 포인트 수
        dimensions: 실험할 차원 리스트
        n_trials: 각 차원에서의 반복 실험 횟수
        distribution: 데이터 분포 ('uniform' 또는 'gaussian')
        p_norm: Lp 노름의 p 값 (1: 맨해튼, 2: 유클리드)
    반환값:
        (평균 비율 리스트, 표준편차 리스트)
    """
    if dimensions is None:
        dimensions = [2, 5, 10, 20, 50, 100, 200, 500, 1000]

    mean_ratios = []
    std_ratios = []

    for d in dimensions:
        ratios = []
        for _ in range(n_trials):
            # 데이터 생성
            if distribution == 'uniform':
                data = np.random.uniform(0, 1, size=(n_samples, d))
            elif distribution == 'gaussian':
                data = np.random.randn(n_samples, d)
            else:
                raise ValueError(f"지원하지 않는 분포: {distribution}")

            # 쿼리 포인트 (원점 사용)
            query = np.zeros(d)

            # 모든 데이터 포인트까지의 Lp 거리 계산
            diff = data - query
            distances = np.sum(np.abs(diff) ** p_norm, axis=1) ** (1.0 / p_norm)

            # Dmax / Dmin 비율 계산
            d_min = np.min(distances)
            d_max = np.max(distances)

            if d_min > 0:
                ratio = d_max / d_min
            else:
                ratio = np.inf

            ratios.append(ratio)

        mean_ratios.append(np.mean(ratios))
        std_ratios.append(np.std(ratios))

    return mean_ratios, std_ratios


def compute_relative_contrast(n_samples=500, dimensions=None, n_trials=20,
                               distribution='uniform', p_norm=2):
    """
    상대적 거리 대비(Relative Distance Contrast)를 계산한다.
    RDC = (Dmax - Dmin) / Dmin

    Beyer et al.의 정의에 따르면, RDC -> 0이면 NN이 의미를 잃는다.

    매개변수:
        (compute_distance_ratio와 동일)
    반환값:
        (평균 RDC 리스트, 표준편차 리스트)
    """
    if dimensions is None:
        dimensions = [2, 5, 10, 20, 50, 100, 200, 500, 1000]

    mean_rdc = []
    std_rdc = []

    for d in dimensions:
        rdcs = []
        for _ in range(n_trials):
            if distribution == 'uniform':
                data = np.random.uniform(0, 1, size=(n_samples, d))
            else:
                data = np.random.randn(n_samples, d)

            query = np.zeros(d)
            diff = data - query
            distances = np.sum(np.abs(diff) ** p_norm, axis=1) ** (1.0 / p_norm)

            d_min = np.min(distances)
            d_max = np.max(distances)

            if d_min > 0:
                rdc = (d_max - d_min) / d_min
            else:
                rdc = np.inf

            rdcs.append(rdc)

        mean_rdc.append(np.mean(rdcs))
        std_rdc.append(np.std(rdcs))

    return mean_rdc, std_rdc


# ============================================================
# 2. 고차원에서의 KNN 분류 성능 저하 실험
# ============================================================

def knn_performance_vs_dimension(dimensions=None, n_samples=300, n_informative=5,
                                  n_trials=10, k=5):
    """
    차원이 증가할 때 KNN 분류 성능의 저하를 실험한다.

    유효 차원(informative features)은 고정하고,
    무관한 차원(noise features)을 추가하여 성능 변화를 관측한다.

    매개변수:
        dimensions: 전체 차원 리스트
        n_samples: 샘플 수
        n_informative: 유효 특성 수
        n_trials: 반복 횟수
        k: KNN의 K값
    반환값:
        (평균 정확도 리스트, 표준편차 리스트)
    """
    if dimensions is None:
        dimensions = [5, 10, 20, 50, 100, 200, 500]

    mean_accs = []
    std_accs = []

    for d in dimensions:
        accs = []
        for _ in range(n_trials):
            # 유효 특성으로 데이터 생성 (2 클래스)
            X_info = np.random.randn(n_samples, n_informative)
            y = (X_info[:, 0] + X_info[:, 1] > 0).astype(int)

            # 무관한 노이즈 특성 추가
            n_noise = d - n_informative
            if n_noise > 0:
                X_noise = np.random.randn(n_samples, n_noise)
                X = np.hstack([X_info, X_noise])
            else:
                X = X_info

            # 스케일링
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            # KNN 교차 검증 (5-Fold)
            knn = KNeighborsClassifier(n_neighbors=k)
            cv_scores = cross_val_score(knn, X_scaled, y, cv=5, scoring='accuracy')
            accs.append(cv_scores.mean())

        mean_accs.append(np.mean(accs))
        std_accs.append(np.std(accs))

    return mean_accs, std_accs


# ============================================================
# 3. 메인 실행
# ============================================================

def main():
    print("=" * 70)
    print("차원의 저주 (Curse of Dimensionality) 실험")
    print("Beyer et al. (1999) 논문 핵심 결과 재현")
    print("=" * 70)

    np.random.seed(42)

    dimensions = [2, 5, 10, 20, 50, 100, 200, 500, 1000]

    # --------------------------------------------------------
    # 실험 1: Dmax/Dmin 비율 (분포별 비교)
    # --------------------------------------------------------
    print("\n[실험 1] 차원별 Dmax/Dmin 비율 (분포별 비교)")
    print("-" * 50)

    print("  균일분포 (L2):")
    ratios_uniform, std_uniform = compute_distance_ratio(
        dimensions=dimensions, distribution='uniform', p_norm=2
    )
    for d, r, s in zip(dimensions, ratios_uniform, std_uniform):
        print(f"    d={d:5d}: Dmax/Dmin = {r:.4f} (+/- {s:.4f})")

    print("\n  가우시안분포 (L2):")
    ratios_gaussian, std_gaussian = compute_distance_ratio(
        dimensions=dimensions, distribution='gaussian', p_norm=2
    )
    for d, r, s in zip(dimensions, ratios_gaussian, std_gaussian):
        print(f"    d={d:5d}: Dmax/Dmin = {r:.4f} (+/- {s:.4f})")

    # --------------------------------------------------------
    # 실험 2: L1 vs L2 노름 비교
    # --------------------------------------------------------
    print("\n[실험 2] L1 vs L2 노름 비교 (균일분포)")
    print("-" * 50)

    print("  L1 (맨해튼 거리):")
    ratios_l1, std_l1 = compute_distance_ratio(
        dimensions=dimensions, distribution='uniform', p_norm=1
    )
    for d, r, s in zip(dimensions, ratios_l1, std_l1):
        print(f"    d={d:5d}: Dmax/Dmin = {r:.4f} (+/- {s:.4f})")

    print("\n  L2 (유클리드 거리):")
    # ratios_uniform은 이미 계산됨
    for d, r, s in zip(dimensions, ratios_uniform, std_uniform):
        print(f"    d={d:5d}: Dmax/Dmin = {r:.4f} (+/- {s:.4f})")

    # --------------------------------------------------------
    # 실험 3: 상대적 거리 대비 (RDC)
    # --------------------------------------------------------
    print("\n[실험 3] 상대적 거리 대비 (Relative Distance Contrast)")
    print("-" * 50)

    rdc_l2, rdc_std_l2 = compute_relative_contrast(
        dimensions=dimensions, distribution='uniform', p_norm=2
    )
    for d, r, s in zip(dimensions, rdc_l2, rdc_std_l2):
        print(f"    d={d:5d}: RDC = {r:.4f} (+/- {s:.4f})")

    # --------------------------------------------------------
    # 실험 4: 고차원에서 KNN 성능 저하
    # --------------------------------------------------------
    print("\n[실험 4] 차원 증가에 따른 KNN 분류 성능 변화")
    print("  (유효 특성 5개 고정, 노이즈 특성 추가)")
    print("-" * 50)

    dim_clf = [5, 10, 20, 50, 100, 200, 500]
    mean_accs, std_accs = knn_performance_vs_dimension(dimensions=dim_clf)

    for d, acc, std in zip(dim_clf, mean_accs, std_accs):
        print(f"    d={d:5d}: 평균 정확도 = {acc:.4f} (+/- {std:.4f})")

    # --------------------------------------------------------
    # 시각화
    # --------------------------------------------------------
    print("\n[시각화] 결과 그래프 생성 중...")

    fig, axes = plt.subplots(2, 2, figsize=(14, 12))

    # (a) 분포별 Dmax/Dmin 비율
    ax = axes[0, 0]
    ax.plot(dimensions, ratios_uniform, 'o-', color='steelblue', linewidth=2,
            markersize=7, label='Uniform')
    ax.fill_between(dimensions,
                    np.array(ratios_uniform) - np.array(std_uniform),
                    np.array(ratios_uniform) + np.array(std_uniform),
                    alpha=0.15, color='steelblue')
    ax.plot(dimensions, ratios_gaussian, 's--', color='coral', linewidth=2,
            markersize=7, label='Gaussian')
    ax.fill_between(dimensions,
                    np.array(ratios_gaussian) - np.array(std_gaussian),
                    np.array(ratios_gaussian) + np.array(std_gaussian),
                    alpha=0.15, color='coral')
    ax.axhline(y=1.0, color='gray', linestyle=':', alpha=0.7, label='Dmax/Dmin = 1')
    ax.set_xscale('log')
    ax.set_xlabel('차원 (d)', fontsize=12)
    ax.set_ylabel('Dmax / Dmin', fontsize=12)
    ax.set_title('(a) 분포별 Dmax/Dmin 비율 (L2 노름)', fontsize=13)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)

    # (b) L1 vs L2 비교
    ax = axes[0, 1]
    ax.plot(dimensions, ratios_l1, 'o-', color='forestgreen', linewidth=2,
            markersize=7, label='L1 (Manhattan)')
    ax.plot(dimensions, ratios_uniform, 's--', color='steelblue', linewidth=2,
            markersize=7, label='L2 (Euclidean)')
    ax.axhline(y=1.0, color='gray', linestyle=':', alpha=0.7)
    ax.set_xscale('log')
    ax.set_xlabel('차원 (d)', fontsize=12)
    ax.set_ylabel('Dmax / Dmin', fontsize=12)
    ax.set_title('(b) L1 vs L2 거리 집중 비교 (균일분포)', fontsize=13)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)

    # (c) 상대적 거리 대비 (RDC)
    ax = axes[1, 0]
    ax.plot(dimensions, rdc_l2, 'o-', color='purple', linewidth=2, markersize=7)
    ax.fill_between(dimensions,
                    np.array(rdc_l2) - np.array(rdc_std_l2),
                    np.array(rdc_l2) + np.array(rdc_std_l2),
                    alpha=0.15, color='purple')
    ax.axhline(y=0.0, color='red', linestyle=':', alpha=0.7, label='RDC = 0 (NN 무의미)')
    ax.set_xscale('log')
    ax.set_xlabel('차원 (d)', fontsize=12)
    ax.set_ylabel('(Dmax - Dmin) / Dmin', fontsize=12)
    ax.set_title('(c) 상대적 거리 대비 (L2, 균일분포)', fontsize=13)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)

    # (d) KNN 분류 성능 저하
    ax = axes[1, 1]
    ax.plot(dim_clf, mean_accs, 'o-', color='darkred', linewidth=2, markersize=7)
    ax.fill_between(dim_clf,
                    np.array(mean_accs) - np.array(std_accs),
                    np.array(mean_accs) + np.array(std_accs),
                    alpha=0.15, color='darkred')
    ax.set_xscale('log')
    ax.set_xlabel('전체 차원 (d)', fontsize=12)
    ax.set_ylabel('KNN 분류 정확도', fontsize=12)
    ax.set_title('(d) 차원 증가에 따른 KNN 성능 저하\n(유효 특성 5개 고정)', fontsize=13)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0.45, 1.0)

    plt.suptitle('차원의 저주 (Curse of Dimensionality)\nBeyer et al. (1999) 핵심 결과 재현',
                 fontsize=15, fontweight='bold', y=1.01)
    plt.tight_layout()
    plt.savefig('D:/26년1학기/기계학습/6장/구현소스/02_curse_of_dimensionality.png',
                dpi=150, bbox_inches='tight')
    plt.show()

    print("  결과 그래프가 02_curse_of_dimensionality.png로 저장되었다.")

    # --------------------------------------------------------
    # 핵심 결론 출력
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("핵심 결론")
    print("=" * 70)
    print(f"  1. 차원 {dimensions[0]} -> {dimensions[-1]}: "
          f"Dmax/Dmin 비율 {ratios_uniform[0]:.2f} -> {ratios_uniform[-1]:.2f} (1에 수렴)")
    print(f"  2. L1 노름이 L2 노름보다 거리 집중이 덜 심하다")
    print(f"     (d=1000에서 L1: {ratios_l1[-1]:.4f}, L2: {ratios_uniform[-1]:.4f})")
    print(f"  3. 노이즈 차원 추가 시 KNN 정확도: "
          f"{mean_accs[0]:.4f} (d={dim_clf[0]}) -> {mean_accs[-1]:.4f} (d={dim_clf[-1]})")
    print(f"  4. 이는 차원 축소(PCA 등) 및 특성 선택의 필요성을 보여준다")
    print("=" * 70)


if __name__ == "__main__":
    main()
