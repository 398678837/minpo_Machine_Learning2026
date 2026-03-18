"""
02_data_structures_benchmark.py
파이썬 자료구조 벤치마크: list, tuple, dict, set의 성능 비교

목적: 파이썬의 네 가지 기본 자료구조(리스트, 튜플, 딕셔너리, 세트)의
      탐색, 삽입, 삭제 연산 성능을 비교하여 각 자료구조의 적절한 사용 시나리오를 이해한다.

주요 개념:
  - 시간 복잡도 (Time Complexity): O(1), O(n)
  - 해시 테이블 기반 자료구조 (dict, set)의 장점
  - 메모리 사용량 비교
  - matplotlib을 활용한 성능 시각화
"""

import time
import sys
import random
import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# 한글 폰트 설정 (Windows)
# ============================================================
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False


def 시간측정(함수, *args, 반복횟수=10):
    """
    함수의 평균 실행 시간을 측정한다.
    """
    시간들 = []
    for _ in range(반복횟수):
        시작 = time.perf_counter()
        함수(*args)
        종료 = time.perf_counter()
        시간들.append(종료 - 시작)
    return np.mean(시간들)


# ============================================================
# 1. 탐색(검색) 성능 비교
# ============================================================
print("=" * 60)
print("  실험 1: 탐색(검색) 성능 비교 - 'in' 연산자")
print("=" * 60)
print("  리스트/튜플: O(n) - 처음부터 끝까지 순차 탐색")
print("  딕셔너리/세트: O(1) - 해시 테이블 기반 즉시 조회")
print()

크기들 = [1000, 5000, 10000, 50000, 100000, 500000]
리스트_탐색시간 = []
튜플_탐색시간 = []
딕셔너리_탐색시간 = []
세트_탐색시간 = []

for 크기 in 크기들:
    # 자료구조 생성
    데이터 = list(range(크기))
    리스트_데이터 = 데이터
    튜플_데이터 = tuple(데이터)
    딕셔너리_데이터 = {x: x for x in 데이터}
    세트_데이터 = set(데이터)

    # 탐색할 값들 (최악의 경우: 마지막 원소 근처)
    탐색값들 = [random.randint(크기 // 2, 크기 - 1) for _ in range(100)]

    # 리스트 탐색
    def 리스트_탐색():
        for v in 탐색값들:
            _ = v in 리스트_데이터

    # 튜플 탐색
    def 튜플_탐색():
        for v in 탐색값들:
            _ = v in 튜플_데이터

    # 딕셔너리 탐색
    def 딕셔너리_탐색():
        for v in 탐색값들:
            _ = v in 딕셔너리_데이터

    # 세트 탐색
    def 세트_탐색():
        for v in 탐색값들:
            _ = v in 세트_데이터

    리스트_탐색시간.append(시간측정(리스트_탐색, 반복횟수=5))
    튜플_탐색시간.append(시간측정(튜플_탐색, 반복횟수=5))
    딕셔너리_탐색시간.append(시간측정(딕셔너리_탐색, 반복횟수=5))
    세트_탐색시간.append(시간측정(세트_탐색, 반복횟수=5))

    print(f"  크기 {크기:>8,}: 리스트={리스트_탐색시간[-1]:.6f}s, "
          f"튜플={튜플_탐색시간[-1]:.6f}s, "
          f"딕셔너리={딕셔너리_탐색시간[-1]:.6f}s, "
          f"세트={세트_탐색시간[-1]:.6f}s")


# ============================================================
# 2. 삽입(추가) 성능 비교
# ============================================================
print("\n" + "=" * 60)
print("  실험 2: 삽입(추가) 성능 비교")
print("=" * 60)

삽입크기 = 100000


def 리스트_append_삽입():
    """리스트 끝에 삽입 (O(1) 분할상환)"""
    lst = []
    for i in range(삽입크기):
        lst.append(i)
    return lst


def 리스트_insert_삽입():
    """리스트 앞에 삽입 (O(n) - 모든 원소 이동)"""
    lst = []
    for i in range(삽입크기 // 10):  # 크기 줄임 (매우 느려서)
        lst.insert(0, i)
    return lst


def 딕셔너리_삽입():
    """딕셔너리 삽입 (O(1))"""
    d = {}
    for i in range(삽입크기):
        d[i] = i
    return d


def 세트_삽입():
    """세트 삽입 (O(1))"""
    s = set()
    for i in range(삽입크기):
        s.add(i)
    return s


시간_리스트_append = 시간측정(리스트_append_삽입, 반복횟수=5)
시간_리스트_insert = 시간측정(리스트_insert_삽입, 반복횟수=3)
시간_딕셔너리_삽입 = 시간측정(딕셔너리_삽입, 반복횟수=5)
시간_세트_삽입 = 시간측정(세트_삽입, 반복횟수=5)

print(f"\n삽입 크기: {삽입크기:,}개")
print(f"리스트 append (끝 삽입):    {시간_리스트_append:.4f}초 (O(1) 분할상환)")
print(f"리스트 insert(0) (앞 삽입): {시간_리스트_insert:.4f}초 ({삽입크기 // 10:,}개, O(n))")
print(f"딕셔너리 삽입:              {시간_딕셔너리_삽입:.4f}초 (O(1))")
print(f"세트 add:                  {시간_세트_삽입:.4f}초 (O(1))")


# ============================================================
# 3. 삭제 성능 비교
# ============================================================
print("\n" + "=" * 60)
print("  실험 3: 삭제 성능 비교")
print("=" * 60)

삭제크기 = 10000


def 리스트_pop_끝_삭제():
    """리스트 끝에서 삭제 (O(1))"""
    lst = list(range(삭제크기))
    while lst:
        lst.pop()


def 리스트_pop_앞_삭제():
    """리스트 앞에서 삭제 (O(n) - 모든 원소 이동)"""
    lst = list(range(삭제크기))
    while lst:
        lst.pop(0)


def 딕셔너리_삭제():
    """딕셔너리 삭제 (O(1))"""
    d = {i: i for i in range(삭제크기)}
    for i in range(삭제크기):
        del d[i]


def 세트_삭제():
    """세트 삭제 (O(1))"""
    s = set(range(삭제크기))
    for i in range(삭제크기):
        s.discard(i)


시간_리스트_pop끝 = 시간측정(리스트_pop_끝_삭제, 반복횟수=5)
시간_리스트_pop앞 = 시간측정(리스트_pop_앞_삭제, 반복횟수=3)
시간_딕셔너리_삭제 = 시간측정(딕셔너리_삭제, 반복횟수=5)
시간_세트_삭제 = 시간측정(세트_삭제, 반복횟수=5)

print(f"\n삭제 크기: {삭제크기:,}개")
print(f"리스트 pop() (끝 삭제):    {시간_리스트_pop끝:.4f}초")
print(f"리스트 pop(0) (앞 삭제):   {시간_리스트_pop앞:.4f}초")
print(f"딕셔너리 del:              {시간_딕셔너리_삭제:.4f}초")
print(f"세트 discard:              {시간_세트_삭제:.4f}초")


# ============================================================
# 4. 메모리 사용량 비교
# ============================================================
print("\n" + "=" * 60)
print("  실험 4: 메모리 사용량 비교")
print("=" * 60)

메모리크기 = 10000
리스트_메모리 = sys.getsizeof(list(range(메모리크기)))
튜플_메모리 = sys.getsizeof(tuple(range(메모리크기)))
딕셔너리_메모리 = sys.getsizeof({i: i for i in range(메모리크기)})
세트_메모리 = sys.getsizeof(set(range(메모리크기)))

print(f"\n원소 수: {메모리크기:,}개")
print(f"리스트:    {리스트_메모리:>10,} bytes ({리스트_메모리 / 1024:.1f} KB)")
print(f"튜플:      {튜플_메모리:>10,} bytes ({튜플_메모리 / 1024:.1f} KB)")
print(f"딕셔너리:  {딕셔너리_메모리:>10,} bytes ({딕셔너리_메모리 / 1024:.1f} KB)")
print(f"세트:      {세트_메모리:>10,} bytes ({세트_메모리 / 1024:.1f} KB)")
print(f"\n튜플은 리스트 대비 {(1 - 튜플_메모리 / 리스트_메모리) * 100:.1f}% 메모리 절약")


# ============================================================
# 5. 시각화
# ============================================================
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# (1) 탐색 성능 - 크기별 스케일링
axes[0, 0].plot(크기들, 리스트_탐색시간, 'o-', label='리스트', color='#e74c3c', linewidth=2)
axes[0, 0].plot(크기들, 튜플_탐색시간, 's-', label='튜플', color='#3498db', linewidth=2)
axes[0, 0].plot(크기들, 딕셔너리_탐색시간, '^-', label='딕셔너리', color='#2ecc71', linewidth=2)
axes[0, 0].plot(크기들, 세트_탐색시간, 'D-', label='세트', color='#f39c12', linewidth=2)
axes[0, 0].set_title('탐색 성능: 크기별 스케일링', fontsize=13, fontweight='bold')
axes[0, 0].set_xlabel('데이터 크기')
axes[0, 0].set_ylabel('실행 시간 (초)')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)
axes[0, 0].set_yscale('log')

# (2) 삽입 성능 - 막대 그래프
삽입_방법들 = ['리스트\nappend\n(끝)', '리스트\ninsert(0)\n(앞)', '딕셔너리\n삽입', '세트\nadd']
삽입_시간들 = [시간_리스트_append, 시간_리스트_insert * (삽입크기 // (삽입크기 // 10)),
             시간_딕셔너리_삽입, 시간_세트_삽입]
삽입_색상 = ['#e74c3c', '#c0392b', '#2ecc71', '#f39c12']

bars = axes[0, 1].bar(삽입_방법들, 삽입_시간들, color=삽입_색상, edgecolor='black', linewidth=0.5)
axes[0, 1].set_title(f'삽입 성능 비교 ({삽입크기:,}개)', fontsize=13, fontweight='bold')
axes[0, 1].set_ylabel('실행 시간 (초)')
axes[0, 1].set_yscale('log')

# (3) 삭제 성능 - 막대 그래프
삭제_방법들 = ['리스트\npop()\n(끝)', '리스트\npop(0)\n(앞)', '딕셔너리\ndel', '세트\ndiscard']
삭제_시간들 = [시간_리스트_pop끝, 시간_리스트_pop앞, 시간_딕셔너리_삭제, 시간_세트_삭제]
삭제_색상 = ['#e74c3c', '#c0392b', '#2ecc71', '#f39c12']

bars = axes[1, 0].bar(삭제_방법들, 삭제_시간들, color=삭제_색상, edgecolor='black', linewidth=0.5)
axes[1, 0].set_title(f'삭제 성능 비교 ({삭제크기:,}개)', fontsize=13, fontweight='bold')
axes[1, 0].set_ylabel('실행 시간 (초)')
axes[1, 0].set_yscale('log')

# (4) 메모리 사용량 - 수평 막대 그래프
메모리_자료구조 = ['리스트', '튜플', '딕셔너리', '세트']
메모리_값들 = [리스트_메모리 / 1024, 튜플_메모리 / 1024,
              딕셔너리_메모리 / 1024, 세트_메모리 / 1024]
메모리_색상 = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12']

barh = axes[1, 1].barh(메모리_자료구조, 메모리_값들, color=메모리_색상,
                       edgecolor='black', linewidth=0.5)
axes[1, 1].set_title(f'메모리 사용량 비교 ({메모리크기:,}개 원소)', fontsize=13, fontweight='bold')
axes[1, 1].set_xlabel('메모리 (KB)')

for bar, val in zip(barh, 메모리_값들):
    axes[1, 1].text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2.,
                    f'{val:.1f} KB', ha='left', va='center', fontsize=10)

plt.suptitle('파이썬 자료구조 벤치마크: list, tuple, dict, set',
             fontsize=15, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('D:/26년1학기/기계학습/2장/구현소스/data_structures_benchmark_결과.png',
            dpi=150, bbox_inches='tight')
plt.show()

# ============================================================
# 6. 시간 복잡도 요약
# ============================================================
print("\n" + "=" * 60)
print("  자료구조별 시간 복잡도 요약")
print("=" * 60)
print("""
| 연산        | 리스트      | 튜플  | 딕셔너리 | 세트   |
|-------------|-------------|-------|----------|--------|
| 인덱스 접근  | O(1)        | O(1)  | O(1)     | N/A    |
| 탐색 (in)   | O(n)        | O(n)  | O(1)     | O(1)   |
| 끝 삽입     | O(1)*       | N/A   | O(1)     | O(1)   |
| 앞 삽입     | O(n)        | N/A   | N/A      | N/A    |
| 끝 삭제     | O(1)        | N/A   | O(1)     | O(1)   |
| 앞 삭제     | O(n)        | N/A   | N/A      | N/A    |
| 메모리 효율  | 중간        | 높음  | 낮음     | 낮음   |
| 변경 가능   | O (mutable) | X     | O        | O      |

* O(1) 분할상환 (amortized)

[ML에서의 활용 가이드]
  - 순서가 중요한 데이터 (특성값, 시계열): 리스트/튜플
  - 빠른 검색이 필요한 경우 (범주 매핑): 딕셔너리
  - 중복 제거, 집합 연산: 세트
  - 변경 불가능한 키 (딕셔너리 키, 캐시): 튜플
""")
