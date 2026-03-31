# -*- coding: utf-8 -*-
"""
03_rare_events_logistic.py
희소 사건 데이터에서의 로지스틱 회귀 문제와 교정 방법

King & Zeng (2001) "Logistic Regression in Rare Events Data"의 핵심 결과 재현:
1. 표준 로지스틱 회귀가 희소 사건의 확률을 과소추정하는 문제 입증
2. 사전 교정(Prior Correction)을 통한 절편 보정
3. 가중 로지스틱 회귀(Weighted Logistic Regression)를 통한 편향 교정
4. ROC 곡선과 보정 곡선(Calibration Plot) 비교

구현 내용:
- 다양한 불균형 비율의 데이터셋 생성
- 표준 vs 가중 vs 사전교정 로지스틱 회귀 비교
- ROC 곡선, 보정 곡선 시각화
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, roc_curve, roc_auc_score,
    precision_recall_curve, average_precision_score,
    classification_report, confusion_matrix
)
from sklearn.preprocessing import StandardScaler
from sklearn.calibration import calibration_curve


# ============================================================
# 1. 불균형 데이터 생성 함수
# ============================================================

def create_imbalanced_data(n_samples=10000, positive_rate=0.02,
                           n_features=10, random_state=42):
    """
    희소 사건(rare events) 데이터셋 생성

    King & Zeng(2001)이 다룬 유형의 데이터:
    - 양성 사례(positive)가 매우 드문 이진 분류 데이터
    - 정치학 예: 국제 분쟁 (~1-3%), 쿠데타 (~1% 미만)
    - 실전 예: 사기 탐지 (~0.1%), 희귀 질환 진단 (~1%)

    매개변수:
        n_samples: 전체 표본 수
        positive_rate: 양성 비율 (0.01 = 1%)
        n_features: 특성 수
        random_state: 랜덤 시드

    반환:
        X, y: 특성 행렬과 레이블
    """
    X, y = make_classification(
        n_samples=n_samples,
        n_features=n_features,
        n_informative=6,
        n_redundant=2,
        n_clusters_per_class=1,
        weights=[1 - positive_rate, positive_rate],
        class_sep=1.5,
        flip_y=0.01,
        random_state=random_state
    )

    return X, y


# ============================================================
# 2. 사전 교정 (Prior Correction) 구현
# ============================================================

def prior_correction(model, population_rate, sample_rate):
    """
    King & Zeng(2001)의 사전 교정(Prior Correction) 방법

    케이스-통제 설계 또는 불균형 표본에서의 절편 보정.
    표본에서의 양성 비율과 인구에서의 실제 양성 비율이 다를 때,
    절편을 보정하여 예측 확률의 편향을 교정한다.

    수식:
        beta_0_corrected = beta_0 - ln[(1-tau)/tau * y_bar/(1-y_bar)]

    여기서:
        tau = 인구의 실제 양성 비율 (population_rate)
        y_bar = 표본의 양성 비율 (sample_rate)

    매개변수:
        model: 학습된 LogisticRegression 모델
        population_rate: 인구에서의 실제 양성 비율
        sample_rate: 학습 표본에서의 양성 비율

    반환:
        correction: 절편 보정값
    """
    correction = np.log(
        ((1 - population_rate) / population_rate) *
        (sample_rate / (1 - sample_rate))
    )
    return correction


def predict_with_prior_correction(model, X, population_rate, sample_rate):
    """
    사전 교정이 적용된 예측 확률 계산

    원래 모델의 로짓 값에서 보정 항을 빼서 보정된 확률을 산출한다.

    매개변수:
        model: 학습된 LogisticRegression 모델
        X: 입력 특성
        population_rate: 인구의 실제 양성 비율
        sample_rate: 학습 표본의 양성 비율

    반환:
        corrected_prob: 보정된 예측 확률
    """
    # 원래 로짓 값 계산
    logits = np.dot(X, model.coef_[0]) + model.intercept_[0]

    # 보정 항 계산 및 적용
    correction = prior_correction(model, population_rate, sample_rate)
    corrected_logits = logits - correction

    # 시그모이드 함수로 확률 변환
    corrected_prob = 1.0 / (1.0 + np.exp(-corrected_logits))

    return corrected_prob


# ============================================================
# 3. 실험 1: 희소 사건에서의 편향 입증
# ============================================================

print("=" * 70)
print("실험 1: 다양한 불균형 비율에서의 로지스틱 회귀 편향 분석")
print("  King & Zeng(2001): 양성 비율이 낮을수록 확률 과소추정")
print("=" * 70)

positive_rates = [0.50, 0.20, 0.10, 0.05, 0.02, 0.01]
n_simulations = 30  # 각 비율에서 반복 시뮬레이션 횟수

print(f"\n{'양성비율':>8s} | {'실제비율':>8s} | {'예측평균':>8s} | {'편향':>8s} | {'과소추정%':>10s}")
print("-" * 60)

bias_results = []

for rate in positive_rates:
    pred_means = []

    for seed in range(n_simulations):
        X, y = create_imbalanced_data(
            n_samples=5000, positive_rate=rate, random_state=seed
        )

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=seed, stratify=y
        )

        scaler = StandardScaler()
        X_train_s = scaler.fit_transform(X_train)
        X_test_s = scaler.transform(X_test)

        model = LogisticRegression(max_iter=2000, random_state=42)
        model.fit(X_train_s, y_train)

        # 테스트 세트에서 양성 클래스의 평균 예측 확률
        prob = model.predict_proba(X_test_s)[:, 1]
        actual_positive_rate = y_test.mean()
        predicted_mean = prob.mean()
        pred_means.append(predicted_mean)

    avg_pred_mean = np.mean(pred_means)
    bias = avg_pred_mean - rate
    underestimate_pct = (1 - avg_pred_mean / rate) * 100 if rate > 0 else 0

    bias_results.append({
        'rate': rate,
        'predicted': avg_pred_mean,
        'bias': bias,
        'underestimate': underestimate_pct
    })

    print(f"{rate:>8.2%} | {rate:>8.4f} | {avg_pred_mean:>8.4f} | "
          f"{bias:>+8.4f} | {underestimate_pct:>9.1f}%")


# 편향 시각화
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

rates = [r['rate'] for r in bias_results]
preds = [r['predicted'] for r in bias_results]
biases = [r['bias'] for r in bias_results]
underestimates = [r['underestimate'] for r in bias_results]

# 좌측: 실제 비율 vs 예측 평균
axes[0].plot(rates, preds, 'ro-', linewidth=2, markersize=8, label='예측 평균')
axes[0].plot(rates, rates, 'b--', linewidth=1.5, label='완벽한 보정 (y=x)')
axes[0].set_xlabel('실제 양성 비율', fontsize=12)
axes[0].set_ylabel('예측 확률 평균', fontsize=12)
axes[0].set_title('실제 비율 vs 예측 확률 평균', fontsize=13)
axes[0].legend(fontsize=11)
axes[0].grid(True, alpha=0.3)

# 우측: 과소추정 비율
axes[1].bar(range(len(rates)), underestimates, color='salmon', edgecolor='black')
axes[1].set_xticks(range(len(rates)))
axes[1].set_xticklabels([f'{r:.0%}' for r in rates])
axes[1].set_xlabel('실제 양성 비율', fontsize=12)
axes[1].set_ylabel('과소추정 비율 (%)', fontsize=12)
axes[1].set_title('양성 비율별 과소추정 정도', fontsize=13)
axes[1].grid(True, alpha=0.3, axis='y')

plt.suptitle('King & Zeng (2001): 희소 사건에서의 로지스틱 회귀 편향', fontsize=15, y=1.02)
plt.tight_layout()
plt.savefig('rare_events_bias.png', dpi=150, bbox_inches='tight')
plt.show()
print("\n[저장 완료] rare_events_bias.png")


# ============================================================
# 4. 실험 2: 교정 방법 비교
# ============================================================

print("\n" + "=" * 70)
print("실험 2: 교정 방법 비교")
print("  1) 표준 로지스틱 회귀 (보정 없음)")
print("  2) 가중 로지스틱 회귀 (class_weight='balanced')")
print("  3) 사전 교정 (Prior Correction)")
print("=" * 70)

# 2% 양성 비율의 불균형 데이터 생성
POSITIVE_RATE = 0.02  # 인구의 실제 양성 비율

X, y = create_imbalanced_data(
    n_samples=10000,
    positive_rate=POSITIVE_RATE,
    n_features=10,
    random_state=42
)

print(f"\n데이터 개요:")
print(f"  전체 표본: {len(y)}")
print(f"  양성 (1): {np.sum(y == 1)} ({np.mean(y):.2%})")
print(f"  음성 (0): {np.sum(y == 0)} ({1-np.mean(y):.2%})")

# 학습/테스트 분리
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

# 표준화
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

sample_positive_rate = y_train.mean()
print(f"  학습 데이터 양성 비율: {sample_positive_rate:.4f}")

# --- 모델 1: 표준 로지스틱 회귀 ---
print("\n[모델 1] 표준 로지스틱 회귀 (보정 없음)")
model_standard = LogisticRegression(max_iter=2000, random_state=42)
model_standard.fit(X_train_s, y_train)
prob_standard = model_standard.predict_proba(X_test_s)[:, 1]
pred_standard = model_standard.predict(X_test_s)

print(f"  예측 확률 평균: {prob_standard.mean():.6f}")
print(f"  정확도: {accuracy_score(y_test, pred_standard):.4f}")
print(f"  AUC: {roc_auc_score(y_test, prob_standard):.4f}")

# --- 모델 2: 가중 로지스틱 회귀 ---
print("\n[모델 2] 가중 로지스틱 회귀 (class_weight='balanced')")
model_weighted = LogisticRegression(
    max_iter=2000, random_state=42,
    class_weight='balanced'  # King & Zeng의 가중 추정법에 대응
)
model_weighted.fit(X_train_s, y_train)
prob_weighted = model_weighted.predict_proba(X_test_s)[:, 1]
pred_weighted = model_weighted.predict(X_test_s)

print(f"  예측 확률 평균: {prob_weighted.mean():.6f}")
print(f"  정확도: {accuracy_score(y_test, pred_weighted):.4f}")
print(f"  AUC: {roc_auc_score(y_test, prob_weighted):.4f}")

# --- 모델 3: 사전 교정 ---
print("\n[모델 3] 사전 교정 (Prior Correction)")
prob_corrected = predict_with_prior_correction(
    model_standard, X_test_s,
    population_rate=POSITIVE_RATE,
    sample_rate=sample_positive_rate
)
pred_corrected = (prob_corrected >= 0.5).astype(int)

# 사전 교정에서는 임계값을 양성 비율에 맞게 조정하는 것이 더 적절
# 기본 임계값 0.5 대신, 양성 비율을 임계값으로 사용
pred_corrected_adjusted = (prob_corrected >= POSITIVE_RATE).astype(int)

print(f"  예측 확률 평균: {prob_corrected.mean():.6f}")
print(f"  정확도 (임계값=0.5): {accuracy_score(y_test, pred_corrected):.4f}")
print(f"  정확도 (임계값={POSITIVE_RATE}): {accuracy_score(y_test, pred_corrected_adjusted):.4f}")
print(f"  AUC: {roc_auc_score(y_test, prob_corrected):.4f}")


# ============================================================
# 5. 분류 보고서 비교
# ============================================================

print("\n" + "=" * 70)
print("분류 보고서 비교")
print("=" * 70)

model_names = ["표준 LR", "가중 LR (balanced)", "사전 교정 (threshold=양성비율)"]
predictions = [pred_standard, pred_weighted, pred_corrected_adjusted]

for name, pred in zip(model_names, predictions):
    print(f"\n--- {name} ---")
    cm = confusion_matrix(y_test, pred)
    tn, fp, fn, tp = cm.ravel()
    print(f"  TN={tn:>4d}  FP={fp:>4d}")
    print(f"  FN={fn:>4d}  TP={tp:>4d}")

    if tp + fn > 0:
        recall = tp / (tp + fn)
        print(f"  재현율(Recall): {recall:.4f} (양성 {tp+fn}개 중 {tp}개 검출)")
    if tp + fp > 0:
        precision = tp / (tp + fp)
        print(f"  정밀도(Precision): {precision:.4f}")


# ============================================================
# 6. ROC 곡선 비교
# ============================================================

print("\n" + "=" * 70)
print("ROC 곡선 및 PR 곡선 시각화")
print("=" * 70)

fig, axes = plt.subplots(1, 2, figsize=(16, 7))

# --- ROC 곡선 ---
ax1 = axes[0]

models_info = [
    ("표준 LR", prob_standard, 'blue'),
    ("가중 LR (balanced)", prob_weighted, 'red'),
    ("사전 교정", prob_corrected, 'green'),
]

for name, prob, color in models_info:
    fpr, tpr, _ = roc_curve(y_test, prob)
    auc = roc_auc_score(y_test, prob)
    ax1.plot(fpr, tpr, color=color, linewidth=2, label=f'{name} (AUC={auc:.4f})')

ax1.plot([0, 1], [0, 1], 'k--', linewidth=1, alpha=0.5, label='무작위 기준선')
ax1.set_xlabel('위양성률 (FPR)', fontsize=12)
ax1.set_ylabel('진양성률 (TPR)', fontsize=12)
ax1.set_title('ROC 곡선 비교', fontsize=14)
ax1.legend(fontsize=10, loc='lower right')
ax1.grid(True, alpha=0.3)

# --- Precision-Recall 곡선 ---
ax2 = axes[1]

for name, prob, color in models_info:
    precision, recall, _ = precision_recall_curve(y_test, prob)
    ap = average_precision_score(y_test, prob)
    ax2.plot(recall, precision, color=color, linewidth=2,
             label=f'{name} (AP={ap:.4f})')

# 기준선: 양성 비율
baseline = y_test.mean()
ax2.axhline(y=baseline, color='black', linestyle='--', linewidth=1, alpha=0.5,
            label=f'기준선 (양성비율={baseline:.3f})')

ax2.set_xlabel('재현율 (Recall)', fontsize=12)
ax2.set_ylabel('정밀도 (Precision)', fontsize=12)
ax2.set_title('Precision-Recall 곡선 비교', fontsize=14)
ax2.legend(fontsize=10, loc='upper right')
ax2.grid(True, alpha=0.3)

plt.suptitle(f'희소 사건 데이터 (양성 비율: {POSITIVE_RATE:.0%}) - 모델 비교',
             fontsize=15, y=1.02)
plt.tight_layout()
plt.savefig('rare_events_roc_pr_curves.png', dpi=150, bbox_inches='tight')
plt.show()
print("[저장 완료] rare_events_roc_pr_curves.png")


# ============================================================
# 7. 보정 곡선 (Calibration Plot) 비교
# ============================================================

print("\n" + "=" * 70)
print("보정 곡선 (Calibration Plot) 비교")
print("  완벽한 보정: 예측 확률 = 실제 발생 비율")
print("=" * 70)

fig, axes = plt.subplots(1, 3, figsize=(18, 6))

for idx, (name, prob, color) in enumerate(models_info):
    ax = axes[idx]

    # 보정 곡선 계산
    # 희소 사건이므로 bin 수를 줄여야 의미 있는 결과가 나옴
    try:
        fraction_of_positives, mean_predicted_value = calibration_curve(
            y_test, prob, n_bins=10, strategy='quantile'
        )

        ax.plot(mean_predicted_value, fraction_of_positives,
                color=color, linewidth=2, marker='o', markersize=6,
                label=name)
        ax.plot([0, 1], [0, 1], 'k--', linewidth=1, alpha=0.5,
                label='완벽한 보정')
    except ValueError:
        # 예측 확률이 매우 좁은 범위에 집중되면 binning이 실패할 수 있음
        ax.text(0.5, 0.5, '보정 곡선 생성 불가\n(확률 범위가 너무 좁음)',
                transform=ax.transAxes, ha='center', va='center', fontsize=11)

    # 예측 확률 히스토그램 (하단)
    ax_hist = ax.twinx()
    ax_hist.hist(prob, bins=30, color=color, alpha=0.2, edgecolor='gray')
    ax_hist.set_ylabel('빈도', fontsize=10, color='gray')
    ax_hist.tick_params(axis='y', labelcolor='gray')

    ax.set_xlabel('예측 확률 평균', fontsize=11)
    ax.set_ylabel('실제 양성 비율', fontsize=11)
    ax.set_title(name, fontsize=13)
    ax.legend(fontsize=9, loc='upper left')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.02)

plt.suptitle('보정 곡선 비교 (Calibration Plot)', fontsize=15, y=1.02)
plt.tight_layout()
plt.savefig('rare_events_calibration.png', dpi=150, bbox_inches='tight')
plt.show()
print("[저장 완료] rare_events_calibration.png")


# ============================================================
# 8. 임계값 분석
# ============================================================

print("\n" + "=" * 70)
print("임계값(Threshold) 분석")
print("  희소 사건에서는 기본 임계값 0.5가 부적절함")
print("=" * 70)

thresholds = [0.01, 0.02, 0.05, 0.1, 0.2, 0.3, 0.5]

print(f"\n[표준 로지스틱 회귀] 임계값별 성능:")
print(f"{'임계값':>8s} | {'정확도':>8s} | {'정밀도':>8s} | {'재현율':>8s} | {'F1':>8s} | {'TP':>5s} | {'FP':>5s} | {'FN':>5s}")
print("-" * 75)

for threshold in thresholds:
    pred_t = (prob_standard >= threshold).astype(int)
    cm = confusion_matrix(y_test, pred_t)
    tn, fp, fn, tp = cm.ravel()

    acc = accuracy_score(y_test, pred_t)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    print(f"{threshold:>8.2f} | {acc:>8.4f} | {precision:>8.4f} | "
          f"{recall:>8.4f} | {f1:>8.4f} | {tp:>5d} | {fp:>5d} | {fn:>5d}")

print("\n주의: 양성 비율이 2%이므로, 임계값=0.5에서는 양성을 거의 검출하지 못함")
print("     임계값을 낮추면 재현율이 증가하지만, 정밀도가 감소함 (트레이드오프)")


# ============================================================
# 9. 가중치별 성능 비교
# ============================================================

print("\n" + "=" * 70)
print("클래스 가중치별 성능 비교")
print("  King & Zeng(2001)의 가중 추정법을 다양한 가중치로 실험")
print("=" * 70)

weight_ratios = [1, 5, 10, 20, 50, 100]

print(f"\n{'양성가중치':>10s} | {'정확도':>8s} | {'정밀도':>8s} | {'재현율':>8s} | {'F1':>8s} | {'AUC':>8s}")
print("-" * 65)

for w in weight_ratios:
    model_w = LogisticRegression(
        max_iter=2000, random_state=42,
        class_weight={0: 1, 1: w}
    )
    model_w.fit(X_train_s, y_train)
    prob_w = model_w.predict_proba(X_test_s)[:, 1]
    pred_w = model_w.predict(X_test_s)

    cm = confusion_matrix(y_test, pred_w)
    tn, fp, fn, tp = cm.ravel()

    acc = accuracy_score(y_test, pred_w)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    auc = roc_auc_score(y_test, prob_w)

    print(f"{w:>10d} | {acc:>8.4f} | {precision:>8.4f} | "
          f"{recall:>8.4f} | {f1:>8.4f} | {auc:>8.4f}")


# ============================================================
# 10. 종합 시각화: 불균형 비율에 따른 모델 비교
# ============================================================

print("\n" + "=" * 70)
print("종합 분석: 불균형 비율에 따른 표준 vs 가중 로지스틱 회귀 비교")
print("=" * 70)

test_rates = [0.50, 0.20, 0.10, 0.05, 0.02, 0.01]
standard_aucs = []
weighted_aucs = []
standard_recalls = []
weighted_recalls = []

for rate in test_rates:
    aucs_std = []
    aucs_wt = []
    recalls_std = []
    recalls_wt = []

    for seed in range(20):
        X_r, y_r = create_imbalanced_data(
            n_samples=5000, positive_rate=rate, random_state=seed
        )

        X_tr, X_te, y_tr, y_te = train_test_split(
            X_r, y_r, test_size=0.3, random_state=seed, stratify=y_r
        )

        sc = StandardScaler()
        X_tr_s = sc.fit_transform(X_tr)
        X_te_s = sc.transform(X_te)

        # 표준 모델
        m_std = LogisticRegression(max_iter=2000, random_state=42)
        m_std.fit(X_tr_s, y_tr)
        p_std = m_std.predict_proba(X_te_s)[:, 1]
        pred_std = m_std.predict(X_te_s)

        # 가중 모델
        m_wt = LogisticRegression(max_iter=2000, random_state=42,
                                   class_weight='balanced')
        m_wt.fit(X_tr_s, y_tr)
        p_wt = m_wt.predict_proba(X_te_s)[:, 1]
        pred_wt = m_wt.predict(X_te_s)

        aucs_std.append(roc_auc_score(y_te, p_std))
        aucs_wt.append(roc_auc_score(y_te, p_wt))

        # 재현율 계산
        cm_std = confusion_matrix(y_te, pred_std)
        cm_wt = confusion_matrix(y_te, pred_wt)

        _, _, fn_s, tp_s = cm_std.ravel()
        _, _, fn_w, tp_w = cm_wt.ravel()

        recalls_std.append(tp_s / (tp_s + fn_s) if (tp_s + fn_s) > 0 else 0)
        recalls_wt.append(tp_w / (tp_w + fn_w) if (tp_w + fn_w) > 0 else 0)

    standard_aucs.append(np.mean(aucs_std))
    weighted_aucs.append(np.mean(aucs_wt))
    standard_recalls.append(np.mean(recalls_std))
    weighted_recalls.append(np.mean(recalls_wt))

# 시각화
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# AUC 비교
x_pos = np.arange(len(test_rates))
width = 0.35

axes[0].bar(x_pos - width/2, standard_aucs, width, color='steelblue',
            edgecolor='black', label='표준 LR')
axes[0].bar(x_pos + width/2, weighted_aucs, width, color='salmon',
            edgecolor='black', label='가중 LR (balanced)')
axes[0].set_xticks(x_pos)
axes[0].set_xticklabels([f'{r:.0%}' for r in test_rates])
axes[0].set_xlabel('양성 비율', fontsize=12)
axes[0].set_ylabel('AUC', fontsize=12)
axes[0].set_title('양성 비율별 AUC 비교', fontsize=13)
axes[0].legend(fontsize=10)
axes[0].grid(True, alpha=0.3, axis='y')
axes[0].set_ylim(0.5, 1.0)

# 재현율 비교
axes[1].bar(x_pos - width/2, standard_recalls, width, color='steelblue',
            edgecolor='black', label='표준 LR')
axes[1].bar(x_pos + width/2, weighted_recalls, width, color='salmon',
            edgecolor='black', label='가중 LR (balanced)')
axes[1].set_xticks(x_pos)
axes[1].set_xticklabels([f'{r:.0%}' for r in test_rates])
axes[1].set_xlabel('양성 비율', fontsize=12)
axes[1].set_ylabel('재현율 (Recall)', fontsize=12)
axes[1].set_title('양성 비율별 재현율 비교', fontsize=13)
axes[1].legend(fontsize=10)
axes[1].grid(True, alpha=0.3, axis='y')
axes[1].set_ylim(0, 1.0)

plt.suptitle('King & Zeng (2001): 불균형 비율에 따른 표준 vs 가중 로지스틱 회귀',
             fontsize=15, y=1.02)
plt.tight_layout()
plt.savefig('rare_events_comprehensive_comparison.png', dpi=150, bbox_inches='tight')
plt.show()
print("[저장 완료] rare_events_comprehensive_comparison.png")


# ============================================================
# 11. 최종 요약
# ============================================================

print("\n" + "=" * 70)
print("최종 요약: King & Zeng (2001) 핵심 결과")
print("=" * 70)
print(f"""
King & Zeng (2001)의 핵심 발견 재현 결과:

1. 편향 존재 확인:
   - 양성 비율이 낮을수록 표준 로지스틱 회귀의 확률 과소추정이 심해짐
   - 양성 비율 2%: 예측 확률이 실제보다 약 {bias_results[-2]['underestimate']:.0f}% 과소추정
   - 양성 비율 1%: 예측 확률이 실제보다 약 {bias_results[-1]['underestimate']:.0f}% 과소추정

2. 교정 방법의 효과:
   - 가중 로지스틱 회귀 (class_weight='balanced'):
     AUC는 유사하지만 재현율이 크게 향상됨
   - 사전 교정 (Prior Correction):
     예측 확률의 보정은 가능하나 분류 성능 개선은 임계값 조정이 필요

3. 실용적 권고사항:
   - 양성 비율 > 20%: 표준 로지스틱 회귀 사용 가능
   - 양성 비율 5~20%: 가중 로지스틱 회귀 권고
   - 양성 비율 < 5%: 반드시 보정 방법 적용 (가중치 또는 사전 교정)
   - 평가 지표: accuracy 대신 AUC, Recall, F1, PR-AUC 사용
   - 임계값: 0.5 대신 양성 비율 또는 비즈니스 요구에 맞게 조정

4. King & Zeng 논문의 기여:
   - 희소 사건에서 MLE의 유한표본 편향을 이론적으로 증명
   - 사전 교정, 가중 추정, 편향 보정 등 실용적 교정 방법 제시
   - 표본 설계에 대한 가이드라인 (양성의 2~5배 음성이면 충분)
""")
