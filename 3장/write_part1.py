import os

content = r"""# 3장: 판다스(Pandas)와 넘파이(NumPy) -- 박사 수준 심화 강의록

> **과목**: 기계학습 (Machine Learning)
> **범위**: 3장 -- 데이터 처리의 핵심 도구
> **수준**: 대학원 박사과정
> **키워드**: NumPy, Pandas, ndarray, DataFrame, 벡터화, 브로드캐스팅, 선형대수, 데이터 파이프라인, Tidy Data

---

## 학습 목표

본 장을 이수한 후 학습자는 다음을 수행할 수 있어야 한다.

1. NumPy ndarray의 내부 메모리 구조(stride, dtype, C-order/F-order)를 설명하고, 성능 최적화에 활용할 수 있다.
2. 브로드캐스팅 규칙을 정확히 적용하여 다양한 형태의 배열 간 연산을 수행할 수 있다.
3. LU/QR/SVD/고유값 분해를 NumPy로 구현하고, 각 분해가 ML 알고리즘(PCA, 선형회귀 등)에서 어떻게 활용되는지 설명할 수 있다.
4. Pandas DataFrame의 내부 구조를 이해하고, method chaining과 pipe()를 사용한 데이터 파이프라인을 구성할 수 있다.
5. 결측치 처리 5가지 전략, 이상치 탐지 3가지 방법, 피처 스케일링 3가지 방법을 비교 분석할 수 있다.
6. Wickham의 Tidy Data 원칙을 적용하여 messy data를 tidy data로 변환할 수 있다.
7. 벡터화 연산과 Python 루프의 성능 차이를 하드웨어 수준(SIMD, 캐시)에서 설명할 수 있다.

---

## 목차

1. [도입: 데이터 없이는 ML도 없다](#1-도입-데이터-없이는-ml도-없다)
2. [NumPy 심화: ndarray의 세계](#2-numpy-심화-ndarray의-세계)
3. [Pandas 심화: DataFrame의 세계](#3-pandas-심화-dataframe의-세계)
4. [데이터 전처리](#4-데이터-전처리)
5. [Tidy Data 개념](#5-tidy-data-개념)
6. [벡터화 vs 루프: 성능의 과학](#6-벡터화-vs-루프-성능의-과학)
7. [논문 리뷰 통합](#7-논문-리뷰-통합)
8. [구현 코드 상세 해설](#8-구현-코드-상세-해설)
9. [보충 자료](#9-보충-자료)
10. [실무 데이터 파이프라인](#10-실무-데이터-파이프라인)
11. [핵심 요약 및 복습 질문](#11-핵심-요약-및-복습-질문)
12. [참고 문헌](#12-참고-문헌)

---

# 1. 도입: 데이터 없이는 ML도 없다

## 1.1 데이터 과학에서 NumPy와 Pandas의 역할

기계학습(Machine Learning)은 본질적으로 **데이터로부터 패턴을 학습하는 기술**이다. 아무리 정교한 알고리즘이라 할지라도 양질의 데이터 없이는 유의미한 결과를 산출할 수 없다. Andrew Ng의 유명한 격언 "데이터가 왕이다(Data is King)"는 이 현실을 정확히 반영한다.

ML 프로젝트의 전형적인 워크플로우는 다음과 같다:

```
데이터 수집 --> 데이터 탐색(EDA) --> 데이터 전처리 --> 피처 엔지니어링
    --> 모델 학습 --> 모델 평가 --> 배포
```

이 워크플로우에서 **모델 학습 이전의 모든 단계**가 데이터 처리에 해당하며, 실무에서 데이터 과학자의 업무 시간 중 **50~80%**가 이 단계에 소비된다(Wickham, 2014). NumPy와 Pandas는 이 데이터 처리 단계의 핵심 도구이다.

### 파이썬 과학 생태계의 레이어 구조

Harris et al. (2020)의 Nature 논문에서 제시한 파이썬 과학 생태계의 레이어 구조는 NumPy의 위상을 명확히 보여준다:

```
+---------------------------------------------------+
|              응용 라이브러리 (Applications)           |
|     scikit-learn, TensorFlow, PyTorch, Keras       |
+---------------------------------------------------+
|           도메인별 라이브러리 (Domain-specific)        |
|     Pandas (표 형식), SciPy (과학 알고리즘)           |
|     matplotlib (시각화), scikit-image (이미지)       |
+---------------------------------------------------+
|                    NumPy                           |
|       ndarray, ufunc, broadcasting                 |
|       linear algebra, FFT, random                  |
+---------------------------------------------------+
|            Python + C Extensions                   |
+---------------------------------------------------+
```

NumPy는 이 생태계의 **기반 인프라(foundation infrastructure)**로 기능한다. Pandas의 DataFrame은 내부적으로 NumPy 배열을 감싸고(wrapping) 있으며, scikit-learn의 `fit()`과 `predict()` 메서드는 NumPy 배열을 입력으로 받는다. TensorFlow와 PyTorch의 텐서(Tensor)도 NumPy 배열과의 상호 변환을 기본 제공한다.

## 1.2 ML 파이프라인에서의 데이터 흐름

전형적인 ML 파이프라인에서 데이터는 다음과 같이 흐른다:

```python
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

# 1단계: Pandas로 데이터 로딩
df = pd.read_csv('data.csv')

# 2단계: Pandas로 탐색 및 전처리
df = df.dropna()
df['new_feature'] = df['feature_a'] * df['feature_b']

# 3단계: NumPy 배열로 변환
X = df[['feature_a', 'feature_b', 'new_feature']].to_numpy()
y = df['target'].to_numpy()

# 4단계: scikit-learn으로 모델링 (내부적으로 NumPy 연산)
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
model = LogisticRegression()
model.fit(X_train_scaled, y_train)
```

이 파이프라인에서 볼 수 있듯이, **Pandas는 데이터의 로딩, 탐색, 전처리를 담당**하고, **NumPy는 수치 연산의 기반**을 제공한다.

## 1.3 왜 파이썬인가?

파이썬이 데이터 과학과 ML의 사실상 표준 언어가 된 이유의 핵심은 **"접착 언어(glue language)"**로서의 역할에 있다. 파이썬 자체는 느리지만, 성능이 중요한 부분은 C/Fortran으로 작성된 라이브러리(BLAS, LAPACK 등)가 처리한다. NumPy는 이 전략의 대표적 성공 사례이다.

McKinney (2010)는 Pandas를 개발한 동기를 다음과 같이 설명한다:

> "파이썬에는 R의 data.frame에 대응하는 고수준 데이터 구조가 없었다. NumPy의 ndarray는 동질적 수치 데이터에는 탁월하지만, 이질적 표 형식 데이터를 다루기에는 부족했다."

이 간극을 메우기 위해 Pandas가 탄생했고, NumPy + Pandas의 조합은 파이썬을 데이터 과학의 지배적 언어로 만드는 데 결정적 역할을 했다.

---

# 2. NumPy 심화: ndarray의 세계

넘파이(NumPy, Numerical Python)는 파이썬에서 **수치 계산**을 위한 핵심 라이브러리이다. 고성능 **다차원 배열(ndarray)** 객체와 이를 다루기 위한 다양한 함수를 제공한다.

```python
import numpy as np
```

## 2.1 ndarray 내부 구조

### 2.1.1 네 가지 핵심 구성 요소

Walt et al. (2011)이 상세히 기술한 바와 같이, ndarray는 네 가지 핵심 요소로 구성된다:

```
ndarray
+-- data    : 데이터가 저장된 메모리 버퍼의 포인터
+-- dtype   : 각 원소의 데이터 타입 (float64, int32 등)
+-- shape   : 각 차원의 크기를 나타내는 튜플
+-- strides : 각 차원에서 다음 원소까지의 바이트 수
```

```python
import numpy as np

arr = np.array([[1.0, 2.0, 3.0],
                [4.0, 5.0, 6.0]])

print(f"dtype:   {arr.dtype}")       # float64
print(f"shape:   {arr.shape}")       # (2, 3)
print(f"strides: {arr.strides}")     # (24, 8)
print(f"nbytes:  {arr.nbytes}")      # 48 = 2 * 3 * 8 bytes
print(f"ndim:    {arr.ndim}")        # 2
print(f"size:    {arr.size}")        # 6
```

### 2.1.2 메모리 레이아웃과 Stride

ndarray는 **연속 메모리 블록(contiguous memory block)**에 동질적 타입의 데이터를 저장한다. 이것이 Python 리스트와의 근본적인 차이이다.

**Python 리스트의 메모리 구조:**
```
리스트 객체 --> [포인터1, 포인터2, 포인터3, ...]
                  |          |          |
                  v          v          v
              PyObject   PyObject   PyObject
              (28+ bytes)(28+ bytes)(28+ bytes)
```

**NumPy 배열의 메모리 구조:**
```
ndarray 객체 --> [8 bytes | 8 bytes | 8 bytes | ...]
                  값1       값2       값3
                  (연속된 메모리 블록)
```

Stride는 각 차원에서 다음 원소로 이동하는 데 필요한 **바이트 수**이다:

```
2x3 float64 배열의 메모리 레이아웃 (C-order):

메모리: [1.0][2.0][3.0][4.0][5.0][6.0]
바이트:  0    8   16   24   32   40

shape = (2, 3)
strides = (24, 8)
  - 행 방향 (axis=0): 24바이트 = 3원소 x 8바이트/원소
  - 열 방향 (axis=1): 8바이트  = 1원소 x 8바이트/원소
```

```python
# Stride 확인 예제
a = np.array([[1, 2, 3, 4],
              [5, 6, 7, 8],
              [9, 10, 11, 12]], dtype=np.float64)

print(f"shape: {a.shape}")        # (3, 4)
print(f"strides: {a.strides}")    # (32, 8)

# 전치(transpose)는 stride만 바꾼다 (데이터 복사 없음!)
b = a.T
print(f"전치 shape: {b.shape}")      # (4, 3)
print(f"전치 strides: {b.strides}")  # (8, 32)
```

### 2.1.3 C-order vs Fortran-order

| 순서 | 메모리 레이아웃 | 빠른 접근 방향 | 사용 예 |
|------|---------------|--------------|---------|
| C-order (row-major) | 행 우선 저장 | 마지막 축 (열 방향) | NumPy 기본값, C 언어 |
| F-order (column-major) | 열 우선 저장 | 첫 번째 축 (행 방향) | Fortran, MATLAB, R |

```python
arr_c = np.array([[1, 2, 3], [4, 5, 6]], order='C')
arr_f = np.array([[1, 2, 3], [4, 5, 6]], order='F')

print(f"C-order strides: {arr_c.strides}")    # (24, 8)
print(f"F-order strides: {arr_f.strides}")    # (8, 16)
```

**성능 시사점**: 행 방향 순회 시 C-order가, 열 방향 순회 시 F-order가 CPU 캐시 효율이 높다.

### 2.1.4 dtype 시스템

| 카테고리 | dtype | 바이트 | 범위/정밀도 |
|---------|-------|-------|------------|
| 정수 | `int8` | 1 | $-128$ ~ $127$ |
| 정수 | `int16` | 2 | $-32{,}768$ ~ $32{,}767$ |
| 정수 | `int32` | 4 | $\approx \pm 2.1 \times 10^9$ |
| 정수 | `int64` | 8 | $\approx \pm 9.2 \times 10^{18}$ |
| 부호 없는 정수 | `uint8` | 1 | $0$ ~ $255$ (이미지 픽셀) |
| 부동소수점 | `float16` | 2 | 반정밀도 (딥러닝 추론) |
| 부동소수점 | `float32` | 4 | 단정밀도 (딥러닝 학습) |
| 부동소수점 | `float64` | 8 | 배정밀도 (과학 계산 기본값) |
| 복소수 | `complex128` | 16 | 신호 처리, 양자 역학 |
| 불리언 | `bool_` | 1 | True/False |

### 2.1.5 배열 생성 함수 총정리

```python
import numpy as np

# === 기본 생성 ===
np.array([1, 2, 3])
np.array([[1, 2], [3, 4]], dtype=float)

# === 초기화 생성 ===
np.zeros((3, 4))           # 0으로 채운 3x4 행렬
np.ones((2, 3))            # 1로 채운 2x3 행렬
np.full((2, 3), 7)         # 7로 채운 2x3 행렬
np.empty((3, 3))           # 초기화 없이 메모리 할당
np.eye(4)                  # 4x4 단위행렬
np.diag([1, 2, 3])         # 대각행렬

# === 범위 생성 ===
np.arange(0, 10, 2)        # [0, 2, 4, 6, 8]
np.linspace(0, 1, 5)       # [0, 0.25, 0.5, 0.75, 1.0]
np.logspace(0, 3, 4)       # [1, 10, 100, 1000]

# === 난수 생성 ===
np.random.seed(42)
np.random.rand(3, 4)                        # 균등분포 U(0,1)
np.random.randn(3, 4)                       # 표준정규분포 N(0,1)
np.random.randint(0, 10, size=(3, 4))       # 정수 난수
np.random.normal(0, 1, size=(100,))         # 정규분포
np.random.choice(['a', 'b', 'c'], size=5)   # 임의 선택
```

### 2.1.6 배열 인덱싱과 슬라이싱

NumPy는 네 가지 인덱싱 방법을 지원한다 (Harris et al., 2020):

```python
arr = np.array([[1, 2, 3, 4],
                [5, 6, 7, 8],
                [9, 10, 11, 12]])

# 1. 기본 인덱싱 (Basic Indexing)
arr[0, 1]           # 2

# 2. 슬라이싱 (Slicing) -- 뷰(view) 반환
arr[0:2, 1:3]       # [[2, 3], [6, 7]]
arr[:, 2]           # [3, 7, 11]

# 3. 팬시 인덱싱 (Fancy Indexing) -- 카피(copy) 반환
arr[[0, 2], [1, 3]] # [2, 12]

# 4. 불리언 인덱싱 (Boolean Indexing)
arr[arr > 5]        # [6, 7, 8, 9, 10, 11, 12]
```

---

## 2.2 브로드캐스팅 (Broadcasting)

브로드캐스팅은 NumPy의 가장 강력하고도 미묘한 기능 중 하나이다. Walt et al. (2011)은 이를 "크기가 다른 배열 간의 연산을 자동으로 수행하는 메커니즘"으로 정의한다.

### 2.2.1 브로드캐스팅의 세 가지 규칙

**규칙 1**: 두 배열의 차원 수가 다르면, 차원 수가 적은 배열의 shape **앞에** 1을 추가한다.

**규칙 2**: 각 차원에서 크기가 같거나, 둘 중 하나가 1이면 **호환(compatible)**된다.

**규칙 3**: 크기가 1인 차원은 다른 배열의 크기에 맞게 **가상으로 확장(stretch)**된다.

### 2.2.2 시각적 설명

```
예제 1: (3, 3) + (3,)
---
배열 A: shape (3, 3)     배열 b: shape (3,) -> (1, 3) -> (3, 3)

[a00 a01 a02]     [b0 b1 b2]     [a00+b0  a01+b1  a02+b2]
[a10 a11 a12]  +  [b0 b1 b2]  =  [a10+b0  a11+b1  a12+b2]
[a20 a21 a22]     [b0 b1 b2]     [a20+b0  a21+b1  a22+b2]


예제 2: (3, 1) + (1, 4) -> (3, 4)
---
[a0]                         [a0+b0  a0+b1  a0+b2  a0+b3]
[a1]  +  [b0 b1 b2 b3]  =   [a1+b0  a1+b1  a1+b2  a1+b3]
[a2]                         [a2+b0  a2+b1  a2+b2  a2+b3]


예제 3: 비호환 -- (3,) + (4,) -> ERROR
---
3 != 4 이고 둘 다 1이 아님 -> ValueError
```

### 2.2.3 코드 예제

```python
import numpy as np

# 예제 1: 행렬 + 벡터
A = np.array([[1, 2, 3],
              [4, 5, 6],
              [7, 8, 9]])
b = np.array([10, 20, 30])
print(A + b)
# [[11 22 33]
#  [14 25 36]
#  [17 28 39]]

# 예제 2: 열 벡터 + 행 벡터 -> 행렬 (외적 패턴)
col = np.array([[1], [2], [3]])   # (3, 1)
row = np.array([10, 20, 30, 40]) # (4,) -> (1, 4)
print(col + row)  # (3, 4) 행렬

# 예제 3: ML에서의 활용 -- 데이터 중심화(centering)
X = np.random.randn(100, 5)
mean = X.mean(axis=0)             # (5,)
X_centered = X - mean             # (100, 5) - (5,) -> 브로드캐스팅

# 예제 4: Z-score 표준화
std = X.std(axis=0)
X_standardized = (X - mean) / std
```

### 2.2.4 메모리 효율성

브로드캐스팅의 핵심적 이점은 **실제로 데이터를 복사하지 않는다**는 것이다. 내부적으로 stride를 0으로 설정하여 작은 배열이 큰 배열의 크기에 맞게 "가상으로" 확장된다.

---

## 2.3 유니버설 함수 (ufunc)

유니버설 함수(ufunc)는 배열의 각 원소에 동일한 연산을 적용하는 벡터화된 함수이다.

| 분류 | 함수 예시 | 설명 |
|------|----------|------|
| 수학 함수 | `np.sin`, `np.cos`, `np.exp`, `np.log`, `np.sqrt` | 원소별 수학 연산 |
| 비교 함수 | `np.greater`, `np.equal`, `np.logical_and` | 원소별 비교 |
| 산술 함수 | `np.add`, `np.subtract`, `np.multiply` | 사칙연산 |
| 집계 함수 | `np.sum`, `np.prod`, `np.min`, `np.max` | 축별 집계 |

```python
A = np.array([[1, 2, 3],
              [4, 5, 6]])
print(np.sum(A))            # 21 (전체 합)
print(np.sum(A, axis=0))    # [5, 7, 9] (열 방향 합)
print(np.sum(A, axis=1))    # [6, 15] (행 방향 합)
print(np.mean(A, axis=0))   # [2.5, 3.5, 4.5]
```

---

## 2.4 선형대수 연산과 ML 활용

선형대수는 기계학습의 수학적 기반이다.

### 2.4.1 기본 행렬 연산

```python
A = np.array([[1, 2], [3, 4]], dtype=float)
B = np.array([[5, 6], [7, 8]], dtype=float)

# 원소별 곱셈 vs 행렬곱
print(A * B)        # 원소별 곱셈
print(A @ B)        # 행렬곱

# 전치, 행렬식, 역행렬, 대각합
print(A.T)
print(np.linalg.det(A))
print(np.linalg.inv(A))
print(np.trace(A))
print(np.linalg.norm(A, 'fro'))
```

### 2.4.2 LU 분해 (LU Decomposition)

행렬 $A$를 하삼각 행렬 $L$과 상삼각 행렬 $U$의 곱으로 분해한다:

$$A = P \cdot L \cdot U$$

**ML 활용**: 연립방정식 풀기, 행렬식 계산, 역행렬 계산의 효율적 수행

```python
from scipy import linalg as la

A = np.array([[2, 1, 1],
              [4, 3, 3],
              [8, 7, 9]], dtype=float)

P, L, U = la.lu(A)
print(f"검증: P @ L @ U = A? {np.allclose(A, P @ L @ U)}")
```

### 2.4.3 QR 분해 (QR Decomposition)

$$A = Q \cdot R, \quad Q^T Q = I$$

**ML 활용**: 최소제곱법의 수치적으로 안정된 풀이

```python
A_qr = np.array([[1, 1, 0],
                 [1, 0, 1],
                 [0, 1, 1]], dtype=float)

Q, R = np.linalg.qr(A_qr)
print(f"직교 행렬인가? {np.allclose(Q.T @ Q, np.eye(3))}")
```

### 2.4.4 SVD (특이값 분해)

$$A = U \cdot \Sigma \cdot V^T$$

**ML 활용**: PCA 차원 축소, 추천 시스템, 잠재 의미 분석(LSA), 데이터 압축

```python
A_svd = np.array([[1, 2, 0],
                  [0, 1, 1],
                  [2, 0, 1],
                  [1, 1, 1],
                  [3, 2, 1]], dtype=float)

U, s, Vt = np.linalg.svd(A_svd, full_matrices=False)

# 차원 축소: 상위 k개 특이값만 사용
k = 2
A_approx = U[:, :k] @ np.diag(s[:k]) @ Vt[:k, :]

error = np.linalg.norm(A_svd - A_approx, 'fro')
original_norm = np.linalg.norm(A_svd, 'fro')
print(f"정보 보존 비율: {(1 - error / original_norm) * 100:.2f}%")

# 분산 설명력
energy = s ** 2 / np.sum(s ** 2) * 100
print(f"누적 설명 비율: {np.cumsum(energy)}")
```

### 2.4.5 고유값 분해 (Eigendecomposition)

$$A \mathbf{v} = \lambda \mathbf{v}$$

**ML 활용**: PCA (공분산 행렬의 고유값 분해), 스펙트럴 클러스터링

```python
cov_matrix = np.array([[4, 2, 1],
                       [2, 3, 1],
                       [1, 1, 2]], dtype=float)

eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)

variance_ratio = eigenvalues / np.sum(eigenvalues) * 100
print(f"분산 설명 비율: {variance_ratio}")
```

### 2.4.6 연립방정식과 정규방정식

선형회귀의 정규방정식(Normal Equation):

$$\boldsymbol{\beta} = (X^T X)^{-1} X^T \mathbf{y}$$

```python
np.random.seed(42)
n_samples = 50
X_raw = np.random.uniform(0, 10, (n_samples, 1))
noise = np.random.normal(0, 1, (n_samples, 1))
y = 3 * X_raw + 2 + noise

X = np.hstack([np.ones((n_samples, 1)), X_raw])

# 방법 1: 역행렬 (수치적으로 불안정 -- 비추천)
beta_inv = np.linalg.inv(X.T @ X) @ X.T @ y

# 방법 2: solve (수치적으로 안정)
beta_solve = np.linalg.solve(X.T @ X, X.T @ y)

# 방법 3: lstsq (최소제곱법, 가장 안정적, 권장)
beta_lstsq, _, _, _ = np.linalg.lstsq(X, y, rcond=None)

print(f"참값: 절편=2, 기울기=3")
print(f"추정값: 절편={beta_lstsq[0,0]:.4f}, 기울기={beta_lstsq[1,0]:.4f}")
```

### 2.4.7 선형대수와 ML 관계 총정리

| 선형대수 연산 | ML 활용 | NumPy 함수 |
|--------------|---------|-----------|
| SVD | PCA, 추천 시스템, LSA | `np.linalg.svd()` |
| 고유값 분해 | PCA, 스펙트럴 클러스터링 | `np.linalg.eigh()` |
| QR 분해 | 최소제곱법 안정적 풀이 | `np.linalg.qr()` |
| LU 분해 | 연립방정식 효율적 풀이 | `scipy.linalg.lu()` |
| 정규방정식 | 선형 회귀 | `np.linalg.lstsq()` |
| 행렬곱 | 신경망 순전파 | `@` 연산자 |
| 노름 | L1, L2 규제 | `np.linalg.norm()` |

---

## 2.5 뷰(View)와 카피(Copy)

슬라이싱은 원본의 **뷰(view)**를 반환한다. 메모리를 공유하므로 효율적이지만, 의도치 않은 변경에 주의해야 한다.

```python
a = np.array([1, 2, 3, 4, 5])
b = a[1:4]       # 뷰
b[0] = 99
print(a)          # [1, 99, 3, 4, 5] -- 원본도 변경!

c = a[1:4].copy() # 카피
c[0] = 100
print(a)          # [1, 99, 3, 4, 5] -- 원본 불변
```

| 연산 | 반환 유형 | 메모리 공유 |
|------|---------|-----------|
| 슬라이싱 `a[1:4]` | 뷰 | O |
| `a.T` (전치) | 뷰 | O |
| `a.reshape()` | 뷰 (가능 시) | O |
| 팬시 인덱싱 `a[[0,2]]` | 카피 | X |
| 불리언 인덱싱 `a[mask]` | 카피 | X |
| `a.copy()` | 카피 | X |
| `a.flatten()` | 카피 | X |
| `a.ravel()` | 뷰 (가능 시) | O |

"""

with open("D:/26년1학기/기계학습/3장/한글강의록.md", "w", encoding="utf-8") as f:
    f.write(content)

print("Part 1 written successfully")
