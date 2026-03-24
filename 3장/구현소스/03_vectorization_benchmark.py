"""
03_vectorization_benchmark.py
NumPy 벡터화 vs Python 루프: 성능 비교 벤치마크

목적: 거리 계산, 행렬곱, 통계량 계산에서 NumPy 벡터화와 Python 루프의
      성능 차이를 측정하고, 1000x speedup을 시각적으로 증명한다.

주요 개념:
  - 벡터화 연산(Vectorized Operations)의 원리와 장점
  - 유클리드 거리 계산의 벡터화
  - 행렬곱의 벡터화
  - 기술통계량 계산의 벡터화
  - 성능 차이의 원인 분석
"""

import time
import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# 한글 폰트 설정 (Windows)
# ============================================================
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False


def 시간측정(함수, *args, 반복=3):
    """함수의 평균 실행 시간을 측정한다."""
    시간들 = []
    for _ in range(반복):
        시작 = time.perf_counter()
        결과 = 함수(*args)
        종료 = time.perf_counter()
        시간들.append(종료 - 시작)
    return np.mean(시간들), 결과


# ============================================================
# 1. 유클리드 거리 계산 벤치마크
# ============================================================
print("=" * 60)
print("  벤치마크 1: 유클리드 거리 계산")
print("=" * 60)
print("  두 점 집합 간의 쌍별(pairwise) 유클리드 거리 계산")
print("  ML 활용: KNN, K-Means 등 거리 기반 알고리즘의 핵심 연산")


def 거리_파이썬루프(X, Y):
    """
    Python 중첩 루프로 쌍별 유클리드 거리를 계산한다.
    시간 복잡도: O(n * m * d) - 매우 느림
    """
    n = len(X)
    m = len(Y)
    거리행렬 = [[0.0] * m for _ in range(n)]
    for i in range(n):
        for j in range(m):
            합 = 0
            for k in range(len(X[0])):
                합 += (X[i][k] - Y[j][k]) ** 2
            거리행렬[i][j] = 합 ** 0.5
    return 거리행렬


def 거리_numpy(X, Y):
    """
    NumPy 벡터화로 쌍별 유클리드 거리를 계산한다.
    브로드캐스팅을 활용하여 루프 없이 한 번에 계산.
    """
    # (n, 1, d) - (1, m, d) = (n, m, d) -> 각 원소 제곱 -> d축 합 -> 제곱근
    차이 = X[:, np.newaxis, :] - Y[np.newaxis, :, :]
    return np.sqrt(np.sum(차이 ** 2, axis=2))


def 거리_numpy_최적화(X, Y):
    """
    NumPy 최적화 버전: (a-b)^2 = a^2 + b^2 - 2ab 공식 활용
    행렬곱을 이용하여 메모리 효율적으로 계산.
    """
    X_제곱합 = np.sum(X ** 2, axis=1, keepdims=True)  # (n, 1)
    Y_제곱합 = np.sum(Y ** 2, axis=1, keepdims=True)  # (m, 1)
    교차항 = X @ Y.T  # (n, m)
    return np.sqrt(np.maximum(X_제곱합 + Y_제곱합.T - 2 * 교차항, 0))


# 테스트 데이터 생성
np.random.seed(42)
크기들_거리 = [50, 100, 200, 500]
차원 = 10

파이썬_거리시간 = []
numpy_거리시간 = []
numpy최적_거리시간 = []

for n in 크기들_거리:
    X = np.random.randn(n, 차원)
    Y = np.random.randn(n, 차원)
    X_리스트 = X.tolist()
    Y_리스트 = Y.tolist()

    시간_py, _ = 시간측정(거리_파이썬루프, X_리스트, Y_리스트, 반복=1)
    시간_np, _ = 시간측정(거리_numpy, X, Y)
    시간_np최적, _ = 시간측정(거리_numpy_최적화, X, Y)

    파이썬_거리시간.append(시간_py)
    numpy_거리시간.append(시간_np)
    numpy최적_거리시간.append(시간_np최적)

    배율 = 시간_py / 시간_np최적
    print(f"  n={n:>4}: 파이썬={시간_py:.4f}s, NumPy={시간_np:.6f}s, "
          f"NumPy최적={시간_np최적:.6f}s, 속도비={배율:.0f}x")


# ============================================================
# 2. 행렬곱 벤치마크
# ============================================================
print("\n" + "=" * 60)
print("  벤치마크 2: 행렬곱 (Matrix Multiplication)")
print("=" * 60)
print("  ML 활용: 신경망 순전파, 선형 변환, 커널 계산")


def 행렬곱_파이썬루프(A, B):
    """Python 삼중 루프로 행렬곱을 계산한다."""
    n, m = len(A), len(B[0])
    k = len(B)
    결과 = [[0.0] * m for _ in range(n)]
    for i in range(n):
        for j in range(m):
            합 = 0
            for p in range(k):
                합 += A[i][p] * B[p][j]
            결과[i][j] = 합
    return 결과


def 행렬곱_numpy(A, B):
    """NumPy의 @ 연산자로 행렬곱을 계산한다."""
    return A @ B


크기들_행렬 = [50, 100, 200, 500]
파이썬_행렬시간 = []
numpy_행렬시간 = []

for n in 크기들_행렬:
    A = np.random.randn(n, n)
    B = np.random.randn(n, n)
    A_리스트 = A.tolist()
    B_리스트 = B.tolist()

    시간_py, _ = 시간측정(행렬곱_파이썬루프, A_리스트, B_리스트, 반복=1)
    시간_np, _ = 시간측정(행렬곱_numpy, A, B)

    파이썬_행렬시간.append(시간_py)
    numpy_행렬시간.append(시간_np)

    배율 = 시간_py / 시간_np
    print(f"  n={n:>4}: 파이썬={시간_py:.4f}s, NumPy={시간_np:.6f}s, 속도비={배율:.0f}x")


# ============================================================
# 3. 통계량 계산 벤치마크
# ============================================================
print("\n" + "=" * 60)
print("  벤치마크 3: 기술통계량 계산 (평균, 표준편차, 상관계수)")
print("=" * 60)
print("  ML 활용: 데이터 표준화, 피처 스케일링, 상관 분석")


def 통계_파이썬(데이터):
    """Python으로 기술통계량을 계산한다."""
    n = len(데이터)
    m = len(데이터[0])

    # 열별 평균
    평균들 = []
    for j in range(m):
        합 = 0
        for i in range(n):
            합 += 데이터[i][j]
        평균들.append(합 / n)

    # 열별 표준편차
    표준편차들 = []
    for j in range(m):
        편차합 = 0
        for i in range(n):
            편차합 += (데이터[i][j] - 평균들[j]) ** 2
        표준편차들.append((편차합 / n) ** 0.5)

    # 열별 표준화 (z-score)
    표준화 = [[0.0] * m for _ in range(n)]
    for i in range(n):
        for j in range(m):
            표준화[i][j] = (데이터[i][j] - 평균들[j]) / 표준편차들[j] if 표준편차들[j] > 0 else 0

    return 평균들, 표준편차들, 표준화


def 통계_numpy(데이터):
    """NumPy로 기술통계량을 계산한다."""
    평균 = np.mean(데이터, axis=0)
    표준편차 = np.std(데이터, axis=0)
    표준화 = (데이터 - 평균) / np.where(표준편차 > 0, 표준편차, 1)
    return 평균, 표준편차, 표준화


크기들_통계 = [1000, 5000, 10000, 50000, 100000]
특성수 = 20
파이썬_통계시간 = []
numpy_통계시간 = []

for n in 크기들_통계:
    데이터_np = np.random.randn(n, 특성수)
    데이터_리스트 = 데이터_np.tolist()

    시간_py, _ = 시간측정(통계_파이썬, 데이터_리스트, 반복=1)
    시간_np, _ = 시간측정(통계_numpy, 데이터_np)

    파이썬_통계시간.append(시간_py)
    numpy_통계시간.append(시간_np)

    배율 = 시간_py / 시간_np
    print(f"  n={n:>7,}: 파이썬={시간_py:.4f}s, NumPy={시간_np:.6f}s, 속도비={배율:.0f}x")


# ============================================================
# 4. 종합 speedup 계산
# ============================================================
print("\n" + "=" * 60)
print("  종합 성능 비교 결과")
print("=" * 60)

최대_거리배율 = 파이썬_거리시간[-1] / numpy최적_거리시간[-1]
최대_행렬배율 = 파이썬_행렬시간[-1] / numpy_행렬시간[-1]
최대_통계배율 = 파이썬_통계시간[-1] / numpy_통계시간[-1]

print(f"\n거리 계산 최대 speedup:  {최대_거리배율:>10,.0f}x (n={크기들_거리[-1]})")
print(f"행렬곱 최대 speedup:     {최대_행렬배율:>10,.0f}x (n={크기들_행렬[-1]})")
print(f"통계량 계산 최대 speedup: {최대_통계배율:>10,.0f}x (n={크기들_통계[-1]:,})")


# ============================================================
# 5. 시각화
# ============================================================
fig, axes = plt.subplots(2, 3, figsize=(18, 10))

# (1) 거리 계산 - 절대 시간
axes[0, 0].plot(크기들_거리, 파이썬_거리시간, 'o-', label='Python 루프', color='#e74c3c', linewidth=2)
axes[0, 0].plot(크기들_거리, numpy_거리시간, 's-', label='NumPy', color='#3498db', linewidth=2)
axes[0, 0].plot(크기들_거리, numpy최적_거리시간, 'D-', label='NumPy 최적화', color='#2ecc71', linewidth=2)
axes[0, 0].set_title('유클리드 거리 계산', fontsize=12, fontweight='bold')
axes[0, 0].set_xlabel('데이터 크기 (n)')
axes[0, 0].set_ylabel('실행 시간 (초)')
axes[0, 0].set_yscale('log')
axes[0, 0].legend(fontsize=9)
axes[0, 0].grid(True, alpha=0.3)

# (2) 행렬곱 - 절대 시간
axes[0, 1].plot(크기들_행렬, 파이썬_행렬시간, 'o-', label='Python 루프', color='#e74c3c', linewidth=2)
axes[0, 1].plot(크기들_행렬, numpy_행렬시간, 's-', label='NumPy (@)', color='#3498db', linewidth=2)
axes[0, 1].set_title('행렬곱 (n x n)', fontsize=12, fontweight='bold')
axes[0, 1].set_xlabel('행렬 크기 (n)')
axes[0, 1].set_ylabel('실행 시간 (초)')
axes[0, 1].set_yscale('log')
axes[0, 1].legend(fontsize=9)
axes[0, 1].grid(True, alpha=0.3)

# (3) 통계량 - 절대 시간
axes[0, 2].plot(크기들_통계, 파이썬_통계시간, 'o-', label='Python 루프', color='#e74c3c', linewidth=2)
axes[0, 2].plot(크기들_통계, numpy_통계시간, 's-', label='NumPy', color='#3498db', linewidth=2)
axes[0, 2].set_title(f'기술통계량 계산 ({특성수}개 특성)', fontsize=12, fontweight='bold')
axes[0, 2].set_xlabel('샘플 수 (n)')
axes[0, 2].set_ylabel('실행 시간 (초)')
axes[0, 2].set_yscale('log')
axes[0, 2].legend(fontsize=9)
axes[0, 2].grid(True, alpha=0.3)

# (4) 거리 계산 - Speedup
거리_배율 = [p / n for p, n in zip(파이썬_거리시간, numpy최적_거리시간)]
axes[1, 0].bar([str(n) for n in 크기들_거리], 거리_배율, color='#f39c12', edgecolor='black')
axes[1, 0].set_title('거리 계산 Speedup (NumPy최적/Python)', fontsize=12, fontweight='bold')
axes[1, 0].set_xlabel('데이터 크기 (n)')
axes[1, 0].set_ylabel('속도 배율 (x)')
for i, v in enumerate(거리_배율):
    axes[1, 0].text(i, v + max(거리_배율) * 0.02, f'{v:.0f}x', ha='center', fontweight='bold')

# (5) 행렬곱 - Speedup
행렬_배율 = [p / n for p, n in zip(파이썬_행렬시간, numpy_행렬시간)]
axes[1, 1].bar([str(n) for n in 크기들_행렬], 행렬_배율, color='#9b59b6', edgecolor='black')
axes[1, 1].set_title('행렬곱 Speedup (NumPy/Python)', fontsize=12, fontweight='bold')
axes[1, 1].set_xlabel('행렬 크기 (n)')
axes[1, 1].set_ylabel('속도 배율 (x)')
for i, v in enumerate(행렬_배율):
    axes[1, 1].text(i, v + max(행렬_배율) * 0.02, f'{v:.0f}x', ha='center', fontweight='bold')

# (6) 통계량 - Speedup
통계_배율 = [p / n for p, n in zip(파이썬_통계시간, numpy_통계시간)]
axes[1, 2].bar([f'{n // 1000}K' for n in 크기들_통계], 통계_배율, color='#1abc9c', edgecolor='black')
axes[1, 2].set_title('통계량 Speedup (NumPy/Python)', fontsize=12, fontweight='bold')
axes[1, 2].set_xlabel('샘플 수')
axes[1, 2].set_ylabel('속도 배율 (x)')
for i, v in enumerate(통계_배율):
    axes[1, 2].text(i, v + max(통계_배율) * 0.02, f'{v:.0f}x', ha='center', fontweight='bold')

plt.suptitle('NumPy 벡터화 vs Python 루프: 성능 벤치마크\n(로그 스케일 - 차이가 매우 큼)',
             fontsize=15, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('D:/26년1학기/기계학습/3장/구현소스/vectorization_benchmark_결과.png',
            dpi=150, bbox_inches='tight')
plt.show()


# ============================================================
# 6. 왜 NumPy가 빠른가? - 원인 분석
# ============================================================
print("\n" + "=" * 60)
print("  왜 NumPy가 빠른가? - 성능 차이의 원인")
print("=" * 60)
print("""
[Python 루프가 느린 이유]
  1. 동적 타이핑: 매 연산마다 타입 확인 필요
  2. 인터프리터 오버헤드: 바이트코드 해석 비용
  3. 객체 오버헤드: 각 숫자가 Python 객체 (28+ bytes)
  4. 메모리 비연속: 리스트의 원소가 메모리에 흩어져 있음
  5. GIL: 싱글 스레드 실행 강제

[NumPy가 빠른 이유]
  1. C/Fortran 내부 루프: 컴파일된 네이티브 코드 실행
  2. 동질적 타입: 타입 확인 한 번만 필요
  3. 연속 메모리: CPU 캐시 효율 극대화
  4. BLAS/LAPACK: 수십 년간 최적화된 수치 라이브러리
  5. SIMD: 벡터 명령어를 통한 하드웨어 수준 병렬화
  6. GIL 해제: C 확장 내에서 GIL 해제하여 멀티코어 활용

[실전 가이드]
  - 수치 연산에는 절대로 Python 루프를 사용하지 말 것
  - NumPy 브로드캐스팅을 최대한 활용할 것
  - 벡터화가 어려운 경우: numba, cython 사용 고려
  - 대규모 데이터: Dask, CuPy(GPU) 사용 고려
""")

# 최종 메모리 비교
print("\n[메모리 비교: Python 리스트 vs NumPy 배열]")
import sys

n_mem = 1_000_000
리스트 = list(range(n_mem))
배열 = np.arange(n_mem, dtype=np.int64)

리스트_메모리 = sys.getsizeof(리스트) + sum(sys.getsizeof(x) for x in 리스트[:100]) * (n_mem // 100)
배열_메모리 = 배열.nbytes

print(f"  데이터 크기: {n_mem:,}개 정수")
print(f"  Python 리스트 메모리: ~{리스트_메모리 / 1024 / 1024:.1f} MB")
print(f"  NumPy 배열 메모리:    ~{배열_메모리 / 1024 / 1024:.1f} MB")
print(f"  메모리 절약: ~{리스트_메모리 / 배열_메모리:.1f}배")
