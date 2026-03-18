"""
03_functional_programming_ml.py
함수형 프로그래밍 패턴의 기계학습 활용

목적: map/filter/reduce를 활용한 데이터 파이프라인,
      데코레이터 패턴을 이용한 타이밍/캐싱,
      제너레이터 패턴을 이용한 배치 데이터 로딩을 구현한다.

주요 개념:
  - map(), filter(), reduce()를 활용한 함수형 데이터 처리
  - 데코레이터(decorator)를 활용한 함수 기능 확장
  - 제너레이터(generator)를 활용한 메모리 효율적 데이터 로딩
  - functools 모듈의 lru_cache를 활용한 메모이제이션
"""

import time
import functools
import random
import sys
import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# 한글 폰트 설정 (Windows)
# ============================================================
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False


# ============================================================
# 1. map/filter/reduce를 활용한 데이터 파이프라인
# ============================================================
print("=" * 60)
print("  1. map/filter/reduce 데이터 파이프라인")
print("=" * 60)

# 원시 데이터: 센서에서 수집된 온도 측정값 (노이즈 포함)
np.random.seed(42)
원시_온도데이터 = [round(random.gauss(25, 5), 1) for _ in range(100)]
# 일부 이상값 추가
원시_온도데이터[10] = -99.0  # 센서 오류
원시_온도데이터[50] = 999.0  # 센서 오류
원시_온도데이터[75] = None   # 결측값

print(f"\n원시 데이터 (처음 20개): {원시_온도데이터[:20]}")
print(f"데이터 수: {len(원시_온도데이터)}개")

# --- 파이프라인 단계 1: 결측값(None) 제거 ---
유효_데이터 = list(filter(lambda x: x is not None, 원시_온도데이터))
print(f"\n[1단계] 결측값 제거 후: {len(유효_데이터)}개")

# --- 파이프라인 단계 2: 이상값 제거 (0~50도 범위만 유지) ---
정상_데이터 = list(filter(lambda x: 0 <= x <= 50, 유효_데이터))
print(f"[2단계] 이상값 제거 후: {len(정상_데이터)}개")

# --- 파이프라인 단계 3: 섭씨 -> 화씨 변환 ---
화씨_데이터 = list(map(lambda c: round(c * 9 / 5 + 32, 1), 정상_데이터))
print(f"[3단계] 화씨 변환: {화씨_데이터[:10]}...")

# --- 파이프라인 단계 4: reduce로 통계량 계산 ---
from functools import reduce

합계 = reduce(lambda acc, x: acc + x, 정상_데이터)
평균 = 합계 / len(정상_데이터)
최솟값 = reduce(lambda a, b: a if a < b else b, 정상_데이터)
최댓값 = reduce(lambda a, b: a if a > b else b, 정상_데이터)

print(f"\n[통계량 (reduce 활용)]")
print(f"  합계: {합계:.1f}")
print(f"  평균: {평균:.1f}도")
print(f"  최솟값: {최솟값}도")
print(f"  최댓값: {최댓값}도")


# --- 함수형 파이프라인을 하나의 함수로 결합 ---
def 데이터_파이프라인(원시데이터, 최소=0, 최대=50):
    """
    함수형 프로그래밍 스타일의 데이터 전처리 파이프라인.

    단계: 결측값 제거 -> 이상값 제거 -> 정규화(0~1 스케일링)
    """
    # 결측값 제거
    유효 = list(filter(lambda x: x is not None, 원시데이터))
    # 이상값 제거
    정상 = list(filter(lambda x: 최소 <= x <= 최대, 유효))
    # Min-Max 정규화 (0~1)
    min_val = min(정상)
    max_val = max(정상)
    범위 = max_val - min_val
    정규화 = list(map(lambda x: round((x - min_val) / 범위, 4) if 범위 > 0 else 0, 정상))
    return 정규화


정규화_결과 = 데이터_파이프라인(원시_온도데이터)
print(f"\n[파이프라인 결과 - 정규화된 데이터]")
print(f"  처음 10개: {정규화_결과[:10]}")
print(f"  최솟값: {min(정규화_결과)}, 최댓값: {max(정규화_결과)}")


# ============================================================
# 2. 데코레이터 패턴: 타이밍과 캐싱
# ============================================================
print("\n" + "=" * 60)
print("  2. 데코레이터 패턴: ML 함수의 타이밍과 캐싱")
print("=" * 60)


# --- 타이밍 데코레이터 ---
def 타이밍(함수):
    """
    함수의 실행 시간을 자동으로 측정하는 데코레이터.
    ML 실험에서 각 단계의 소요 시간을 추적하는 데 유용하다.
    """
    @functools.wraps(함수)
    def 래퍼(*args, **kwargs):
        시작 = time.perf_counter()
        결과 = 함수(*args, **kwargs)
        종료 = time.perf_counter()
        경과시간 = 종료 - 시작
        print(f"  [{함수.__name__}] 실행 시간: {경과시간:.4f}초")
        return 결과
    return 래퍼


# --- 로깅 데코레이터 ---
def 로깅(함수):
    """
    함수 호출 시 입력/출력을 자동으로 기록하는 데코레이터.
    실험 재현성을 위한 로깅에 활용된다.
    """
    @functools.wraps(함수)
    def 래퍼(*args, **kwargs):
        print(f"  [로그] {함수.__name__} 호출 - args 크기: {[len(a) if hasattr(a, '__len__') else a for a in args]}")
        결과 = 함수(*args, **kwargs)
        if hasattr(결과, '__len__'):
            print(f"  [로그] {함수.__name__} 완료 - 결과 크기: {len(결과)}")
        return 결과
    return 래퍼


# --- 캐싱 데코레이터 (메모이제이션) ---
def 캐싱(최대크기=128):
    """
    함수 결과를 캐싱하는 데코레이터.
    동일한 입력에 대해 재계산을 방지한다.
    하이퍼파라미터 조합별 결과를 캐싱하는 데 활용 가능하다.
    """
    def 데코레이터(함수):
        캐시 = {}

        @functools.wraps(함수)
        def 래퍼(*args):
            if args in 캐시:
                print(f"  [캐시 히트] {함수.__name__}({args})")
                return 캐시[args]
            결과 = 함수(*args)
            if len(캐시) < 최대크기:
                캐시[args] = 결과
            print(f"  [캐시 미스] {함수.__name__}({args}) -> 새로 계산")
            return 결과
        래퍼.캐시 = 캐시
        return 래퍼
    return 데코레이터


# 데코레이터 적용 예시
@타이밍
@로깅
def 데이터_전처리(데이터):
    """데이터 전처리 함수 (타이밍 + 로깅 적용)"""
    정제 = [x for x in 데이터 if x is not None and 0 <= x <= 50]
    평균 = sum(정제) / len(정제)
    표준화 = [(x - 평균) for x in 정제]
    return 표준화


print("\n[데코레이터 적용 함수 실행]")
전처리_결과 = 데이터_전처리(원시_온도데이터)


# functools.lru_cache 활용 (내장 캐싱 데코레이터)
@functools.lru_cache(maxsize=128)
def 피보나치(n):
    """
    피보나치 수 계산 (캐시 적용).
    lru_cache 없이는 지수 시간 복잡도 O(2^n),
    캐시 적용 시 선형 시간 O(n).
    """
    if n <= 1:
        return n
    return 피보나치(n - 1) + 피보나치(n - 2)


print("\n[lru_cache 데모: 피보나치 수]")
시작 = time.perf_counter()
결과 = 피보나치(100)
종료 = time.perf_counter()
print(f"  피보나치(100) = {결과}")
print(f"  실행 시간: {종료 - 시작:.6f}초 (캐시 덕분에 즉시 완료)")
print(f"  캐시 정보: {피보나치.cache_info()}")


# 커스텀 캐싱 데코레이터 예시
@캐싱(최대크기=64)
def 거리계산(x1, y1, x2, y2):
    """두 점 간의 유클리드 거리 계산 (캐싱 적용)"""
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5


print("\n[커스텀 캐싱 데코레이터 데모]")
거리계산(0, 0, 3, 4)  # 캐시 미스
거리계산(0, 0, 3, 4)  # 캐시 히트
거리계산(1, 1, 4, 5)  # 캐시 미스


# ============================================================
# 3. 제너레이터 패턴: 배치 데이터 로딩
# ============================================================
print("\n" + "=" * 60)
print("  3. 제너레이터 패턴: 메모리 효율적 배치 데이터 로딩")
print("=" * 60)


def 배치_데이터_로더(데이터, 배치크기=32, 셔플=True):
    """
    ML 학습을 위한 배치 데이터 로더 (제너레이터).

    대용량 데이터셋을 한 번에 메모리에 로드하지 않고,
    배치 단위로 순차적으로 공급한다.

    Parameters
    ----------
    데이터 : list or np.ndarray
        전체 데이터셋
    배치크기 : int
        한 배치의 크기 (기본값: 32)
    셔플 : bool
        에폭 시작 시 데이터를 섞을지 여부

    Yields
    ------
    list
        배치 데이터
    """
    인덱스들 = list(range(len(데이터)))

    if 셔플:
        random.shuffle(인덱스들)

    for 시작 in range(0, len(인덱스들), 배치크기):
        배치_인덱스 = 인덱스들[시작:시작 + 배치크기]
        배치 = [데이터[i] for i in 배치_인덱스]
        yield 배치


def 에폭_학습기(데이터, 에폭수=3, 배치크기=16):
    """
    에폭(epoch) 기반 학습 루프 시뮬레이션.

    Parameters
    ----------
    데이터 : list
        학습 데이터
    에폭수 : int
        전체 데이터를 반복하는 횟수
    배치크기 : int
        배치 크기
    """
    for 에폭 in range(에폭수):
        에폭_손실 = 0
        배치수 = 0
        for 배치 in 배치_데이터_로더(데이터, 배치크기):
            # 간단한 학습 시뮬레이션 (평균 제곱 오차)
            배치_손실 = sum(x ** 2 for x in 배치) / len(배치)
            에폭_손실 += 배치_손실
            배치수 += 1

        평균_손실 = 에폭_손실 / 배치수
        print(f"  에폭 {에폭 + 1}/{에폭수} - 평균 손실: {평균_손실:.4f}, 배치 수: {배치수}")


# 학습 데이터 생성
학습_데이터 = [random.gauss(0, 1) for _ in range(200)]
print(f"\n학습 데이터 크기: {len(학습_데이터)}개")
print(f"\n[배치 학습 시뮬레이션]")
에폭_학습기(학습_데이터, 에폭수=3, 배치크기=32)


# --- 메모리 효율 비교: 리스트 vs 제너레이터 ---
print("\n[메모리 효율 비교]")

# 리스트: 모든 데이터를 메모리에 저장
리스트_전체 = [x ** 2 for x in range(1_000_000)]
리스트_메모리 = sys.getsizeof(리스트_전체)

# 제너레이터: 필요할 때만 값 생성
제너레이터_전체 = (x ** 2 for x in range(1_000_000))
제너레이터_메모리 = sys.getsizeof(제너레이터_전체)

print(f"  리스트 (100만개) 메모리:    {리스트_메모리:>12,} bytes ({리스트_메모리 / 1024 / 1024:.1f} MB)")
print(f"  제너레이터 (100만개) 메모리: {제너레이터_메모리:>12,} bytes ({제너레이터_메모리} bytes!)")
print(f"  메모리 절약: {리스트_메모리 / 제너레이터_메모리:.0f}배")


# --- 무한 데이터 스트림 제너레이터 ---
def 데이터_증강기(원본데이터, 노이즈강도=0.1):
    """
    데이터 증강(augmentation) 제너레이터.
    원본 데이터에 랜덤 노이즈를 추가하여 무한히 새로운 데이터를 생성한다.
    """
    while True:
        for 데이터 in 원본데이터:
            노이즈 = random.gauss(0, 노이즈강도)
            yield 데이터 + 노이즈


print("\n[데이터 증강 제너레이터]")
원본 = [1.0, 2.0, 3.0, 4.0, 5.0]
증강기 = 데이터_증강기(원본, 노이즈강도=0.2)

print(f"  원본 데이터: {원본}")
증강_데이터 = [round(next(증강기), 2) for _ in range(15)]
print(f"  증강 데이터 (15개): {증강_데이터}")


# ============================================================
# 4. 함수 합성 (Function Composition) 패턴
# ============================================================
print("\n" + "=" * 60)
print("  4. 함수 합성 (Function Composition) 패턴")
print("=" * 60)


def 파이프라인(*함수들):
    """
    여러 함수를 순차적으로 합성하는 파이프라인 생성기.
    f(g(h(x))) 대신 파이프라인(h, g, f)(x)로 표현 가능.

    ML 전처리 단계를 체인으로 연결하는 데 활용된다.
    """
    def 합성_함수(입력):
        결과 = 입력
        for 함수 in 함수들:
            결과 = 함수(결과)
        return 결과
    return 합성_함수


# 개별 전처리 함수 정의
def 결측값_제거(데이터):
    """결측값(None) 제거"""
    return [x for x in 데이터 if x is not None]


def 이상값_제거(데이터, 하한=0, 상한=50):
    """범위 밖의 이상값 제거"""
    return [x for x in 데이터 if 하한 <= x <= 상한]


def 표준화(데이터):
    """평균 0, 표준편차 1로 표준화 (Z-score)"""
    평균 = sum(데이터) / len(데이터)
    분산 = sum((x - 평균) ** 2 for x in 데이터) / len(데이터)
    표준편차 = 분산 ** 0.5
    return [round((x - 평균) / 표준편차, 4) if 표준편차 > 0 else 0 for x in 데이터]


# 파이프라인 생성
ML_전처리 = 파이프라인(결측값_제거, 이상값_제거, 표준화)

# 파이프라인 실행
최종_결과 = ML_전처리(원시_온도데이터)
print(f"\n[함수 합성 파이프라인 결과]")
print(f"  입력 크기: {len(원시_온도데이터)}개")
print(f"  출력 크기: {len(최종_결과)}개")
print(f"  처음 10개: {최종_결과[:10]}")
print(f"  평균: {sum(최종_결과) / len(최종_결과):.4f} (표준화 후 ~0)")


# ============================================================
# 5. 시각화: 파이프라인 결과 비교
# ============================================================
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# (1) 원시 데이터 히스토그램
원시_유효 = [x for x in 원시_온도데이터 if x is not None]
axes[0].hist(원시_유효, bins=30, color='#e74c3c', alpha=0.7, edgecolor='black')
axes[0].set_title('원시 데이터 (이상값 포함)', fontsize=12, fontweight='bold')
axes[0].set_xlabel('온도 (도)')
axes[0].set_ylabel('빈도')
axes[0].axvline(x=-99, color='red', linestyle='--', label='이상값')
axes[0].axvline(x=999, color='red', linestyle='--')

# (2) 정제된 데이터 히스토그램
axes[1].hist(정상_데이터, bins=20, color='#3498db', alpha=0.7, edgecolor='black')
axes[1].set_title('정제된 데이터 (이상값 제거)', fontsize=12, fontweight='bold')
axes[1].set_xlabel('온도 (도)')
axes[1].set_ylabel('빈도')

# (3) 표준화된 데이터 히스토그램
axes[2].hist(최종_결과, bins=20, color='#2ecc71', alpha=0.7, edgecolor='black')
axes[2].set_title('표준화된 데이터 (Z-score)', fontsize=12, fontweight='bold')
axes[2].set_xlabel('표준화 값')
axes[2].set_ylabel('빈도')
axes[2].axvline(x=0, color='red', linestyle='--', alpha=0.5, label='평균=0')
axes[2].legend()

plt.suptitle('함수형 프로그래밍 데이터 파이프라인: 단계별 데이터 변환',
             fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('D:/26년1학기/기계학습/2장/구현소스/functional_programming_결과.png',
            dpi=150, bbox_inches='tight')
plt.show()


print("\n" + "=" * 60)
print("  핵심 정리")
print("=" * 60)
print("""
[함수형 프로그래밍 패턴과 ML 활용]

1. map/filter/reduce
   - map(): 데이터 변환 (스케일링, 인코딩, 정규화)
   - filter(): 데이터 필터링 (이상값 제거, 결측값 제거)
   - reduce(): 집계 연산 (합산, 최솟값/최댓값)

2. 데코레이터 (Decorator)
   - @타이밍: 학습/추론 시간 측정
   - @로깅: 실험 결과 자동 기록
   - @lru_cache: 중복 계산 방지 (하이퍼파라미터 튜닝 시)

3. 제너레이터 (Generator)
   - 배치 데이터 로딩: 대용량 데이터의 메모리 효율적 처리
   - 데이터 증강: 무한 스트림 기반 데이터 생성
   - 에폭 학습: yield를 통한 배치 단위 데이터 공급

4. 함수 합성 (Function Composition)
   - 전처리 파이프라인: 여러 단계를 하나로 결합
   - scikit-learn의 Pipeline이 이 패턴의 객체 지향 구현체
""")
