"""
02_pandas_data_pipeline.py
Pandas 데이터 파이프라인: method chaining, pipe(), 결측치 처리 전략, 그룹별 변환, 윈도우 함수

목적: Pandas의 고급 데이터 처리 기법을 활용하여
      ML 전처리에 필요한 다양한 파이프라인 패턴을 구현한다.

주요 개념:
  - Method chaining으로 가독성 높은 파이프라인 구성
  - pipe()를 활용한 커스텀 변환 함수 통합
  - 결측치 처리 전략 비교 (삭제, 평균/중앙값 대체, 보간, 그룹별 대체)
  - groupby + transform/apply를 활용한 그룹별 피처 생성
  - rolling/expanding 윈도우 함수
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ============================================================
# 한글 폰트 설정 (Windows)
# ============================================================
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

np.random.seed(42)


# ============================================================
# 1. 실습 데이터 생성
# ============================================================
print("=" * 60)
print("  1. 실습 데이터 생성 (가상 고객 거래 데이터)")
print("=" * 60)

n = 500
고객ID = np.random.choice(['C001', 'C002', 'C003', 'C004', 'C005'], size=n)
날짜 = pd.date_range('2024-01-01', periods=n, freq='6H')
카테고리 = np.random.choice(['전자제품', '의류', '식품', '도서'], size=n)
금액 = np.random.exponential(50000, size=n).astype(int) + 5000
수량 = np.random.randint(1, 10, size=n)

df = pd.DataFrame({
    '날짜': 날짜,
    '고객ID': 고객ID,
    '카테고리': 카테고리,
    '금액': 금액,
    '수량': 수량
})

# 의도적으로 결측치 삽입 (현실적인 시나리오)
결측_인덱스_금액 = np.random.choice(n, size=30, replace=False)
결측_인덱스_수량 = np.random.choice(n, size=20, replace=False)
df.loc[결측_인덱스_금액, '금액'] = np.nan
df.loc[결측_인덱스_수량, '수량'] = np.nan

# 이상값 삽입
이상값_인덱스 = np.random.choice(n, size=5, replace=False)
df.loc[이상값_인덱스, '금액'] = np.random.randint(500000, 1000000, size=5).astype(float)

print(f"\n데이터 shape: {df.shape}")
print(f"\n처음 10행:")
print(df.head(10))
print(f"\n결측치 현황:")
print(df.isna().sum())
print(f"\n기술 통계:")
print(df.describe())


# ============================================================
# 2. Method Chaining으로 파이프라인 구성
# ============================================================
print("\n" + "=" * 60)
print("  2. Method Chaining 파이프라인")
print("=" * 60)

결과_체이닝 = (
    df
    .copy()
    # 날짜에서 파생 변수 생성
    .assign(
        연도=lambda x: x['날짜'].dt.year,
        월=lambda x: x['날짜'].dt.month,
        요일=lambda x: x['날짜'].dt.day_name(),
        시간대=lambda x: pd.cut(x['날짜'].dt.hour,
                              bins=[0, 6, 12, 18, 24],
                              labels=['새벽', '오전', '오후', '저녁'],
                              right=False)
    )
    # 결측치가 아닌 행만 유지 (간단 버전)
    .dropna(subset=['금액'])
    # 이상값 제거 (IQR 방식 적용)
    .query('금액 < @df["금액"].quantile(0.99)')
    # 총금액 계산
    .assign(총금액=lambda x: x['금액'] * x['수량'].fillna(1))
    # 정렬
    .sort_values(['고객ID', '날짜'])
    # 인덱스 초기화
    .reset_index(drop=True)
)

print(f"\n처리 후 shape: {결과_체이닝.shape}")
print(f"\n처리 결과 (처음 10행):")
print(결과_체이닝.head(10))


# ============================================================
# 3. pipe()를 활용한 커스텀 변환 함수
# ============================================================
print("\n" + "=" * 60)
print("  3. pipe()를 활용한 커스텀 파이프라인")
print("=" * 60)


def 결측치_처리(df, 전략='중앙값'):
    """
    수치형 열의 결측치를 처리하는 함수.

    Parameters
    ----------
    df : pd.DataFrame
    전략 : str
        '삭제', '평균', '중앙값', '0', '보간' 중 선택

    Returns
    -------
    pd.DataFrame
    """
    df = df.copy()
    수치열 = df.select_dtypes(include=[np.number]).columns

    if 전략 == '삭제':
        df = df.dropna(subset=수치열)
    elif 전략 == '평균':
        df[수치열] = df[수치열].fillna(df[수치열].mean())
    elif 전략 == '중앙값':
        df[수치열] = df[수치열].fillna(df[수치열].median())
    elif 전략 == '0':
        df[수치열] = df[수치열].fillna(0)
    elif 전략 == '보간':
        df[수치열] = df[수치열].interpolate(method='linear')

    print(f"  [결측치 처리] 전략: {전략}, 결측치 수: {df.isna().sum().sum()}")
    return df


def 이상값_제거(df, 열='금액', 방법='IQR'):
    """
    IQR 방법으로 이상값을 제거하는 함수.
    """
    df = df.copy()
    Q1 = df[열].quantile(0.25)
    Q3 = df[열].quantile(0.75)
    IQR = Q3 - Q1
    하한 = Q1 - 1.5 * IQR
    상한 = Q3 + 1.5 * IQR
    이전크기 = len(df)
    df = df[(df[열] >= 하한) & (df[열] <= 상한)]
    제거수 = 이전크기 - len(df)
    print(f"  [이상값 제거] 열: {열}, 범위: [{하한:.0f}, {상한:.0f}], 제거: {제거수}개")
    return df


def 피처_엔지니어링(df):
    """
    파생 변수를 생성하는 피처 엔지니어링 함수.
    """
    df = df.copy()
    df['총금액'] = df['금액'] * df['수량']
    df['로그_금액'] = np.log1p(df['금액'])
    df['금액_구간'] = pd.qcut(df['금액'], q=4, labels=['저', '중저', '중고', '고'])
    print(f"  [피처 엔지니어링] 추가된 열: 총금액, 로그_금액, 금액_구간")
    return df


# pipe()로 연결
print("\n[pipe() 파이프라인 실행]")
최종_결과 = (
    df
    .pipe(결측치_처리, 전략='중앙값')
    .pipe(이상값_제거, 열='금액')
    .pipe(피처_엔지니어링)
)

print(f"\n최종 결과 shape: {최종_결과.shape}")
print(최종_결과.head())


# ============================================================
# 4. 결측치 처리 전략 비교
# ============================================================
print("\n" + "=" * 60)
print("  4. 결측치 처리 전략별 결과 비교")
print("=" * 60)

전략들 = ['삭제', '평균', '중앙값', '0', '보간']
전략_결과 = {}

for 전략 in 전략들:
    처리됨 = 결측치_처리(df, 전략=전략)
    전략_결과[전략] = {
        '행 수': len(처리됨),
        '금액_평균': 처리됨['금액'].mean(),
        '금액_중앙값': 처리됨['금액'].median(),
        '금액_표준편차': 처리됨['금액'].std(),
    }

비교_df = pd.DataFrame(전략_결과).T
print(f"\n전략별 비교:")
print(비교_df.round(1))


# ============================================================
# 5. 그룹별 변환 (GroupBy + Transform/Apply)
# ============================================================
print("\n" + "=" * 60)
print("  5. 그룹별 변환 (GroupBy)")
print("=" * 60)

# 결측치 먼저 처리
df_처리 = df.pipe(결측치_처리, 전략='중앙값')

# --- 그룹별 통계 ---
print("\n[고객별 집계]")
고객별_집계 = df_처리.groupby('고객ID').agg(
    거래횟수=('금액', 'count'),
    총매출=('금액', 'sum'),
    평균금액=('금액', 'mean'),
    최대금액=('금액', 'max'),
    평균수량=('수량', 'mean')
).round(0)
print(고객별_집계)

# --- groupby + transform: 그룹 통계를 원래 행에 매핑 ---
print("\n[그룹별 Z-score 표준화 (transform)]")
df_처리['금액_고객별_zscore'] = (
    df_처리.groupby('고객ID')['금액']
    .transform(lambda x: (x - x.mean()) / x.std())
)
print(df_처리[['고객ID', '금액', '금액_고객별_zscore']].head(10))

# --- 그룹별 순위 ---
print("\n[고객별 금액 순위]")
df_처리['금액_고객별_순위'] = (
    df_처리.groupby('고객ID')['금액']
    .rank(ascending=False, method='dense')
)
print(df_처리[['고객ID', '금액', '금액_고객별_순위']].head(10))

# --- 그룹별 누적합 ---
print("\n[고객별 누적 매출]")
df_처리 = df_처리.sort_values(['고객ID', '날짜'])
df_처리['누적매출'] = df_처리.groupby('고객ID')['금액'].cumsum()
print(df_처리[['고객ID', '날짜', '금액', '누적매출']].head(15))

# --- 그룹별 결측치 대체 (각 그룹의 평균으로) ---
print("\n[카테고리별 평균으로 결측치 대체]")
df_그룹대체 = df.copy()
df_그룹대체['금액'] = (
    df_그룹대체.groupby('카테고리')['금액']
    .transform(lambda x: x.fillna(x.mean()))
)
print(f"  대체 후 결측치: {df_그룹대체['금액'].isna().sum()}")


# ============================================================
# 6. 윈도우 함수 (Rolling/Expanding)
# ============================================================
print("\n" + "=" * 60)
print("  6. 윈도우 함수 (Rolling/Expanding)")
print("=" * 60)

# 일별 매출 데이터 생성
일별_매출 = (
    df_처리
    .set_index('날짜')
    .resample('D')['금액']
    .sum()
    .reset_index()
)
일별_매출.columns = ['날짜', '일별매출']

print(f"\n일별 매출 데이터: {len(일별_매출)}일")

# 이동 평균 (Moving Average)
일별_매출['7일_이동평균'] = 일별_매출['일별매출'].rolling(window=7).mean()
일별_매출['30일_이동평균'] = 일별_매출['일별매출'].rolling(window=30).mean()

# 이동 표준편차
일별_매출['7일_이동표준편차'] = 일별_매출['일별매출'].rolling(window=7).std()

# 누적 평균 (Expanding Mean)
일별_매출['누적평균'] = 일별_매출['일별매출'].expanding().mean()

# 볼린저 밴드 (Bollinger Bands)
일별_매출['상한밴드'] = 일별_매출['7일_이동평균'] + 2 * 일별_매출['7일_이동표준편차']
일별_매출['하한밴드'] = 일별_매출['7일_이동평균'] - 2 * 일별_매출['7일_이동표준편차']

print(일별_매출.head(15))


# ============================================================
# 7. 시각화
# ============================================================
fig, axes = plt.subplots(2, 2, figsize=(16, 10))

# (1) 결측치 전략 비교
전략_이름 = list(전략_결과.keys())
평균값들 = [v['금액_평균'] for v in 전략_결과.values()]
axes[0, 0].bar(전략_이름, 평균값들, color=['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6'],
               edgecolor='black')
axes[0, 0].axhline(y=df['금액'].mean(), color='gray', linestyle='--', alpha=0.5, label='원본 평균 (결측 제외)')
axes[0, 0].set_title('결측치 처리 전략별 평균 금액', fontsize=12, fontweight='bold')
axes[0, 0].set_ylabel('평균 금액 (원)')
axes[0, 0].legend()

# (2) 고객별 매출 분포 - 박스플롯
고객_데이터_list = []
고객_라벨 = []
for 고객 in sorted(df_처리['고객ID'].unique()):
    고객_데이터_list.append(df_처리[df_처리['고객ID'] == 고객]['금액'].values)
    고객_라벨.append(고객)
axes[0, 1].boxplot(고객_데이터_list, labels=고객_라벨)
axes[0, 1].set_title('고객별 금액 분포 (박스플롯)', fontsize=12, fontweight='bold')
axes[0, 1].set_ylabel('금액 (원)')

# (3) 일별 매출 + 이동 평균
axes[1, 0].plot(일별_매출['날짜'], 일별_매출['일별매출'], alpha=0.3, color='gray', label='일별 매출')
axes[1, 0].plot(일별_매출['날짜'], 일별_매출['7일_이동평균'], color='#e74c3c', linewidth=2, label='7일 이동평균')
axes[1, 0].plot(일별_매출['날짜'], 일별_매출['30일_이동평균'], color='#3498db', linewidth=2, label='30일 이동평균')
axes[1, 0].set_title('일별 매출과 이동 평균', fontsize=12, fontweight='bold')
axes[1, 0].set_ylabel('매출 (원)')
axes[1, 0].legend(fontsize=9)
axes[1, 0].tick_params(axis='x', rotation=45)

# (4) 볼린저 밴드
axes[1, 1].plot(일별_매출['날짜'], 일별_매출['일별매출'], alpha=0.3, color='gray', label='일별 매출')
axes[1, 1].plot(일별_매출['날짜'], 일별_매출['7일_이동평균'], color='#2ecc71', linewidth=2, label='7일 이동평균')
axes[1, 1].fill_between(일별_매출['날짜'],
                        일별_매출['하한밴드'],
                        일별_매출['상한밴드'],
                        alpha=0.2, color='#2ecc71', label='볼린저 밴드 (2 sigma)')
axes[1, 1].set_title('볼린저 밴드 (이상 탐지)', fontsize=12, fontweight='bold')
axes[1, 1].set_ylabel('매출 (원)')
axes[1, 1].legend(fontsize=9)
axes[1, 1].tick_params(axis='x', rotation=45)

plt.suptitle('Pandas 데이터 파이프라인: 결측치 처리, 그룹 변환, 윈도우 함수',
             fontsize=15, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('D:/26년1학기/기계학습/3장/구현소스/pandas_pipeline_결과.png',
            dpi=150, bbox_inches='tight')
plt.show()

print("\n" + "=" * 60)
print("  핵심 정리")
print("=" * 60)
print("""
[Pandas 파이프라인 핵심 패턴]

1. Method Chaining
   - .assign() -> .query() -> .sort_values() -> .reset_index()
   - 각 단계가 DataFrame을 반환하여 체이닝 가능

2. pipe()
   - 커스텀 함수를 파이프라인에 통합
   - df.pipe(함수1).pipe(함수2).pipe(함수3)
   - scikit-learn의 Pipeline과 유사한 개념

3. 결측치 처리 전략
   - 삭제: 데이터가 충분할 때 (편향 위험)
   - 평균/중앙값 대체: 가장 일반적 (분포 왜곡 주의)
   - 보간: 시계열 데이터에 적합
   - 그룹별 대체: 카테고리별 특성 반영

4. GroupBy + Transform
   - transform: 그룹 통계를 원래 행에 매핑 (Z-score 등)
   - apply: 그룹별 커스텀 함수 적용
   - rank: 그룹 내 순위 부여
   - cumsum: 그룹별 누적합

5. 윈도우 함수
   - rolling(n): 최근 n개 데이터의 이동 통계
   - expanding(): 처음부터 현재까지의 누적 통계
   - 활용: 이동 평균, 볼린저 밴드, 이상 탐지
""")
