# -*- coding: utf-8 -*-
"""
04_Linear Regression
4장 선형 회귀 - 보험료 예측하기
"""

# ============================================================
# 4.2 라이브러리 및 데이터 불러오기
# ============================================================
import pandas as pd

file_url = 'https://media.githubusercontent.com/media/musthave-ML10/data_source/main/insurance.csv'
data = pd.read_csv(file_url)

# ============================================================
# 4.3 데이터 확인하기
# ============================================================
print(data)
print(data.head())
print(data.info())
print(data.describe())
print(round(data.describe(), 2))

# ============================================================
# 4.4 전처리: 학습셋과 실험셋 나누기
# ============================================================
X = data[['age', 'sex', 'bmi', 'children', 'smoker']]
y = data['charges']

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=100)

# ============================================================
# 4.5 모델링
# ============================================================
from sklearn.linear_model import LinearRegression

model = LinearRegression()
model.fit(X_train, y_train)

# ============================================================
# 4.6 모델을 활용해 예측하기
# ============================================================
pred = model.predict(X_test)

# ============================================================
# 4.7 예측 모델 평가하기
# ============================================================
comparison = pd.DataFrame({'actual': y_test, 'pred': pred})
print(comparison)

import matplotlib.pyplot as plt  # ❶
import seaborn as sns  # ❷

plt.figure(figsize=(10, 10))  # ❶ 그래프 크기를 정의
sns.scatterplot(x='actual', y='pred', data=comparison)  # ❷
plt.show()

from sklearn.metrics import mean_squared_error  # ❶
print(mean_squared_error(y_test, pred) ** 0.5)  # ❷ RMSE

print(mean_squared_error(y_test, pred) ** 0.5)  # squared=False 대신 직접 루트

print(model.score(X_train, y_train))  # R²

# ============================================================
# 4.8 이해하기 : 선형 회귀 (Linear Regression)
# ============================================================
print(model.coef_)
print(pd.Series(model.coef_, index=X.columns))
print(model.intercept_)
