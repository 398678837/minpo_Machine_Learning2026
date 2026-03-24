# 4장: 선형회귀 (Linear Regression) - 강의 스크립트

---

**교수자**: Jung, Minpo
**교과목**: Machine Learning
**학기**: 2026년도 1학기
**대상**: 박사과정 수업 (중국 박사과정 학생 대상)
**강의 시간**: 약 75분

---

## [도입부] 강의 개요 (약 3분)

안녕하세요, 오늘은 4장 선형회귀에 대해 강의하겠습니다.

선형회귀는 기계학습에서 가장 기본이 되는 알고리즘이면서, 동시에 200년이 넘는 역사를 가진 가장 오래된 통계 방법 중 하나입니다. 오늘 강의에서는 OLS의 수학적 원리부터 시작하여 Ridge, Lasso, Elastic Net까지의 정규화 기법을 체계적으로 다루겠습니다. 또한 SCAD 같은 고급 주제와 회귀 진단, 그리고 실습 구현까지 포함하겠습니다.

**오늘의 학습 목표**는 다음과 같습니다:

> 선형회귀의 수학적 원리를 OLS부터 정규화 기법(Ridge, Lasso, Elastic Net)까지 체계적으로 이해하고, 직접 구현을 통해 알고리즘의 내부 동작을 파악한다. 나아가 회귀 진단, SCAD 등 고급 주제와 실무 응용사례를 학습한다.

---

## [Part 1] 역사와 의의 (약 5분)

### 슬라이드: 최소제곱법의 탄생

선형회귀의 역사를 먼저 살펴보겠습니다. 선형회귀는 **최소제곱법(Method of Least Squares)**에서 출발합니다.

**르장드르(Adrien-Marie Legendre)**가 1805년에 최소제곱법을 최초로 공식 발표했습니다. 그는 혜성 궤도를 관측 데이터로부터 결정하는 문제에서, 관측값과 예측값 사이의 잔차 제곱합을 최소화하는 원리를 제안했습니다.

그런데 **가우스(Carl Friedrich Gauss)**가 1809년에 자신의 저서에서 최소제곱법을 발표하면서, 자신이 1795년부터 이미 이 방법을 사용해왔다고 주장했습니다. 가우스의 중요한 기여는 최소제곱법이 **정규 분포 가정 하에서 최대우도추정량(MLE)**과 동일하다는 것을 증명한 것입니다. 이로써 최소제곱법에 확률론적 정당성이 부여되었습니다.

### 슬라이드: 통계학에서 기계학습으로

선형회귀는 200년이 넘는 역사에도 불구하고, 현대 기계학습에서 여전히 핵심적인 위치를 차지하고 있습니다.

| 측면 | 역할 |
|------|------|
| **기초 알고리즘** | 지도학습에서 연속값을 예측하는 가장 기본적인 모델 |
| **이론적 토대** | 비용 함수 최적화, 편향-분산 트레이드오프, 정규화 등 ML 핵심 개념의 출발점 |
| **확장의 기반** | 로지스틱 회귀, 신경망, 커널 방법 등 고급 모델의 구성 요소 |
| **해석 가능성** | 회귀 계수를 통해 특성의 영향력을 직접 해석 가능 |
| **벤치마크** | 새로운 모델의 성능을 비교하는 기준선(baseline) |

여기서 강조하고 싶은 것은, 선형회귀가 단순한 "옛날 방법"이 아니라는 점입니다. Ridge, Lasso, Elastic Net 같은 정규화를 통해 현대 고차원 데이터 분석의 핵심 도구로 진화해왔습니다. 참고로 Tibshirani(1996)의 Lasso 논문은 Google Scholar 인용 50,000회 이상을 기록하고 있습니다.

### 슬라이드: 선형회귀의 수학적 정의

이제 수학적 정의를 보겠습니다. **선형회귀(Linear Regression)**는 독립 변수 $\mathbf{x} \in \mathbb{R}^p$와 종속 변수 $y \in \mathbb{R}$ 사이의 선형 관계를 모델링합니다.

$$
y = \beta_0 + \beta_1 x_1 + \beta_2 x_2 + \cdots + \beta_p x_p + \epsilon
$$

행렬 표기로 간결하게 쓰면:

$$
\mathbf{y} = \mathbf{X}\boldsymbol{\beta} + \boldsymbol{\epsilon}
$$

각 기호의 의미는 다음과 같습니다:

- $\mathbf{y} \in \mathbb{R}^n$: 반응 벡터 (n개 관측치)
- $\mathbf{X} \in \mathbb{R}^{n \times (p+1)}$: 설계 행렬 (첫 열은 절편을 위한 1 벡터)
- $\boldsymbol{\beta} \in \mathbb{R}^{p+1}$: 회귀 계수 벡터
- $\boldsymbol{\epsilon} \in \mathbb{R}^n$: 오차 벡터, $\epsilon_i \overset{iid}{\sim} N(0, \sigma^2)$

이 행렬 표기법에 익숙해지는 것이 매우 중요합니다. 앞으로의 모든 유도에서 이 표기를 사용할 것입니다.

---

## [Part 2] OLS 이론 (약 10분)

### 슬라이드: 정규방정식 유도 (행렬 미분)

이제 OLS의 핵심인 정규방정식을 유도하겠습니다. **최소제곱법(OLS)**은 잔차 제곱합(RSS)을 최소화하는 $\boldsymbol{\beta}$를 찾는 것입니다.

$$
RSS(\boldsymbol{\beta}) = \|\mathbf{y} - \mathbf{X}\boldsymbol{\beta}\|_2^2 = (\mathbf{y} - \mathbf{X}\boldsymbol{\beta})^T(\mathbf{y} - \mathbf{X}\boldsymbol{\beta})
$$

이것을 전개하면:

$$
RSS(\boldsymbol{\beta}) = \mathbf{y}^T\mathbf{y} - 2\boldsymbol{\beta}^T\mathbf{X}^T\mathbf{y} + \boldsymbol{\beta}^T\mathbf{X}^T\mathbf{X}\boldsymbol{\beta}
$$

여기서 **행렬 미분 규칙**을 적용합니다. 두 가지 핵심 공식을 기억해야 합니다:

> - $\frac{\partial}{\partial \mathbf{x}}(\mathbf{a}^T\mathbf{x}) = \mathbf{a}$
> - $\frac{\partial}{\partial \mathbf{x}}(\mathbf{x}^T\mathbf{A}\mathbf{x}) = 2\mathbf{A}\mathbf{x}$ (A가 대칭일 때)

이 규칙을 적용하여 $\boldsymbol{\beta}$에 대해 편미분하면:

$$
\frac{\partial RSS}{\partial \boldsymbol{\beta}} = -2\mathbf{X}^T\mathbf{y} + 2\mathbf{X}^T\mathbf{X}\boldsymbol{\beta}
$$

이것을 0으로 놓으면 **정규방정식(Normal Equation)**을 얻습니다:

$$
\mathbf{X}^T\mathbf{X}\boldsymbol{\beta} = \mathbf{X}^T\mathbf{y}
$$

$\mathbf{X}^T\mathbf{X}$가 가역(invertible)이면, OLS 추정량은 다음과 같습니다:

$$
\boxed{\hat{\boldsymbol{\beta}}_{OLS} = (\mathbf{X}^T\mathbf{X})^{-1}\mathbf{X}^T\mathbf{y}}
$$

이 공식은 매우 중요하니 반드시 외워두시기 바랍니다.

이 해가 최솟값인지 확인하기 위해 2차 미분(헤시안)을 구하면:

$$
\frac{\partial^2 RSS}{\partial \boldsymbol{\beta} \partial \boldsymbol{\beta}^T} = 2\mathbf{X}^T\mathbf{X}
$$

$\mathbf{X}^T\mathbf{X}$는 양의 반정치(positive semi-definite) 행렬이므로, RSS는 볼록(convex) 함수이고 정규방정식의 해는 전역 최솟값입니다.

### 슬라이드: 기하학적 해석

OLS를 기하학적으로 이해하는 것도 매우 중요합니다. 핵심은 **직교 사영(orthogonal projection)**입니다.

- $\mathbf{y}$는 $\mathbb{R}^n$ 공간의 벡터입니다.
- $\mathbf{X}$의 열들이 생성하는 부분공간을 $\mathcal{C}(\mathbf{X})$ (열공간)라 합시다.
- OLS 예측값 $\hat{\mathbf{y}} = \mathbf{X}\hat{\boldsymbol{\beta}}$는 $\mathbf{y}$를 $\mathcal{C}(\mathbf{X})$에 **직교 사영**한 것입니다.

$$
\hat{\mathbf{y}} = \mathbf{X}(\mathbf{X}^T\mathbf{X})^{-1}\mathbf{X}^T\mathbf{y} = \mathbf{H}\mathbf{y}
$$

여기서 $\mathbf{H} = \mathbf{X}(\mathbf{X}^T\mathbf{X})^{-1}\mathbf{X}^T$를 **햇 행렬(hat matrix)** 또는 **사영 행렬(projection matrix)**이라 합니다.

**핵심 성질**을 정리하면:

- 잔차 벡터 $\mathbf{e} = \mathbf{y} - \hat{\mathbf{y}}$는 열공간에 **직교**합니다: $\mathbf{X}^T\mathbf{e} = \mathbf{0}$
- 피타고라스 정리가 성립합니다: $\|\mathbf{y}\|^2 = \|\hat{\mathbf{y}}\|^2 + \|\mathbf{e}\|^2$ (TSS = ESS + RSS)
- $R^2 = \cos^2\theta$로, $\mathbf{y}$와 $\hat{\mathbf{y}}$ 사이 각도의 코사인 제곱입니다.

이 기하학적 관점은 뒤에 나올 Ridge 회귀의 이해에도 도움이 됩니다.

### 슬라이드: 가우스-마르코프 정리

**가우스-마르코프 정리(Gauss-Markov Theorem)**는 OLS 추정량의 최적성을 보장하는 핵심 정리입니다. 다음 네 가지 조건을 만족할 때:

1. $E[\epsilon_i] = 0$ (오차의 기대값이 0)
2. $\text{Var}(\epsilon_i) = \sigma^2$ (등분산성)
3. $\text{Cov}(\epsilon_i, \epsilon_j) = 0, \; i \neq j$ (오차 간 무상관)
4. $\mathbf{X}$는 고정된(non-random) 행렬

OLS 추정량 $\hat{\boldsymbol{\beta}}_{OLS}$는 **BLUE(Best Linear Unbiased Estimator)**입니다.

- **Best**: 모든 선형 비편향 추정량 중에서 분산이 가장 작다
- **Linear**: $\hat{\boldsymbol{\beta}}$가 $\mathbf{y}$의 선형 함수이다
- **Unbiased**: $E[\hat{\boldsymbol{\beta}}] = \boldsymbol{\beta}$
- **Estimator**: $\boldsymbol{\beta}$의 추정량이다

OLS 추정량의 **분산-공분산 행렬**은:

$$
\text{Var}(\hat{\boldsymbol{\beta}}_{OLS}) = \sigma^2 (\mathbf{X}^T\mathbf{X})^{-1}
$$

여기서 매우 중요한 포인트가 있습니다. 가우스-마르코프 정리는 OLS가 **비편향 추정량 중에서** 최적이라고 말할 뿐입니다. 만약 약간의 편향을 허용한다면? Ridge 회귀처럼 편향을 도입하면 MSE 관점에서 OLS보다 더 나은 추정량이 존재할 수 있습니다. 이것이 바로 Hoerl & Kennard(1970)의 핵심 통찰이며, 다음 섹션에서 자세히 다루겠습니다.

---

## [Part 3] 다중공선성 (약 5분)

### 슬라이드: 다중공선성의 정의와 문제점

Ridge 회귀로 넘어가기 전에, 먼저 **다중공선성(Multicollinearity)** 문제를 이해해야 합니다. 다중공선성은 독립 변수들 사이에 높은 선형 상관관계가 존재하는 현상입니다.

수학적으로 보면, $\mathbf{X}^T\mathbf{X}$ 행렬이 **특이(singular)**에 가까워지면:

- $(\mathbf{X}^T\mathbf{X})^{-1}$의 원소가 매우 커집니다
- $\text{Var}(\hat{\boldsymbol{\beta}}) = \sigma^2(\mathbf{X}^T\mathbf{X})^{-1}$이 폭증합니다
- 회귀 계수 추정이 **불안정**해집니다 (데이터가 조금만 바뀌어도 계수가 크게 변동)

### 슬라이드: VIF와 조건수

다중공선성을 진단하는 두 가지 주요 지표가 있습니다.

첫 번째는 **분산 팽창 인자(VIF)**입니다:

$$
VIF_j = \frac{1}{1 - R_j^2}
$$

여기서 $R_j^2$는 $x_j$를 나머지 모든 독립 변수들로 회귀했을 때의 결정계수입니다.

| VIF 값 | 해석 |
|--------|------|
| 1 | 다중공선성 없음 |
| 1~5 | 약한 다중공선성 (일반적으로 허용) |
| 5~10 | 중간 수준 (주의 필요) |
| 10 이상 | 심각한 다중공선성 (조치 필요) |

두 번째는 **조건수(condition number)**입니다:

$$
\kappa(\mathbf{X}^T\mathbf{X}) = \frac{\lambda_{\max}}{\lambda_{\min}}
$$

조건수가 30 이상이면 다중공선성을 의심합니다.

### 슬라이드: 다중공선성 해결 방법

| 방법 | 설명 |
|------|------|
| **변수 제거** | VIF가 높은 변수를 수동으로 제거 |
| **주성분 회귀(PCR)** | PCA로 차원을 축소한 후 회귀 |
| **Ridge 회귀** | L2 정규화로 $(\mathbf{X}^T\mathbf{X} + \lambda\mathbf{I})$의 조건수를 개선 |
| **Lasso 회귀** | L1 정규화로 불필요한 변수를 자동 제거 |

이제 이 해결 방법들을 본격적으로 살펴보겠습니다.

---

## [Part 4] Ridge 회귀 (약 10분)

### 슬라이드: Hoerl & Kennard (1970)의 핵심 아이디어

Hoerl과 Kennard는 1970년 *Technometrics*에 발표한 논문에서 **릿지 회귀(Ridge Regression)**를 공식 제안했습니다.

핵심 통찰은 가우스-마르코프 정리의 "허점"을 파고든 것입니다. 앞에서 말씀드렸듯이, OLS는 비편향 추정량 중 최적이지만, **약간의 편향을 도입**하면 분산을 크게 줄여 전체 MSE를 감소시킬 수 있습니다.

$$
MSE(\hat{\boldsymbol{\beta}}) = \text{Var}(\hat{\boldsymbol{\beta}}) + [\text{Bias}(\hat{\boldsymbol{\beta}})]^2
$$

OLS에서는 편향이 0이지만 분산이 클 수 있습니다. Ridge 회귀는 편향을 약간 증가시키되 분산을 더 크게 감소시켜서, 전체 MSE를 줄입니다. 이것이 **편향-분산 트레이드오프(bias-variance tradeoff)**의 고전적 예시입니다.

이 개념은 기계학습 전체를 관통하는 핵심 원리이니 꼭 기억해 두시기 바랍니다.

### 슬라이드: L2 정규화의 수학적 정의

Ridge 회귀의 최적화 문제는 다음과 같습니다:

$$
\hat{\boldsymbol{\beta}}_{ridge} = \arg\min_{\boldsymbol{\beta}} \left\{ \|\mathbf{y} - \mathbf{X}\boldsymbol{\beta}\|_2^2 + \lambda \|\boldsymbol{\beta}\|_2^2 \right\}
$$

여기서:

- $\|\mathbf{y} - \mathbf{X}\boldsymbol{\beta}\|_2^2$: 잔차 제곱합 (데이터 적합도)
- $\lambda \|\boldsymbol{\beta}\|_2^2 = \lambda \sum_{j=1}^p \beta_j^2$: L2 패널티 (정규화 항)
- $\lambda \geq 0$: 정규화 강도 (하이퍼파라미터)

유도 과정을 보겠습니다. 목적 함수를 미분하면:

$$
-2\mathbf{X}^T\mathbf{y} + 2\mathbf{X}^T\mathbf{X}\boldsymbol{\beta} + 2\lambda\boldsymbol{\beta} = 0
$$

$$
(\mathbf{X}^T\mathbf{X} + \lambda\mathbf{I})\boldsymbol{\beta} = \mathbf{X}^T\mathbf{y}
$$

따라서 **닫힌 형태(closed-form) 해**는:

$$
\boxed{\hat{\boldsymbol{\beta}}_{ridge} = (\mathbf{X}^T\mathbf{X} + \lambda\mathbf{I})^{-1}\mathbf{X}^T\mathbf{y}}
$$

OLS와 비교해 보면, $\lambda\mathbf{I}$만 추가된 것입니다. 이것이 가져오는 **핵심 효과**는 세 가지입니다:

1. 행렬의 **조건수를 감소**시킵니다: $\kappa(\mathbf{X}^T\mathbf{X} + \lambda\mathbf{I}) < \kappa(\mathbf{X}^T\mathbf{X})$
2. 역행렬 계산을 **수치적으로 안정**하게 만듭니다
3. 회귀 계수를 **0 방향으로 축소(shrinkage)**합니다

### 슬라이드: 고유값 분해를 통한 이해

$\mathbf{X}^T\mathbf{X}$의 고유값 분해 $\mathbf{X}^T\mathbf{X} = \mathbf{V}\mathbf{D}\mathbf{V}^T$를 사용하면, Ridge 회귀는 각 고유값 방향의 계수를 $\frac{d_j}{d_j + \lambda}$만큼 축소합니다:

- 고유값 $d_j$가 큰 방향: 축소 비율이 1에 가까움 (거의 변하지 않음)
- 고유값 $d_j$가 작은 방향: 축소 비율이 0에 가까움 (강하게 축소)

직관적으로 말하면, 데이터의 분산이 작은, 즉 불안정한 방향의 계수를 선택적으로 축소하는 효과가 있습니다.

### 슬라이드: 베이지안 해석

Ridge 회귀는 **베이지안 관점**에서도 자연스럽게 해석됩니다.

- 사전 분포(prior): $\boldsymbol{\beta} \sim N(\mathbf{0}, \tau^2\mathbf{I})$
- 우도(likelihood): $\mathbf{y}|\mathbf{X},\boldsymbol{\beta} \sim N(\mathbf{X}\boldsymbol{\beta}, \sigma^2\mathbf{I})$

사후 최빈값(MAP)을 구하면:

$$
\hat{\boldsymbol{\beta}}_{MAP} = \arg\min_{\boldsymbol{\beta}} \left[ \frac{1}{2\sigma^2}\|\mathbf{y} - \mathbf{X}\boldsymbol{\beta}\|^2 + \frac{1}{2\tau^2}\|\boldsymbol{\beta}\|^2 \right]
$$

$\lambda = \sigma^2/\tau^2$로 놓으면 Ridge 회귀와 정확히 동일합니다. 즉:

> **Ridge 회귀 = 회귀 계수에 정규 분포 사전 분포를 부여한 베이지안 MAP 추정**

$\tau^2$가 작을수록 (사전 분포가 0 근처에 집중될수록) $\lambda$가 커지고 계수가 더 많이 축소됩니다.

### 슬라이드: 릿지 트레이스

Hoerl과 Kennard가 도입한 **릿지 트레이스(Ridge Trace)**는 $\lambda$를 x축, 각 회귀 계수를 y축에 놓고 그린 그래프입니다. $\lambda = 0$ (OLS)에서 시작하여 $\lambda$가 증가할수록 모든 계수가 0으로 수렴하는 경로를 보여줍니다. 실습에서 직접 이것을 시각화해 볼 것입니다.

---

## [Part 5] Lasso 회귀 (약 10분)

### 슬라이드: Tibshirani (1996)의 혁신

이제 Lasso로 넘어가겠습니다. Tibshirani가 1996년에 제안한 **Lasso(Least Absolute Shrinkage and Selection Operator)**는 통계학과 기계학습 역사에서 가장 영향력 있는 논문 중 하나입니다.

Lasso의 핵심 혁신은 매우 간단합니다. Ridge의 L2 패널티($\|\boldsymbol{\beta}\|_2^2$)를 **L1 패널티($\|\boldsymbol{\beta}\|_1$)**로 교체한 것입니다. 이 간단한 변경이 근본적으로 다른 성질을 만들어냅니다: **축소(shrinkage)**와 **변수 선택(variable selection)**을 동시에 수행합니다.

### 슬라이드: L1 정규화의 수학적 정의

Lasso의 최적화 문제:

$$
\hat{\boldsymbol{\beta}}_{lasso} = \arg\min_{\boldsymbol{\beta}} \left\{ \frac{1}{2n}\|\mathbf{y} - \mathbf{X}\boldsymbol{\beta}\|_2^2 + \lambda \|\boldsymbol{\beta}\|_1 \right\}
$$

동치인 제약 조건 형태로 쓰면:

$$
\hat{\boldsymbol{\beta}}_{lasso} = \arg\min_{\boldsymbol{\beta}} \sum_{i=1}^n (y_i - \mathbf{x}_i^T\boldsymbol{\beta})^2 \quad \text{subject to} \quad \sum_{j=1}^p |\beta_j| \leq t
$$

여기서 중요한 차이점이 있습니다. L1 노름은 원점에서 미분 불가능하므로, Lasso는 닫힌 형태의 해가 일반적으로 존재하지 않습니다. 따라서 좌표 하강법(coordinate descent) 등의 반복 알고리즘이 필요합니다.

### 슬라이드: 연성 임계값 연산자

직교 설계($\mathbf{X}^T\mathbf{X} = n\mathbf{I}$)에서 Lasso의 해는 **연성 임계값 연산자(Soft Thresholding Operator)**로 표현됩니다:

$$
\hat{\beta}_j^{lasso} = S(\hat{\beta}_j^{OLS}, \lambda) = \text{sign}(\hat{\beta}_j^{OLS}) \cdot \max(|\hat{\beta}_j^{OLS}| - \lambda, 0)
$$

이 연산자의 동작을 세 구간으로 나누어 봅시다:

- $|\hat{\beta}_j^{OLS}| \leq \lambda$: 계수를 **정확히 0으로** 만듭니다 (변수 제거)
- $\hat{\beta}_j^{OLS} > \lambda$: 계수를 $\lambda$만큼 축소합니다 ($\hat{\beta}_j - \lambda$)
- $\hat{\beta}_j^{OLS} < -\lambda$: 계수를 $\lambda$만큼 축소합니다 ($\hat{\beta}_j + \lambda$)

이것은 Ridge의 비례 축소($\hat{\beta}_j^{ridge} = \frac{d_j}{d_j + \lambda}\hat{\beta}_j^{OLS}$)와 근본적으로 다릅니다. Ridge는 계수를 0에 가깝게 만들 뿐, **정확히 0으로 만들지 못합니다**. 이것이 두 방법의 가장 큰 차이점입니다.

### 슬라이드: L1 vs L2 기하학적 설명

Lasso가 희소해(sparse solution)를 생성하는 이유를 기하학적으로 이해해 봅시다. 이 부분은 시험에도 자주 나오는 중요한 내용입니다.

2차원에서 생각해 봅시다:

- **L2 (Ridge)**: 제약 영역이 **원**입니다 ($\beta_1^2 + \beta_2^2 \leq t$). RSS의 타원형 등고선과 원의 접점은 일반적으로 좌표축 위에 있지 않습니다. 따라서 계수가 정확히 0이 되기 어렵습니다.

- **L1 (Lasso)**: 제약 영역이 **마름모**입니다 ($|\beta_1| + |\beta_2| \leq t$). 마름모의 **꼭짓점이 좌표축 위**에 있으므로, RSS 등고선과의 접점이 꼭짓점에서 만날 확률이 높습니다. 꼭짓점에서는 하나 이상의 좌표가 0이므로, 변수가 자동으로 선택됩니다.

PPT에서 이 그림을 보면 직관적으로 이해할 수 있습니다. 마름모의 뾰족한 꼭짓점에서 접선이 만나면 $\beta_1 = 0$ 또는 $\beta_2 = 0$이 됩니다.

### 슬라이드: Lasso의 베이지안 해석

Lasso는 베이지안 관점에서 회귀 계수에 **라플라스(Laplace) 사전 분포**를 부여한 MAP 추정에 해당합니다:

$$
p(\beta_j) = \frac{\lambda}{2} \exp(-\lambda |\beta_j|)
$$

라플라스 분포는 정규 분포보다 원점에서 더 뾰족하고 꼬리가 더 두껍습니다. 이 때문에:

- 0 근처의 작은 계수에 대한 사전 확률이 더 높습니다 (희소성 유도)
- 큰 계수에 대해서도 적당한 사전 확률을 부여합니다 (꼬리가 두꺼움)

정리하면, **Ridge = 정규 분포 사전 분포**, **Lasso = 라플라스 분포 사전 분포**입니다.

---

## [Part 6] Elastic Net (약 7분)

### 슬라이드: Zou & Hastie (2005)의 동기

Zou와 Hastie는 2005년 논문에서 Lasso의 두 가지 한계를 지적했습니다:

1. **$p > n$ 문제**: 변수 수가 표본 수보다 많으면, Lasso는 최대 $n$개의 변수만 선택할 수 있습니다. 유전체학 등 고차원 데이터에서 심각한 제약입니다.

2. **그룹화 효과 부재**: 높은 상관관계를 가진 변수 그룹이 있을 때, Lasso는 그 중 하나만 선택하고 나머지를 제거하는 경향이 있습니다. 실제로는 상관된 변수들이 모두 중요할 수 있는데 말이죠.

### 슬라이드: L1 + L2 혼합 정규화

Elastic Net은 L1과 L2를 결합한 것입니다:

$$
\hat{\boldsymbol{\beta}}_{enet} = \arg\min_{\boldsymbol{\beta}} \left\{ \frac{1}{2n}\|\mathbf{y} - \mathbf{X}\boldsymbol{\beta}\|_2^2 + \lambda \left[ \alpha \|\boldsymbol{\beta}\|_1 + \frac{1-\alpha}{2} \|\boldsymbol{\beta}\|_2^2 \right] \right\}
$$

여기서:

- $\lambda > 0$: 전체 정규화 강도
- $\alpha \in [0, 1]$: L1과 L2의 혼합 비율 (sklearn에서 `l1_ratio`)
  - $\alpha = 1$: 순수 Lasso
  - $\alpha = 0$: 순수 Ridge
  - $0 < \alpha < 1$: Elastic Net

### 슬라이드: 그룹화 효과 (Grouping Effect)

Elastic Net의 가장 중요한 이론적 결과는 **그룹화 효과 정리**입니다.

**정리 (Zou & Hastie, 2005)**: 두 변수 $x_i$와 $x_j$의 표본 상관계수가 $r$일 때:

$$
|\hat{\beta}_i - \hat{\beta}_j| \leq \frac{1}{\lambda(1-\alpha)} \sqrt{2(1-r)} \cdot \|\mathbf{y}\|
$$

이 부등식이 말하는 것은:

- 상관관계가 높을수록 ($r \to 1$) 두 계수의 차이가 작아집니다
- L2 패널티 강도가 클수록 두 계수가 더 유사해집니다
- 순수 Lasso ($\alpha = 1$)에서는 분모가 0이 되어 이 성질이 성립하지 않습니다

> 직관적으로, Elastic Net은 "상관된 변수들은 함께 선택하거나 함께 제거한다"는 원칙을 따릅니다.

### 슬라이드: 제약 영역의 기하학

Elastic Net의 제약 영역은 L1의 마름모와 L2의 원을 결합한 **모서리가 둥근 마름모(rounded diamond)** 형태입니다.

- $\alpha$가 1에 가까울수록 마름모에 가까움 (희소성 강조)
- $\alpha$가 0에 가까울수록 원에 가까움 (안정성 강조)

### 슬라이드: 세 방법의 종합 비교

이 표는 매우 중요하니 잘 정리해 두시기 바랍니다:

| 특성 | Ridge (L2) | Lasso (L1) | Elastic Net (L1+L2) |
|------|-----------|-----------|-------------------|
| **패널티** | $\lambda\|\boldsymbol{\beta}\|_2^2$ | $\lambda\|\boldsymbol{\beta}\|_1$ | $\lambda[\alpha\|\boldsymbol{\beta}\|_1 + (1-\alpha)\|\boldsymbol{\beta}\|_2^2/2]$ |
| **변수 선택** | X (모든 계수 비영) | O (일부 계수 = 0) | O (일부 계수 = 0) |
| **그룹화 효과** | O (상관 변수 동시 축소) | X (하나만 선택) | O (상관 변수 동시 선택) |
| **닫힌 형태 해** | O | X | X |
| **$p > n$ 지원** | O | 최대 $n$개 변수 | O |
| **베이지안 사전분포** | 정규 분포 | 라플라스 분포 | 정규+라플라스 혼합 |
| **제약 영역** | 원 | 마름모 | 둥근 마름모 |

---

## [Part 7] 좌표 하강법 (약 5분)

### 슬라이드: Friedman, Hastie, Tibshirani (2010)의 glmnet 알고리즘

Lasso와 Elastic Net은 닫힌 형태의 해가 없으므로, 효율적인 수치 알고리즘이 필요합니다. Friedman, Hastie, Tibshirani가 2010년에 제안한 **좌표 하강법(Coordinate Descent)** 기반의 `glmnet` 알고리즘이 바로 그것입니다. sklearn의 `Lasso`, `ElasticNet` 클래스가 이 알고리즘에 기반합니다.

### 슬라이드: 알고리즘 원리

좌표 하강법은 **한 번에 하나의 변수(좌표)만 최적화**하고, 이를 모든 변수에 대해 반복 순환하는 방법입니다.

Elastic Net 문제에서 $j$번째 좌표에 대한 업데이트 규칙:

$$
\tilde{\beta}_j \leftarrow \frac{S\left(\frac{1}{n}\sum_{i=1}^{n} x_{ij} \cdot r_i^{(j)},\; \alpha\lambda\right)}{\frac{1}{n}\sum_{i=1}^{n} x_{ij}^2 + \lambda(1-\alpha)}
$$

여기서:

- $r_i^{(j)} = y_i - \beta_0 - \sum_{k \neq j} x_{ik}\beta_k$: $j$번째 변수를 제외한 **부분 잔차(partial residual)**
- $S(z, \gamma) = \text{sign}(z) \cdot \max(|z| - \gamma, 0)$: **연성 임계값 연산자**

각 좌표별 최적화가 연성 임계값 연산자로 닫힌 형태로 구해진다는 것이 이 알고리즘의 핵심입니다.

### 슬라이드: 핵심 최적화 기법

실용적으로 중요한 세 가지 최적화 기법이 있습니다:

**1. 따뜻한 시작 (Warm Start)**: 정규화 경로를 따라 순차적으로 풀 때, 이전 $\lambda$에서의 해를 다음 $\lambda$의 초기값으로 사용합니다. 인접한 $\lambda$ 값에서의 해는 매우 유사하므로 수렴이 극도로 빠릅니다.

**2. 활성 집합 (Active Set)**: 0이 아닌 계수를 가진 변수 집합만 우선적으로 업데이트합니다. Lasso에서 대부분의 계수가 0이므로, 활성 집합만 업데이트하면 계산량이 크게 감소합니다.

**3. lambda_max 계산**: 모든 계수가 0이 되는 최소 $\lambda$ 값을 미리 계산합니다:

$$
\lambda_{\max} = \frac{1}{\alpha n} \max_j |X_j^T (y - \bar{y})|
$$

좌표 하강법이 효율적인 이유를 정리하면:

1. 각 좌표별 최적화가 닫힌 형태로 가능합니다
2. 목적 함수가 볼록이므로 전역 수렴이 보장됩니다
3. 한 좌표 업데이트는 $O(n)$이므로, 한 번 순환은 $O(np)$입니다

---

## [Part 8] SCAD와 Oracle 특성 (약 5분)

### 슬라이드: Fan & Li (2001)의 문제 제기

이번에는 좀 더 고급 주제를 다루겠습니다. Fan과 Li는 2001년 JASA 논문에서 Lasso의 근본적 한계를 지적했습니다.

Lasso의 L1 패널티는 계수의 크기에 관계없이 동일한 양만큼 축소합니다. 따라서 작은 계수는 적절히 0으로 제거하지만, **큰 계수도 불필요하게 축소(over-shrinkage)**하여 편향이 발생합니다.

### 슬라이드: 오라클 성질

**오라클(oracle)**은 "어떤 변수가 진정으로 중요한지 미리 알고 있는 이상적인 존재"입니다. **오라클 성질**은 두 가지 조건을 동시에 만족하는 것입니다:

1. **일관성 있는 변수 선택**: 표본이 충분히 크면 진정한 변수를 올바르게 식별한다.

$$
P\left(\{j : \hat{\beta}_j \neq 0\} = \{j : \beta_j^* \neq 0\}\right) \to 1 \quad (n \to \infty)
$$

2. **점근적 정규성**: 0이 아닌 계수의 추정이, 진정한 모델을 알고 있을 때의 OLS와 동일한 점근 분포를 가진다.

중요한 사실은, **Lasso는 오라클 성질을 만족하지 못합니다**. 큰 계수에 대한 과도한 축소 때문입니다.

### 슬라이드: SCAD 패널티

Fan과 Li가 제안한 **SCAD(Smoothly Clipped Absolute Deviation)** 패널티는 세 구간으로 나누어 동작합니다:

| 구간 | 패널티 동작 | 효과 |
|------|-----------|------|
| $|\theta| \leq \lambda$ | L1과 동일 | 작은 계수를 0으로 제거 |
| $\lambda < |\theta| \leq a\lambda$ | 패널티가 점차 감소 | 중간 계수를 점진적으로 축소 |
| $|\theta| > a\lambda$ | 패널티 미분 = 0 | 큰 계수에 추가 축소 없음 (편향 없음) |

여기서 $a > 2$ (통상 $a = 3.7$)입니다.

### 슬라이드: 좋은 패널티의 세 가지 조건과 정규화 계보

Fan과 Li는 좋은 패널티 함수의 세 가지 조건을 제시했습니다:

1. **비편향성**: 큰 계수에 대해 편향이 없거나 거의 없을 것
2. **희소성**: 작은 계수를 0으로 만들 것
3. **연속성**: 추정량이 데이터의 연속 함수일 것

이 세 조건을 동시에 만족하는 패널티는 반드시 **비볼록(nonconvex)**이어야 합니다. L1(Lasso)은 볼록이므로 비편향성을 만족하지 못합니다.

정규화 방법의 계보를 정리하면:

| 방법 | 연도 | 변수 선택 | 오라클 성질 | 볼록성 |
|------|------|---------|-----------|--------|
| Ridge | 1970 | X | X | O |
| Lasso | 1996 | O | X | O |
| SCAD | 2001 | O | O | X |
| Elastic Net | 2005 | O | X | O |
| Adaptive Lasso | 2006 | O | O | O |
| MCP | 2010 | O | O | X |

---

## [Part 9] 회귀 진단 (약 5분)

### 슬라이드: 잔차 분석

회귀 모델을 적합한 후에는 반드시 회귀 진단을 수행해야 합니다.

**잔차의 종류**:

| 잔차 유형 | 공식 | 용도 |
|----------|------|------|
| 일반 잔차 | $e_i = y_i - \hat{y}_i$ | 기본 분석 |
| 표준화 잔차 | $r_i = \frac{e_i}{\hat{\sigma}\sqrt{1 - h_{ii}}}$ | 이상치 탐지 |
| 스튜던트화 잔차 | $t_i = \frac{e_i}{\hat{\sigma}_{(i)}\sqrt{1 - h_{ii}}}$ | 더 정밀한 이상치 탐지 |

여기서 $h_{ii}$는 햇 행렬의 대각 원소(레버리지), $\hat{\sigma}_{(i)}$는 $i$번째 관측치를 제외하고 추정한 표준 오차입니다.

**잔차 플롯 확인 사항**:

1. **예측값 vs 잔차 플롯**: 패턴이 없어야 합니다 (등분산성 확인)
2. **잔차의 정규성**: Q-Q plot으로 확인
3. **자기상관**: 시계열 데이터에서 잔차의 독립성 확인

### 슬라이드: Q-Q Plot

Q-Q plot은 잔차가 정규 분포를 따르는지 시각적으로 확인하는 도구입니다. x축에 이론적 정규 분포의 분위수, y축에 잔차의 분위수를 놓고, 점들이 45도 직선 위에 놓이면 정규 분포를 따르는 것입니다.

```python
import scipy.stats as stats
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(6, 6))
stats.probplot(residuals, dist="norm", plot=ax)
ax.set_title('정규 Q-Q Plot')
plt.show()
```

### 슬라이드: Cook's Distance

**쿡의 거리(Cook's Distance)**는 각 관측치가 회귀 모델에 미치는 **영향력(influence)**을 측정합니다.

$$
D_i = \frac{(\hat{\mathbf{y}} - \hat{\mathbf{y}}_{(i)})^T (\hat{\mathbf{y}} - \hat{\mathbf{y}}_{(i)})}{p \cdot MSE} = \frac{r_i^2}{p} \cdot \frac{h_{ii}}{(1-h_{ii})^2}
$$

판정 기준:

- $D_i > 1$: 영향력이 큰 관측치
- $D_i > 4/n$: 보다 보수적인 기준

```python
import numpy as np
from sklearn.linear_model import LinearRegression

model = LinearRegression().fit(X, y)
y_pred = model.predict(X)
residuals = y - y_pred

# 햇 행렬의 대각 원소 (레버리지)
H = X @ np.linalg.inv(X.T @ X) @ X.T
leverage = np.diag(H)

# MSE
n, p = X.shape
mse = np.sum(residuals**2) / (n - p)

# 표준화 잔차
std_residuals = residuals / np.sqrt(mse * (1 - leverage))

# Cook's Distance
cooks_d = (std_residuals**2 / p) * (leverage / (1 - leverage)**2)
```

### 슬라이드: 회귀 진단 종합 체크리스트

| 항목 | 확인 방법 | 위반 시 조치 |
|------|----------|------------|
| 선형성 | 예측값 vs 잔차 플롯 | 변수 변환, 다항 회귀 |
| 등분산성 | 예측값 vs 잔차 플롯 | WLS, 변수 변환 |
| 정규성 | Q-Q plot, Shapiro-Wilk 검정 | 변수 변환, 로버스트 회귀 |
| 독립성 | Durbin-Watson 검정 | GLS, 시계열 모델 |
| 다중공선성 | VIF, 조건수 | 변수 제거, Ridge 회귀 |
| 이상치/영향점 | Cook's distance, 레버리지 | 제거 또는 로버스트 회귀 |

---

## [Part 10] 실습: Ridge 회귀 구현 (약 5분)

### 슬라이드: 다중공선성 데이터 생성

이제 실습으로 넘어가겠습니다. 먼저 Ridge 회귀의 효과를 확인하기 위해 다중공선성이 있는 데이터를 생성합니다. 기본 독립 특성 5개에, 이들의 선형 결합으로 구성된 5개의 상관 특성을 추가합니다.

```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import Ridge, RidgeCV
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
from sklearn.metrics import mean_squared_error, r2_score

np.random.seed(42)

def generate_data(n_samples=200, n_features=10, noise_std=1.0):
    """다중공선성이 있는 회귀 데이터 생성"""
    X_base = np.random.randn(n_samples, 5)
    X_corr = np.column_stack([
        X_base[:, 0] + 0.1 * np.random.randn(n_samples),
        X_base[:, 1] + 0.1 * np.random.randn(n_samples),
        X_base[:, 2] + 0.15 * np.random.randn(n_samples),
        X_base[:, 0] + X_base[:, 1] + 0.2 * np.random.randn(n_samples),
        0.5 * X_base[:, 3] + 0.5 * X_base[:, 4] + 0.1 * np.random.randn(n_samples)
    ])
    X = np.column_stack([X_base, X_corr])
    beta_true = np.array([3.0, -2.0, 1.5, 0.0, 0.5,
                          0.0, 0.0, 0.0, 0.0, 0.0])
    y = X @ beta_true + noise_std * np.random.randn(n_samples)
    return X, y, beta_true

X, y, beta_true = generate_data(n_samples=200, n_features=10)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
```

여기서 핵심 포인트는 x5~x9가 x0~x4의 선형 결합이라는 것입니다. 이것이 다중공선성을 유발합니다. 그리고 진정한 계수에서 x5~x9의 계수는 모두 0입니다.

### 슬라이드: Ridge 회귀 직접 구현

정규방정식의 닫힌 형태 해 $\hat{\boldsymbol{\beta}} = (\mathbf{X}^T\mathbf{X} + \lambda\mathbf{I})^{-1}\mathbf{X}^T\mathbf{y}$를 직접 구현합니다.

```python
class RidgeRegressionFromScratch:
    def __init__(self, alpha=1.0):
        self.alpha = alpha
        self.coef_ = None
        self.intercept_ = None

    def fit(self, X, y):
        n_samples, n_features = X.shape
        self.X_mean_ = np.mean(X, axis=0)
        self.y_mean_ = np.mean(y)
        X_centered = X - self.X_mean_
        y_centered = y - self.y_mean_

        XtX = X_centered.T @ X_centered
        identity = np.eye(n_features)
        regularized = XtX + self.alpha * identity
        Xty = X_centered.T @ y_centered

        # np.linalg.solve가 역행렬보다 수치적으로 안정적
        self.coef_ = np.linalg.solve(regularized, Xty)
        self.intercept_ = self.y_mean_ - self.X_mean_ @ self.coef_
        return self

    def predict(self, X):
        return X @ self.coef_ + self.intercept_
```

실제로 이 코드를 실행하면 sklearn의 Ridge와 거의 동일한 결과를 얻습니다. 계수의 차이가 $10^{-10}$ 수준으로, 사실상 같은 결과입니다.

### 슬라이드: 정규화 경로 및 교차 검증

릿지 트레이스를 그려보면, $\lambda$가 증가할수록 모든 계수가 0 방향으로 축소되는 것을 확인할 수 있습니다. 교차 검증을 통해 최적의 $\lambda$를 선택하고, OLS와 비교하면 Ridge가 조건수를 크게 개선하는 것을 볼 수 있습니다.

```python
# 교차 검증으로 최적 lambda 선택
alpha_candidates = np.logspace(-2, 4, 100)
ridge_cv = RidgeCV(alphas=alpha_candidates, cv=5,
                   scoring='neg_mean_squared_error')
ridge_cv.fit(X_scaled, y)
print(f"최적 lambda: {ridge_cv.alpha_:.4f}")
```

---

## [Part 11] 실습: Lasso 회귀 구현 (약 5분)

### 슬라이드: 연성 임계값 연산자와 좌표 하강법

Lasso는 좌표 하강법으로 구현합니다. 핵심은 연성 임계값 연산자입니다:

```python
def soft_threshold(z, gamma):
    """S(z, gamma) = sign(z) * max(|z| - gamma, 0)"""
    return np.sign(z) * np.maximum(np.abs(z) - gamma, 0.0)
```

Friedman et al.(2010)의 알고리즘을 충실히 구현한 Lasso 클래스를 보겠습니다.

```python
class LassoRegressionFromScratch:
    def __init__(self, alpha=1.0, max_iter=1000, tol=1e-6):
        self.alpha = alpha
        self.max_iter = max_iter
        self.tol = tol

    def fit(self, X, y):
        n_samples, n_features = X.shape
        self.X_mean_ = np.mean(X, axis=0)
        self.y_mean_ = np.mean(y)
        X_centered = X - self.X_mean_
        y_centered = y - self.y_mean_
        col_norms_sq = np.sum(X_centered ** 2, axis=0) / n_samples

        w = np.zeros(n_features)
        residual = y_centered.copy()

        for iteration in range(self.max_iter):
            w_old = w.copy()
            for j in range(n_features):
                residual += X_centered[:, j] * w[j]
                rho_j = X_centered[:, j].T @ residual / n_samples
                if col_norms_sq[j] > 0:
                    w[j] = soft_threshold(rho_j, self.alpha) / col_norms_sq[j]
                else:
                    w[j] = 0.0
                residual -= X_centered[:, j] * w[j]

            if np.max(np.abs(w - w_old)) < self.tol:
                self.n_iter_ = iteration + 1
                break

        self.coef_ = w
        self.intercept_ = self.y_mean_ - self.X_mean_ @ self.coef_
        return self
```

주목할 점은 for 루프 안에서 각 변수 $j$에 대해: 부분 잔차를 계산하고, 연성 임계값을 적용하고, 잔차를 업데이트하는 세 단계가 반복된다는 것입니다.

### 슬라이드: Lasso 정규화 경로

Lasso의 정규화 경로를 시각화하면, $\lambda$가 감소할수록 변수가 하나씩 모델에 추가되는 것을 볼 수 있습니다. 이것이 바로 변수 선택 효과입니다. 진정한 비영 계수를 가진 변수들이 먼저 모델에 들어오고, 노이즈 변수들은 나중에 들어오거나 아예 들어오지 않습니다.

교차 검증으로 최적 $\lambda$를 선택하면:

```python
lasso_cv = LassoCV(alphas=alphas, cv=5, max_iter=5000)
lasso_cv.fit(X_scaled, y)
print(f"최적 lambda: {lasso_cv.alpha_:.6f}")
print(f"선택된 변수 수: {np.sum(np.abs(lasso_cv.coef_) > 1e-10)}")
```

---

## [Part 12] 실습: Elastic Net 구현 (약 5분)

### 슬라이드: Elastic Net 좌표 하강법

Elastic Net은 Lasso의 업데이트 규칙에 L2 패널티를 분모에 추가한 것입니다:

```python
class ElasticNetFromScratch:
    def __init__(self, alpha=1.0, l1_ratio=0.5, max_iter=1000, tol=1e-6):
        self.alpha = alpha
        self.l1_ratio = l1_ratio
        self.max_iter = max_iter
        self.tol = tol

    def fit(self, X, y):
        n_samples, n_features = X.shape
        self.X_mean_ = np.mean(X, axis=0)
        self.y_mean_ = np.mean(y)
        X_c = X - self.X_mean_
        y_c = y - self.y_mean_

        l1_penalty = self.alpha * self.l1_ratio
        l2_penalty = self.alpha * (1 - self.l1_ratio)
        col_norms_sq = np.sum(X_c ** 2, axis=0) / n_samples

        w = np.zeros(n_features)
        residual = y_c.copy()

        for iteration in range(self.max_iter):
            w_old = w.copy()
            for j in range(n_features):
                residual += X_c[:, j] * w[j]
                rho_j = X_c[:, j].T @ residual / n_samples
                denominator = col_norms_sq[j] + l2_penalty
                if denominator > 0:
                    w[j] = soft_threshold(rho_j, l1_penalty) / denominator
                else:
                    w[j] = 0.0
                residual -= X_c[:, j] * w[j]

            if np.max(np.abs(w - w_old)) < self.tol:
                break

        self.coef_ = w
        self.intercept_ = self.y_mean_ - self.X_mean_ @ self.coef_
        return self
```

Lasso 코드와 비교해 보면, 분모에 `l2_penalty`가 추가된 것이 유일한 차이점입니다. 매우 간단하죠?

### 슬라이드: 그룹화 효과 시연

상관된 특성 그룹이 있는 데이터를 생성하여 Ridge, Lasso, Elastic Net을 비교합니다:

```python
# Ridge vs Lasso vs Elastic Net 비교
ridge_cv = RidgeCV(alphas=alphas_grid, cv=5, scoring='neg_mean_squared_error')
lasso_cv = LassoCV(alphas=alphas_grid, cv=5, max_iter=5000)
enet_cv = ElasticNetCV(alphas=alphas_grid, l1_ratio=0.5, cv=5, max_iter=5000)
```

실험 결과의 핵심 관찰:

1. **Ridge**: 모든 변수의 계수가 0이 아닙니다. 노이즈 변수도 작은 계수를 가집니다. 그룹 내 변수의 계수는 유사합니다.

2. **Lasso**: 변수 선택이 이루어집니다. 그러나 그룹 1(x0, x1, x2) 중 **하나만 선택**하고 나머지를 제거하는 경향이 있습니다. 이것이 Lasso의 그룹화 효과 부재 문제입니다.

3. **Elastic Net**: 변수 선택과 그룹화 효과를 동시에 달성합니다. 그룹 1의 세 변수가 모두 유사한 계수를 가지면서, 노이즈 변수는 0이 됩니다.

### 슬라이드: 제약 영역 시각화

PPT에서 세 가지 제약 영역을 나란히 보겠습니다:

- **L2 (Ridge)**: 원 형태 -- $\beta_1^2 + \beta_2^2 \leq t$
- **L1 (Lasso)**: 마름모 형태 -- $|\beta_1| + |\beta_2| \leq t$ (꼭짓점에서 변수 선택)
- **Elastic Net**: 둥근 마름모 형태 -- 희소성과 안정성의 균형

---

## [Part 13] 응용사례 (약 3분)

### 슬라이드: 부동산 가격 예측

캘리포니아 주택 가격 데이터셋을 사용한 예시를 보겠습니다.

```python
from sklearn.datasets import fetch_california_housing
housing = fetch_california_housing()
# 샘플 수: 20,640, 특성 수: 8
# 타겟: 중위 주택 가격 (단위: 10만 달러)
```

주요 계수 해석:

| 특성 | 의미 | 회귀 계수 방향 |
|------|------|-------------|
| MedInc | 중위 소득 | 강한 양(+) |
| HouseAge | 주택 연령 | 양(+) |
| Latitude | 위도 | 음(-) |

R2가 약 0.58로, 선형 모델의 한계를 보여줍니다. 비선형 모델(Random Forest, XGBoost 등)을 사용하면 성능이 향상됩니다.

### 슬라이드: 광고비-매출 분석

마케팅 분야의 전형적인 회귀 분석입니다. TV, 라디오, 신문 광고비가 매출에 미치는 영향을 분석합니다.

분석 결과, Elastic Net이 신문 광고의 계수를 0 근처로 축소하여 실질적으로 제거합니다. 이는 "신문 광고 예산을 TV와 라디오로 재배분하라"는 실무적 시사점을 제공합니다.

---

## [Part 14] 핵심 요약 및 마무리 (약 2분)

### 슬라이드: 이론 요약표

| 개념 | 핵심 수식 | 핵심 특성 |
|------|----------|----------|
| **OLS** | $\hat{\boldsymbol{\beta}} = (\mathbf{X}^T\mathbf{X})^{-1}\mathbf{X}^T\mathbf{y}$ | BLUE, 비편향 |
| **Ridge** | $\hat{\boldsymbol{\beta}} = (\mathbf{X}^T\mathbf{X} + \lambda\mathbf{I})^{-1}\mathbf{X}^T\mathbf{y}$ | L2, 축소, 닫힌 형태 해 |
| **Lasso** | $\min \frac{1}{2n}\|\mathbf{y}-\mathbf{X}\boldsymbol{\beta}\|^2 + \lambda\|\boldsymbol{\beta}\|_1$ | L1, 변수 선택, 좌표 하강법 |
| **Elastic Net** | L1+L2 혼합 정규화 | 그룹화 효과 |
| **SCAD** | 비볼록 패널티 | 오라클 성질 |

### 슬라이드: 핵심 논문 연대기

| 연도 | 논문 | 핵심 기여 |
|------|------|----------|
| 1970 | Hoerl & Kennard | Ridge, 편향-분산 트레이드오프 |
| 1996 | Tibshirani | Lasso, L1을 통한 변수 선택 |
| 2001 | Fan & Li | SCAD, 오라클 성질 |
| 2005 | Zou & Hastie | Elastic Net, 그룹화 효과 |
| 2010 | Friedman et al. | glmnet, 좌표 하강법 |

### 슬라이드: 방법 선택 가이드

```
다중공선성이 심한가?
+-- YES --> Ridge 또는 Elastic Net
|           +-- 변수 선택이 필요한가?
|           |   +-- YES --> Elastic Net
|           |   +-- NO  --> Ridge
|           +-- 상관된 변수 그룹이 있는가?
|               +-- YES --> Elastic Net (그룹화 효과)
|               +-- NO  --> 상황에 따라 Ridge 또는 Lasso
+-- NO  --> OLS 또는 Lasso
            +-- 변수 수가 많은가?
            |   +-- YES --> Lasso (변수 선택)
            |   +-- NO  --> OLS
            +-- p > n 인가?
                +-- YES --> Elastic Net
                +-- NO  --> Lasso
```

이것으로 4장 선형회귀 강의를 마치겠습니다. 오늘 배운 내용은 앞으로 다룰 로지스틱 회귀, 신경망 등 고급 모델의 기초가 되니 반드시 복습하시기 바랍니다.

---

## [부록] 복습 질문 10개

다음 질문들을 과제로 제출해 주시기 바랍니다. 수학적 유도와 설명을 포함하여 답안을 작성하세요.

**질문 1. 정규방정식 유도**: OLS의 비용 함수 $RSS(\boldsymbol{\beta}) = \|\mathbf{y} - \mathbf{X}\boldsymbol{\beta}\|^2$를 $\boldsymbol{\beta}$에 대해 행렬 미분하여 정규방정식을 유도하라. 이 해가 최솟값임을 헤시안으로 확인하라.

**질문 2. 가우스-마르코프 정리의 한계**: 가우스-마르코프 정리는 OLS가 BLUE임을 보장한다. 그런데 왜 Ridge 회귀가 OLS보다 MSE 관점에서 더 나을 수 있는가? $MSE = \text{Var} + \text{Bias}^2$로 설명하라.

**질문 3. Ridge의 닫힌 형태 해**: Ridge 회귀의 목적 함수를 미분하여 닫힌 형태 해를 유도하라. $\lambda\mathbf{I}$가 조건수를 개선하는 이유를 설명하라.

**질문 4. L1 vs L2 기하학**: Lasso는 변수 선택이 가능하고 Ridge는 불가능한 이유를 제약 영역의 기하학으로 설명하라.

**질문 5. 연성 임계값 연산자**: $S(z, \gamma) = \text{sign}(z) \cdot \max(|z| - \gamma, 0)$의 동작을 세 구간으로 나누어 설명하라.

**질문 6. Elastic Net의 그룹화 효과**: Lasso의 그룹화 효과 부재 문제와 Elastic Net의 해결 방법을 설명하라.

**질문 7. 좌표 하강법의 효율성**: 따뜻한 시작과 활성 집합 전략이 어떻게 계산 속도를 향상시키는지 기술하라.

**질문 8. SCAD와 오라클 성질**: 오라클 성질의 두 가지 조건을 기술하고, Lasso가 이를 만족하지 못하는 이유와 SCAD의 해결 방법을 설명하라.

**질문 9. 베이지안 해석**: Ridge와 Lasso를 각각 베이지안 MAP 관점에서 해석하라.

**질문 10. 회귀 진단**: (a) 깔때기 모양 잔차 패턴, (b) Q-Q plot 꼬리 이탈, (c) Cook's distance > 1인 관측치에 대한 진단과 대응을 기술하라.

---

> **참고 문헌**
>
> - Hoerl, A. E., & Kennard, R. W. (1970). Ridge Regression: Biased Estimation for Nonorthogonal Problems. *Technometrics*, 12(1), 55-67.
> - Tibshirani, R. (1996). Regression Shrinkage and Selection via the Lasso. *JRSS Series B*, 58(1), 267-288.
> - Fan, J., & Li, R. (2001). Variable Selection via Nonconcave Penalized Likelihood and its Oracle Properties. *JASA*, 96(456), 1348-1360.
> - Zou, H., & Hastie, T. (2005). Regularization and Variable Selection via the Elastic Net. *JRSS Series B*, 67(2), 301-320.
> - Friedman, J., Hastie, T., & Tibshirani, R. (2010). Regularization Paths for Generalized Linear Models via Coordinate Descent. *Journal of Statistical Software*, 33(1), 1-22.
