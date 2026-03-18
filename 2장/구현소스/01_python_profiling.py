"""
01_python_profiling.py
파이썬 성능 프로파일링: 다양한 연산 방식의 실행 시간 비교

목적: 리스트 컴프리헨션, for 루프, map, NumPy 벡터화의 성능을 비교하여
      파이썬에서 효율적인 코드를 작성하는 방법을 이해한다.

주요 개념:
  - time 모듈을 활용한 실행 시간 측정
  - 리스트 컴프리헨션 vs for 루프 vs map() vs NumPy 벡터화
  - matplotlib을 활용한 성능 비교 시각화
"""

import time
import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# 한글 폰트 설정 (Windows)
# ============================================================
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False


def 시간측정(함수, *args, 반복횟수=5):
    """
    함수의 실행 시간을 측정하는 유틸리티 함수.
    여러 번 실행하여 평균 시간을 반환한다.

    Parameters
    ----------
    함수 : callable
        시간을 측정할 함수
    *args : tuple
        함수에 전달할 인자들
    반복횟수 : int
        측정 반복 횟수 (기본값: 5)

    Returns
    -------
    float
        평균 실행 시간 (초)
    """
    시간들 = []
    for _ in range(반복횟수):
        시작 = time.perf_counter()
        함수(*args)
        종료 = time.perf_counter()
        시간들.append(종료 - 시작)
    return np.mean(시간들)


# ============================================================
# 1. 제곱 연산 비교
# ============================================================
print("=" * 60)
print("  실험 1: 제곱 연산 (x^2) 성능 비교")
print("=" * 60)

데이터크기 = 1_000_000
데이터_리스트 = list(range(데이터크기))
데이터_배열 = np.arange(데이터크기)


def for루프_제곱(data):
    """for 루프를 사용한 제곱 연산"""
    결과 = []
    for x in data:
        결과.append(x ** 2)
    return 결과


def 리스트컴프리헨션_제곱(data):
    """리스트 컴프리헨션을 사용한 제곱 연산"""
    return [x ** 2 for x in data]


def map_제곱(data):
    """map()을 사용한 제곱 연산"""
    return list(map(lambda x: x ** 2, data))


def numpy_제곱(data):
    """NumPy 벡터화를 사용한 제곱 연산"""
    return data ** 2


# 각 방식의 실행 시간 측정
시간_for루프 = 시간측정(for루프_제곱, 데이터_리스트)
시간_컴프리헨션 = 시간측정(리스트컴프리헨션_제곱, 데이터_리스트)
시간_map = 시간측정(map_제곱, 데이터_리스트)
시간_numpy = 시간측정(numpy_제곱, 데이터_배열)

print(f"\n데이터 크기: {데이터크기:,}개")
print(f"for 루프:         {시간_for루프:.4f}초")
print(f"리스트 컴프리헨션: {시간_컴프리헨션:.4f}초")
print(f"map():            {시간_map:.4f}초")
print(f"NumPy 벡터화:     {시간_numpy:.6f}초")
print(f"\nNumPy 대비 for 루프 속도비: {시간_for루프 / 시간_numpy:.1f}배 느림")


# ============================================================
# 2. 합산 연산 비교
# ============================================================
print("\n" + "=" * 60)
print("  실험 2: 합산 연산 성능 비교")
print("=" * 60)


def for루프_합산(data):
    """for 루프를 사용한 합산"""
    합계 = 0
    for x in data:
        합계 += x
    return 합계


def builtin_합산(data):
    """내장 sum()을 사용한 합산"""
    return sum(data)


def numpy_합산(data):
    """NumPy를 사용한 합산"""
    return np.sum(data)


시간_for합산 = 시간측정(for루프_합산, 데이터_리스트)
시간_builtin합산 = 시간측정(builtin_합산, 데이터_리스트)
시간_numpy합산 = 시간측정(numpy_합산, 데이터_배열)

print(f"\nfor 루프 합산:    {시간_for합산:.4f}초")
print(f"내장 sum() 합산:  {시간_builtin합산:.4f}초")
print(f"NumPy sum() 합산: {시간_numpy합산:.6f}초")


# ============================================================
# 3. 조건부 필터링 비교
# ============================================================
print("\n" + "=" * 60)
print("  실험 3: 조건부 필터링 (짝수 추출) 성능 비교")
print("=" * 60)


def for루프_필터(data):
    """for 루프를 사용한 짝수 필터링"""
    결과 = []
    for x in data:
        if x % 2 == 0:
            결과.append(x)
    return 결과


def 컴프리헨션_필터(data):
    """리스트 컴프리헨션을 사용한 짝수 필터링"""
    return [x for x in data if x % 2 == 0]


def filter_필터(data):
    """filter()를 사용한 짝수 필터링"""
    return list(filter(lambda x: x % 2 == 0, data))


def numpy_필터(data):
    """NumPy 불리언 인덱싱을 사용한 짝수 필터링"""
    return data[data % 2 == 0]


시간_for필터 = 시간측정(for루프_필터, 데이터_리스트)
시간_컴프리헨션필터 = 시간측정(컴프리헨션_필터, 데이터_리스트)
시간_filter필터 = 시간측정(filter_필터, 데이터_리스트)
시간_numpy필터 = 시간측정(numpy_필터, 데이터_배열)

print(f"\nfor 루프:         {시간_for필터:.4f}초")
print(f"리스트 컴프리헨션: {시간_컴프리헨션필터:.4f}초")
print(f"filter():         {시간_filter필터:.4f}초")
print(f"NumPy 불리언 인덱싱: {시간_numpy필터:.6f}초")


# ============================================================
# 4. 데이터 크기별 스케일링 테스트
# ============================================================
print("\n" + "=" * 60)
print("  실험 4: 데이터 크기별 성능 스케일링")
print("=" * 60)

크기들 = [1000, 10000, 100000, 500000, 1000000]
for루프_시간들 = []
컴프리헨션_시간들 = []
map_시간들 = []
numpy_시간들 = []

for 크기 in 크기들:
    리스트 = list(range(크기))
    배열 = np.arange(크기)

    for루프_시간들.append(시간측정(for루프_제곱, 리스트, 반복횟수=3))
    컴프리헨션_시간들.append(시간측정(리스트컴프리헨션_제곱, 리스트, 반복횟수=3))
    map_시간들.append(시간측정(map_제곱, 리스트, 반복횟수=3))
    numpy_시간들.append(시간측정(numpy_제곱, 배열, 반복횟수=3))

    print(f"  크기 {크기:>10,}: for={for루프_시간들[-1]:.4f}s, "
          f"comp={컴프리헨션_시간들[-1]:.4f}s, "
          f"map={map_시간들[-1]:.4f}s, "
          f"numpy={numpy_시간들[-1]:.6f}s")


# ============================================================
# 5. 시각화
# ============================================================
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# (1) 제곱 연산 비교 - 막대 그래프
방법들 = ['for 루프', '리스트\n컴프리헨션', 'map()', 'NumPy\n벡터화']
시간들 = [시간_for루프, 시간_컴프리헨션, 시간_map, 시간_numpy]
색상들 = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12']

bars = axes[0, 0].bar(방법들, 시간들, color=색상들, edgecolor='black', linewidth=0.5)
axes[0, 0].set_title('제곱 연산 (x^2) 성능 비교', fontsize=13, fontweight='bold')
axes[0, 0].set_ylabel('실행 시간 (초)')
axes[0, 0].set_yscale('log')  # 로그 스케일 (차이가 크므로)

# 각 막대 위에 시간 표시
for bar, t in zip(bars, 시간들):
    axes[0, 0].text(bar.get_x() + bar.get_width() / 2., bar.get_height() * 1.1,
                    f'{t:.4f}s', ha='center', va='bottom', fontsize=9)

# (2) 합산/필터 비교 - 그룹 막대 그래프
연산들 = ['합산', '필터링']
for_시간 = [시간_for합산, 시간_for필터]
numpy_시간 = [시간_numpy합산, 시간_numpy필터]

x = np.arange(len(연산들))
너비 = 0.3

axes[0, 1].bar(x - 너비 / 2, for_시간, 너비, label='for 루프', color='#e74c3c')
axes[0, 1].bar(x + 너비 / 2, numpy_시간, 너비, label='NumPy', color='#f39c12')
axes[0, 1].set_title('연산별 for루프 vs NumPy', fontsize=13, fontweight='bold')
axes[0, 1].set_ylabel('실행 시간 (초)')
axes[0, 1].set_xticks(x)
axes[0, 1].set_xticklabels(연산들)
axes[0, 1].legend()
axes[0, 1].set_yscale('log')

# (3) 데이터 크기별 스케일링 - 선 그래프
axes[1, 0].plot(크기들, for루프_시간들, 'o-', label='for 루프', color='#e74c3c', linewidth=2)
axes[1, 0].plot(크기들, 컴프리헨션_시간들, 's-', label='리스트 컴프리헨션', color='#3498db', linewidth=2)
axes[1, 0].plot(크기들, map_시간들, '^-', label='map()', color='#2ecc71', linewidth=2)
axes[1, 0].plot(크기들, numpy_시간들, 'D-', label='NumPy 벡터화', color='#f39c12', linewidth=2)
axes[1, 0].set_title('데이터 크기별 성능 스케일링', fontsize=13, fontweight='bold')
axes[1, 0].set_xlabel('데이터 크기')
axes[1, 0].set_ylabel('실행 시간 (초)')
axes[1, 0].set_yscale('log')
axes[1, 0].legend()
axes[1, 0].grid(True, alpha=0.3)

# (4) 속도 배율 비교 - 수평 막대 그래프
속도배율 = [시간_for루프 / 시간_numpy,
           시간_컴프리헨션 / 시간_numpy,
           시간_map / 시간_numpy,
           1.0]
방법라벨 = ['for 루프', '리스트 컴프리헨션', 'map()', 'NumPy (기준)']

barh = axes[1, 1].barh(방법라벨, 속도배율, color=색상들, edgecolor='black', linewidth=0.5)
axes[1, 1].set_title('NumPy 대비 속도 비율 (낮을수록 빠름)', fontsize=13, fontweight='bold')
axes[1, 1].set_xlabel('상대 실행 시간 (NumPy = 1)')
axes[1, 1].set_xscale('log')

# 각 막대 옆에 배율 표시
for bar, ratio in zip(barh, 속도배율):
    axes[1, 1].text(bar.get_width() * 1.05, bar.get_y() + bar.get_height() / 2.,
                    f'{ratio:.1f}x', ha='left', va='center', fontsize=10, fontweight='bold')

plt.suptitle('파이썬 성능 프로파일링: 다양한 연산 방식 비교\n(데이터 크기: 1,000,000)',
             fontsize=15, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('D:/26년1학기/기계학습/2장/구현소스/python_profiling_결과.png',
            dpi=150, bbox_inches='tight')
plt.show()

print("\n" + "=" * 60)
print("  결론")
print("=" * 60)
print("""
[성능 순위] (빠른 순)
  1. NumPy 벡터화 - 압도적 성능 (C 수준 내부 루프)
  2. 리스트 컴프리헨션 - 파이썬 내에서 가장 빠른 반복
  3. map() - 컴프리헨션과 유사하나 lambda 오버헤드
  4. for 루프 - 가장 느림 (append 오버헤드 추가)

[핵심 교훈]
  - 수치 연산에는 반드시 NumPy를 사용할 것
  - 순수 파이썬에서는 리스트 컴프리헨션이 가장 효율적
  - NumPy는 for 루프 대비 수십~수백 배 빠름
  - 데이터가 클수록 NumPy의 이점이 극대화됨
""")
