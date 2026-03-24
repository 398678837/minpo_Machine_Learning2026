content = r"""

---

# 3. Pandas 심화: DataFrame의 세계

**판다스(Pandas)**는 파이썬에서 **표 형태(tabular)의 데이터**를 다루기 위한 핵심 라이브러리이다. McKinney (2010)가 금융 데이터 분석의 필요에 의해 개발을 시작했으며, 현재는 데이터 과학의 사실상 표준 도구이다.

```python
import pandas as pd
```

## 3.1 DataFrame 내부 구조

### 3.1.1 Series와 DataFrame의 관계

- **Series**: 인덱스가 부여된 1차원 배열. 내부적으로 NumPy ndarray를 감싼다.
- **DataFrame**: 여러 Series의 집합. 각 열이 독립적인 Series이며, 열마다 다른 dtype을 가질 수 있다.

```python
import pandas as pd
import numpy as np

# DataFrame 생성
df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 28],
    'score': [85.5, 92.3, 88.1]
})

# 각 열은 독립적인 Series
print(type(df['name']))    # <class 'pandas.core.series.Series'>
print(df['name'].dtype)    # object (문자열)
print(df['age'].dtype)     # int64
print(df['score'].dtype)   # float64
```

### 3.1.2 BlockManager 아키텍처

Pandas 2.0 이전의 내부 구조는 **BlockManager**로 구현되어 있었다. 같은 dtype의 열들을 하나의 NumPy 배열 블록으로 묶어 관리한다:

```
DataFrame
+-- BlockManager
    +-- IntBlock:    [age 열 데이터]         (int64 NumPy 배열)
    +-- FloatBlock:  [score 열 데이터]       (float64 NumPy 배열)
    +-- ObjectBlock: [name 열 데이터]        (object NumPy 배열)
    +-- Index:       [0, 1, 2]              (행 인덱스)
    +-- Columns:     ['name', 'age', 'score'] (열 이름)
```

Pandas 2.0부터는 선택적으로 **Apache Arrow 백엔드**를 사용할 수 있어, 특히 문자열 처리 성능이 크게 향상되었다.

### 3.1.3 데이터 입출력 (I/O)

Pandas는 거의 모든 데이터 형식을 지원한다 (Reback et al., 2020):

| 형식 | 읽기 | 쓰기 | 특징 |
|------|------|------|------|
| CSV | `pd.read_csv()` | `df.to_csv()` | 가장 범용적, 텍스트 기반 |
| Excel | `pd.read_excel()` | `df.to_excel()` | 비개발자와 공유 시 |
| SQL | `pd.read_sql()` | `df.to_sql()` | 데이터베이스 연동 |
| JSON | `pd.read_json()` | `df.to_json()` | API 데이터 |
| Parquet | `pd.read_parquet()` | `df.to_parquet()` | 대용량, 컬럼 기반, 고효율 |
| Feather | `pd.read_feather()` | `df.to_feather()` | 빠른 직렬화 |

```python
# CSV 파일 읽기
df = pd.read_csv('data.csv', encoding='utf-8', index_col=0)

# 주요 매개변수
# - filepath_or_buffer: 파일 경로 또는 URL
# - sep: 구분자 (기본 ',')
# - encoding: 인코딩 ('utf-8', 'cp949')
# - index_col: 인덱스로 사용할 열
# - header: 헤더 행 번호
# - dtype: 열별 타입 지정
# - parse_dates: 날짜 파싱할 열
# - na_values: 결측치로 인식할 값
# - usecols: 읽어올 열 지정 (메모리 절약)
# - chunksize: 대용량 파일 청크 단위 읽기
```

### 3.1.4 데이터 탐색 함수

```python
import pandas as pd

sample = pd.DataFrame({
    'Var_1': [1, 3, 2, 5, 3, 1, 2, 5, 6, 7, 7, 8, 9, 3, 2, 1, 2, 2, 3],
    'Var_2': [2, 4, 5, 6, 2, 1, 6, 7, 8, 4, 7, 3, 7, 9, 2, 3, 6, 4, 3]
})

# 기본 탐색
sample.head()          # 처음 5행
sample.tail(10)        # 마지막 10행
sample.info()          # 구조 정보 (타입, 결측치, 메모리)
sample.describe()      # 기술 통계량
sample.shape           # (19, 2)
sample.dtypes          # 열별 타입
sample.columns         # 열 이름 목록
sample.index           # 인덱스 정보
```

| 함수 | 용도 | 반환값 |
|------|------|--------|
| `head(n)` | 처음 n행 | DataFrame |
| `tail(n)` | 마지막 n행 | DataFrame |
| `info()` | 구조 정보 | None (출력) |
| `describe()` | 기술 통계량 | DataFrame |
| `shape` | 행/열 수 | 튜플 |
| `dtypes` | 열별 타입 | Series |

---

## 3.2 인덱싱 최적화

### 3.2.1 loc vs iloc 비교

| 구분 | `loc` | `iloc` |
|------|-------|--------|
| 기준 | 인덱스 **이름** (Label) | 정수 **위치** (Integer) |
| 슬라이싱 끝 값 | **포함** | **미포함** |
| 사용 예 | `df.loc['a':'c']` | `df.iloc[0:3]` |

```python
sample_df = pd.DataFrame(
    {'var_1': [2, 4, 5, 1, 4], 'var_2': [2, 3, 4, 4, 5]},
    index=['a', 'b', 'c', 'd', 'e']
)

# loc: 라벨 기반 (끝 값 포함)
sample_df.loc['a':'c']          # a, b, c 행
sample_df.loc['a':'c', 'var_1'] # a~c 행의 var_1 열

# iloc: 위치 기반 (끝 값 미포함)
sample_df.iloc[0:3]             # 0, 1, 2번 행
sample_df.iloc[0:3, 0:1]       # 0~2행, 0열
```

### 3.2.2 조건 기반 필터링 (불리언 인덱싱)

```python
# 단일 조건
df[df['score'] > 80]

# 복합 조건 (& : AND, | : OR, ~ : NOT)
df[(df['age'] >= 25) & (df['score'] > 80)]

# query() 메서드 (더 읽기 쉬움)
df.query('age >= 25 and score > 80')
df.query('name in ["Alice", "Bob"]')
```

### 3.2.3 인덱스 최적화 팁

```python
# set_index(): 특정 열을 인덱스로 설정
df = df.set_index('key')

# reset_index(): 인덱스를 열로 복원
df = df.reset_index()
df = df.reset_index(drop=True)   # 기존 인덱스 버림

# 인덱스 정렬 (검색 성능 향상)
df = df.sort_index()
```

---

## 3.3 메서드 체이닝 패턴

현대적 Pandas 코드의 핵심은 **메서드 체이닝(Method Chaining)**이다. 각 메서드가 DataFrame을 반환하므로, 점(`.`)으로 연결하여 파이프라인을 구성할 수 있다.

### 3.3.1 기본 패턴

```python
result = (
    df
    .copy()
    .assign(
        year=lambda x: x['date'].dt.year,
        month=lambda x: x['date'].dt.month
    )
    .dropna(subset=['amount'])
    .query('amount < @df["amount"].quantile(0.99)')
    .assign(total=lambda x: x['amount'] * x['quantity'].fillna(1))
    .sort_values(['customer_id', 'date'])
    .reset_index(drop=True)
)
```

### 3.3.2 pipe()를 활용한 커스텀 변환

`pipe()`는 커스텀 함수를 체이닝에 통합하는 핵심 메서드이다:

```python
def handle_missing(df, strategy='median'):
    """결측치 처리 함수."""
    df = df.copy()
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if strategy == 'drop':
        df = df.dropna(subset=numeric_cols)
    elif strategy == 'mean':
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
    elif strategy == 'median':
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
    elif strategy == 'zero':
        df[numeric_cols] = df[numeric_cols].fillna(0)
    elif strategy == 'interpolate':
        df[numeric_cols] = df[numeric_cols].interpolate(method='linear')
    return df

def remove_outliers(df, column='amount', method='IQR'):
    """IQR 방법으로 이상값 제거."""
    df = df.copy()
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    return df[(df[column] >= lower) & (df[column] <= upper)]

def feature_engineering(df):
    """파생 변수 생성."""
    df = df.copy()
    df['total'] = df['amount'] * df['quantity']
    df['log_amount'] = np.log1p(df['amount'])
    df['amount_bin'] = pd.qcut(df['amount'], q=4, labels=['low', 'mid_low', 'mid_high', 'high'])
    return df

# pipe()로 연결
result = (
    df
    .pipe(handle_missing, strategy='median')
    .pipe(remove_outliers, column='amount')
    .pipe(feature_engineering)
)
```

이 패턴은 scikit-learn의 Pipeline과 유사한 개념으로, 각 변환 단계를 독립적으로 테스트하고 재사용할 수 있게 해준다.

---

## 3.4 GroupBy 심화

McKinney (2010)는 Hadley Wickham의 **split-apply-combine** 전략을 Pandas에 구현했다.

### 3.4.1 Split-Apply-Combine 패턴

```
전체 데이터 --[Split]--> 그룹1, 그룹2, ...
                         --[Apply]--> 결과1, 결과2, ...
                                      --[Combine]--> 최종 결과
```

### 3.4.2 기본 집계

```python
import pandas as pd

iris = pd.DataFrame({
    'sepal_length': [5.1, 4.9, 7.0, 6.4, 6.3, 5.8],
    'sepal_width':  [3.5, 3.0, 3.2, 3.2, 3.3, 2.7],
    'species': ['setosa', 'setosa', 'versicolor', 'versicolor', 'virginica', 'virginica']
})

# 단일 집계
iris.groupby('species')['sepal_length'].mean()

# 다중 집계
iris.groupby('species')['sepal_length'].agg(['mean', 'std', 'count'])

# Named Aggregation (권장 패턴)
iris.groupby('species').agg(
    mean_sl=('sepal_length', 'mean'),
    max_sl=('sepal_length', 'max'),
    count=('sepal_length', 'count')
)
```

### 3.4.3 transform: 그룹 통계를 원래 행에 매핑

```python
# 그룹별 Z-score 표준화
df['amount_zscore'] = (
    df.groupby('customer_id')['amount']
    .transform(lambda x: (x - x.mean()) / x.std())
)

# 그룹별 순위
df['rank_in_group'] = (
    df.groupby('customer_id')['amount']
    .rank(ascending=False, method='dense')
)

# 그룹별 누적합
df['cumulative_amount'] = (
    df.groupby('customer_id')['amount'].cumsum()
)

# 그룹별 결측치 대체 (각 그룹의 평균으로)
df['amount_filled'] = (
    df.groupby('category')['amount']
    .transform(lambda x: x.fillna(x.mean()))
)
```

### 3.4.4 윈도우 함수 (Rolling/Expanding)

```python
# 이동 평균 (Moving Average)
df['ma_7'] = df['daily_sales'].rolling(window=7).mean()
df['ma_30'] = df['daily_sales'].rolling(window=30).mean()

# 이동 표준편차
df['std_7'] = df['daily_sales'].rolling(window=7).std()

# 누적 평균
df['expanding_mean'] = df['daily_sales'].expanding().mean()

# 볼린저 밴드 (이상 탐지에 활용)
df['upper_band'] = df['ma_7'] + 2 * df['std_7']
df['lower_band'] = df['ma_7'] - 2 * df['std_7']
```

---

## 3.5 Merge와 Join 심화

### 3.5.1 merge()의 4가지 방식

```python
left = pd.DataFrame({'key': ['a', 'b', 'c', 'd', 'e'], 'val_1': [1, 3, 4, 2, 1]})
right = pd.DataFrame({'key': ['b', 'c', 'e', 'f', 'g'], 'val_2': [4, 6, 3, 2, 3]})

# Inner Join: 교집합
left.merge(right, on='key', how='inner')

# Outer Join: 합집합
left.merge(right, on='key', how='outer')

# Left Join: 왼쪽 기준
left.merge(right, on='key', how='left')

# Right Join: 오른쪽 기준
left.merge(right, on='key', how='right')
```

```
left의 key:  {a, b, c, d, e}
right의 key: {b, c, e, f, g}

Inner Join:  {b, c, e}             <-- 교집합
Outer Join:  {a, b, c, d, e, f, g} <-- 합집합
Left Join:   {a, b, c, d, e}      <-- 왼쪽 전체
Right Join:  {b, c, e, f, g}      <-- 오른쪽 전체
```

### 3.5.2 merge, join, concat 비교

| 함수 | 결합 기준 | 방향 | 기본 Join |
|------|----------|------|-----------|
| `merge()` | 공통 열 (key) | 좌우 | inner |
| `join()` | 인덱스 | 좌우 | left |
| `concat()` | 인덱스 | 위아래/좌우 | outer |

---

## 3.6 Pivot과 Reshape

### 3.6.1 pivot_table()

```python
# 월별-카테고리별 매출 교차 집계
sales.pivot_table(
    values='amount',
    index='month',
    columns='category',
    aggfunc='sum',
    fill_value=0,
    margins=True         # 합계 행/열 추가
)
```

### 3.6.2 melt() -- Wide to Long

```python
wide = pd.DataFrame({
    'name': ['Alice', 'Bob'],
    'math': [90, 78],
    'english': [85, 92]
})

long = wide.melt(
    id_vars='name',
    var_name='subject',
    value_name='score'
)
```

### 3.6.3 pivot() -- Long to Wide

```python
wide_again = long.pivot(
    index='name',
    columns='subject',
    values='score'
)
```

---

# 4. 데이터 전처리

데이터 전처리는 ML 파이프라인에서 가장 중요하고 시간이 많이 소요되는 단계이다.

## 4.1 결측치 처리 전략 5가지 비교

### 전략 1: 삭제 (Listwise Deletion)

```python
df_dropped = df.dropna()             # 결측치 있는 행 삭제
df_dropped = df.dropna(thresh=3)     # 비결측치가 3개 미만인 행 삭제
df_dropped = df.dropna(subset=['important_col'])  # 특정 열 기준
```

- **장점**: 구현이 간단, 편향 없는 완전 데이터
- **단점**: 데이터 손실, 결측이 MCAR(완전 무작위 결측)이 아니면 편향 발생
- **적합 상황**: 데이터가 충분하고 결측 비율이 낮을 때 (< 5%)

### 전략 2: 평균 대체 (Mean Imputation)

```python
df['col'] = df['col'].fillna(df['col'].mean())
```

- **장점**: 평균은 보존
- **단점**: 분산 축소, 상관관계 왜곡
- **적합 상황**: 결측 비율이 낮고 정규분포에 가까울 때

### 전략 3: 중앙값 대체 (Median Imputation)

```python
df['col'] = df['col'].fillna(df['col'].median())
```

- **장점**: 이상치에 강건(robust)
- **단점**: 역시 분산 축소
- **적합 상황**: 분포가 왜곡(skewed)되어 있을 때

### 전략 4: 0 또는 상수 대체

```python
df['col'] = df['col'].fillna(0)
```

- **장점**: 도메인 지식에 기반 가능
- **단점**: 분포 왜곡 가능
- **적합 상황**: 결측이 "해당 없음"을 의미할 때

### 전략 5: 보간법 (Interpolation)

```python
df['col'] = df['col'].interpolate(method='linear')
# 시계열: method='time', 'spline', 'polynomial' 등
```

- **장점**: 시간적 연속성 보존
- **단점**: 비시계열 데이터에는 부적절할 수 있음
- **적합 상황**: 시계열 데이터

### 고급: 그룹별 대체

```python
# 카테고리별 평균으로 대체 (가장 권장되는 방법 중 하나)
df['amount'] = (
    df.groupby('category')['amount']
    .transform(lambda x: x.fillna(x.mean()))
)
```

### 전략 비교 요약

| 전략 | 평균 보존 | 분산 보존 | 상관관계 보존 | 데이터 손실 |
|------|---------|---------|------------|-----------|
| 삭제 | O | O | O | O (행 손실) |
| 평균 대체 | O | X (축소) | X (약화) | X |
| 중앙값 대체 | 근사 | X (축소) | X (약화) | X |
| 0 대체 | X (왜곡) | X (왜곡) | X (왜곡) | X |
| 보간법 | 근사 | 근사 | 근사 | X |
| 그룹별 대체 | O (그룹별) | 부분 | 부분 | X |

---

## 4.2 이상치 탐지

### 4.2.1 IQR (사분위수 범위) 방법

사분위수 범위(Interquartile Range)를 기반으로 이상치를 탐지한다:

$$\text{IQR} = Q_3 - Q_1$$
$$\text{하한} = Q_1 - 1.5 \times \text{IQR}$$
$$\text{상한} = Q_3 + 1.5 \times \text{IQR}$$

```python
Q1 = df['amount'].quantile(0.25)
Q3 = df['amount'].quantile(0.75)
IQR = Q3 - Q1
lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR

outliers = df[(df['amount'] < lower) | (df['amount'] > upper)]
df_clean = df[(df['amount'] >= lower) & (df['amount'] <= upper)]

print(f"IQR: {IQR:.2f}")
print(f"정상 범위: [{lower:.2f}, {upper:.2f}]")
print(f"이상치 수: {len(outliers)}")
```

### 4.2.2 Z-score 방법

평균으로부터의 표준편차 거리를 기준으로 이상치를 탐지한다:

$$z = \frac{x - \mu}{\sigma}$$

일반적으로 $|z| > 3$인 값을 이상치로 판단한다.

```python
from scipy import stats

z_scores = np.abs(stats.zscore(df['amount'].dropna()))
outlier_mask = z_scores > 3
print(f"Z-score 이상치 수: {outlier_mask.sum()}")

# 또는 수동 계산
mean = df['amount'].mean()
std = df['amount'].std()
z = (df['amount'] - mean) / std
outliers = df[np.abs(z) > 3]
```

### 4.2.3 Isolation Forest

앙상블 기반의 비지도 이상치 탐지 알고리즘이다. 이상치는 정상 데이터보다 **고립(isolate)시키기 쉽다**는 원리에 기반한다.

```python
from sklearn.ensemble import IsolationForest

iso_forest = IsolationForest(contamination=0.05, random_state=42)
labels = iso_forest.fit_predict(df[['amount', 'quantity']])
# labels: 1 = 정상, -1 = 이상치

df['is_outlier'] = labels == -1
print(f"Isolation Forest 이상치 수: {df['is_outlier'].sum()}")
```

### 이상치 탐지 방법 비교

| 방법 | 가정 | 다변량 | 복잡도 | 적합 상황 |
|------|------|--------|-------|----------|
| IQR | 없음 | 단변량 | 낮음 | 탐색적 분석, 단일 변수 |
| Z-score | 정규분포 | 단변량 | 낮음 | 정규분포에 가까운 데이터 |
| Isolation Forest | 없음 | 다변량 | 중간 | 고차원, 복잡한 분포 |

---

## 4.3 피처 스케일링

ML 알고리즘은 특성(feature)의 스케일에 민감한 경우가 많다. 특히 거리 기반 알고리즘(KNN, SVM, K-Means)과 경사하강법 기반 알고리즘(선형회귀, 신경망)에서 스케일링은 필수적이다.

### 4.3.1 StandardScaler (Z-score 표준화)

평균을 0, 표준편차를 1로 변환한다:

$$x' = \frac{x - \mu}{\sigma}$$

```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 수동 구현 (NumPy)
X_manual = (X - X.mean(axis=0)) / X.std(axis=0)
```

- **장점**: 이상치에 의한 범위 왜곡이 적음, 대부분의 알고리즘에 적합
- **단점**: 정규분포를 가정
- **적합 알고리즘**: 선형회귀, 로지스틱회귀, SVM, PCA, 신경망

### 4.3.2 MinMaxScaler (최소-최대 정규화)

값을 $[0, 1]$ 범위로 변환한다:

$$x' = \frac{x - x_{\min}}{x_{\max} - x_{\min}}$$

```python
from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

# 수동 구현 (NumPy)
X_manual = (X - X.min(axis=0)) / (X.max(axis=0) - X.min(axis=0))
```

- **장점**: 직관적, 범위가 명확
- **단점**: 이상치에 매우 민감
- **적합 알고리즘**: 이미지 처리, 신경망 (입력 범위 제한)

### 4.3.3 RobustScaler (강건 스케일링)

중앙값과 IQR을 사용하여 이상치에 강건한 스케일링을 수행한다:

$$x' = \frac{x - \text{median}}{Q_3 - Q_1}$$

```python
from sklearn.preprocessing import RobustScaler

scaler = RobustScaler()
X_scaled = scaler.fit_transform(X)
```

- **장점**: 이상치에 강건
- **단점**: 범위가 [0,1]로 고정되지 않음
- **적합 상황**: 이상치가 많은 데이터

### 스케일링 방법 비교

| 방법 | 수식 | 이상치 민감도 | 범위 | 적합 상황 |
|------|------|-------------|------|----------|
| StandardScaler | $(x-\mu)/\sigma$ | 중간 | 고정 안 됨 | 대부분의 경우 |
| MinMaxScaler | $(x-\min)/(\max-\min)$ | 높음 | [0, 1] | 범위 제한 필요 시 |
| RobustScaler | $(x-\text{median})/\text{IQR}$ | 낮음 | 고정 안 됨 | 이상치 다수 |

> **주의**: 스케일링은 반드시 학습 데이터(train set)에 대해 `fit()`한 후, 테스트 데이터(test set)에는 동일한 파라미터로 `transform()`만 적용해야 한다. 테스트 데이터에 `fit_transform()`을 적용하면 **데이터 누출(data leakage)**이 발생한다.

---

# 5. Tidy Data 개념

## 5.1 Wickham의 Tidy Data 원칙

Hadley Wickham (2014)은 "Tidy Data" 논문에서 데이터 정리의 체계적 원칙을 제안했다. 이 원칙은 R의 tidyverse 생태계에서 출발했지만, Pandas를 포함한 모든 데이터 분석 도구에 보편적으로 적용된다.

### 5.1.1 세 가지 원칙

1. **각 변수(variable)는 하나의 열(column)을 구성한다.**
2. **각 관측(observation)은 하나의 행(row)을 구성한다.**
3. **각 관측 단위(observational unit)의 유형은 하나의 테이블을 구성한다.**

### 5.1.2 깔끔한 데이터 vs 지저분한 데이터

```
깔끔한 형태 (Long format):          지저분한 형태 (Wide format):
+--------+------+------+           +--------+------+------+
| name   | subj | score|           | name   | math | eng  |
+--------+------+------+           +--------+------+------+
| Alice  | math | 90   |           | Alice  | 90   | 85   |
| Alice  | eng  | 85   |           | Bob    | 78   | 92   |
| Bob    | math | 78   |           +--------+------+------+
| Bob    | eng  | 92   |
+--------+------+------+
```

왼쪽이 깔끔한 형태이다. 'subj'와 'score'가 각각 하나의 열이다.

## 5.2 지저분한 데이터의 다섯 가지 유형

### 유형 1: 열 헤더가 변수명이 아닌 값

```python
# 지저분한 형태
messy = pd.DataFrame({
    'name': ['Alice', 'Bob'],
    '2023': [85, 92],
    '2024': [90, 88]
})

# 깔끔한 형태로 변환 (melt)
tidy = messy.melt(
    id_vars='name',
    var_name='year',
    value_name='score'
)
```

### 유형 2: 하나의 열에 여러 변수 저장

```python
messy = pd.DataFrame({
    'item': ['math_mid', 'math_final', 'eng_mid', 'eng_final'],
    'score': [85, 90, 78, 88]
})

# 문자열 분리로 해결
split_cols = messy['item'].str.split('_', expand=True)
split_cols.columns = ['subject', 'exam']
tidy = pd.concat([split_cols, messy['score']], axis=1)
```

### 유형 3: 변수가 행과 열에 걸쳐 저장

melt와 pivot의 조합으로 해결한다.

### 유형 4: 하나의 테이블에 여러 관측 단위 혼재

정규화(normalization)를 통해 별도 테이블로 분리한다.

### 유형 5: 하나의 관측 단위가 여러 테이블에 분산

```python
import glob
files = glob.glob('data/sales_*.csv')
dfs = [pd.read_csv(f) for f in files]
combined = pd.concat(dfs, ignore_index=True)
```

## 5.3 깔끔한 데이터의 장점

1. **분석 코드 재사용**: 동일한 코드로 다양한 데이터셋 분석 가능
2. **시각화 단순화**: seaborn 등의 도구가 자동으로 올바르게 매핑
3. **ML 파이프라인 호환**: scikit-learn이 요구하는 "행=샘플, 열=특성" 형식과 일치

```python
import seaborn as sns

# 깔끔한 데이터 = seaborn에 바로 전달 가능
sns.boxplot(data=tidy, x='subject', y='score')
```

---

# 6. 벡터화 vs 루프: 성능의 과학

## 6.1 왜 NumPy가 빠른가?

### Python 루프가 느린 이유

1. **동적 타이핑**: 매 연산마다 타입 확인 필요 (약 5~10 CPU 명령어 추가)
2. **인터프리터 오버헤드**: 바이트코드를 해석하는 비용
3. **객체 오버헤드**: Python의 각 숫자는 PyObject (28+ bytes). 정수 하나에 포인터, 참조 카운트, 타입 포인터 등이 포함
4. **메모리 비연속**: 리스트의 원소가 메모리에 흩어져 있어 CPU 캐시 미스(cache miss) 빈발
5. **GIL**: 글로벌 인터프리터 락(Global Interpreter Lock)이 싱글 스레드 실행을 강제

### NumPy가 빠른 이유

1. **C/Fortran 내부 루프**: 컴파일된 네이티브 코드로 실행. 인터프리터 오버헤드 없음
2. **동질적 타입**: 배열의 모든 원소가 같은 타입이므로 타입 확인이 한 번만 필요
3. **연속 메모리**: CPU 캐시 효율 극대화. 현대 CPU의 L1 캐시 라인(64 bytes)에 float64 8개가 딱 맞음
4. **BLAS/LAPACK**: 수십 년간 최적화된 수치 라이브러리. 행렬곱은 이론적 최적에 근접한 성능
5. **SIMD (Single Instruction, Multiple Data)**: AVX/SSE 등 벡터 명령어를 통해 하나의 명령어로 4~8개의 부동소수점 연산을 동시 수행
6. **GIL 해제**: NumPy의 C 확장은 GIL을 해제하여 멀티코어 활용 가능

## 6.2 하드웨어 수준의 설명

### SIMD (Single Instruction, Multiple Data)

```
Python 루프 (스칼라 처리):
  명령어 1: a[0] + b[0] = c[0]
  명령어 2: a[1] + b[1] = c[1]
  명령어 3: a[2] + b[2] = c[2]
  명령어 4: a[3] + b[3] = c[3]
  ... (N번 반복)

NumPy SIMD (벡터 처리, AVX-256):
  명령어 1: [a[0], a[1], a[2], a[3]] + [b[0], b[1], b[2], b[3]]
            = [c[0], c[1], c[2], c[3]]
  ... (N/4번 반복)
```

AVX-256은 256비트 레지스터를 사용하여 float64 4개를 동시에 처리한다. AVX-512는 8개를 동시에 처리한다.

### CPU 캐시 효율

```
Python 리스트 (비연속 메모리):
  캐시 라인 1: [포인터1] -> [PyObject at 0x7f...100]  <-- 캐시 미스!
  캐시 라인 2: [포인터2] -> [PyObject at 0x7f...200]  <-- 캐시 미스!
  ... (매번 다른 메모리 주소 접근 -> 캐시 효율 낮음)

NumPy 배열 (연속 메모리):
  캐시 라인 1: [val1, val2, val3, val4, val5, val6, val7, val8]
  캐시 라인 2: [val9, val10, val11, ...]
  ... (순차 접근 -> 캐시 프리페치 효과 -> 캐시 효율 극대화)
```

## 6.3 벤치마크 결과

### 유클리드 거리 계산

```python
def distance_python_loop(X, Y):
    """Python 중첩 루프로 쌍별 유클리드 거리를 계산."""
    n, m = len(X), len(Y)
    D = [[0.0] * m for _ in range(n)]
    for i in range(n):
        for j in range(m):
            s = 0
            for k in range(len(X[0])):
                s += (X[i][k] - Y[j][k]) ** 2
            D[i][j] = s ** 0.5
    return D

def distance_numpy(X, Y):
    """NumPy 브로드캐스팅으로 쌍별 유클리드 거리를 계산."""
    diff = X[:, np.newaxis, :] - Y[np.newaxis, :, :]
    return np.sqrt(np.sum(diff ** 2, axis=2))

def distance_numpy_optimized(X, Y):
    """(a-b)^2 = a^2 + b^2 - 2ab 공식으로 최적화."""
    X_sq = np.sum(X ** 2, axis=1, keepdims=True)
    Y_sq = np.sum(Y ** 2, axis=1, keepdims=True)
    cross = X @ Y.T
    return np.sqrt(np.maximum(X_sq + Y_sq.T - 2 * cross, 0))
```

실제 벤치마크에서의 일반적인 결과:

| 데이터 크기 (n) | Python 루프 | NumPy | NumPy 최적화 | 속도비 |
|----------------|------------|-------|-------------|--------|
| 50 | 0.03s | 0.0002s | 0.0001s | ~300x |
| 100 | 0.20s | 0.0005s | 0.0002s | ~1,000x |
| 200 | 1.50s | 0.002s | 0.0004s | ~3,750x |
| 500 | 25.0s | 0.012s | 0.002s | ~12,500x |

### 메모리 비교

```python
import sys
n = 1_000_000
python_list = list(range(n))
numpy_array = np.arange(n, dtype=np.int64)

# Python 리스트: 약 28 MB (각 원소가 PyObject)
# NumPy 배열: 약 7.6 MB (연속 int64)
# 메모리 절약: 약 3.7배
```

## 6.4 실전 가이드

1. **수치 연산에는 절대로 Python 루프를 사용하지 말 것**
2. NumPy **브로드캐스팅**을 최대한 활용할 것
3. 벡터화가 어려운 경우: **numba** 또는 **cython** 사용 고려
4. 대규모 데이터: **Dask**, **CuPy(GPU)** 사용 고려
5. Pandas에서도 `.apply()`보다 **벡터화된 메서드**(`.str`, `.dt`, 직접 연산)를 우선 사용

"""

with open("D:/26년1학기/기계학습/3장/한글강의록.md", "a", encoding="utf-8") as f:
    f.write(content)

print("Part 2 written successfully")
