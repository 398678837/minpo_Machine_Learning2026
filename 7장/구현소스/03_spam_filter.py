# -*- coding: utf-8 -*-
"""
03_spam_filter.py
TF-IDF + 나이브 베이즈를 사용한 완전한 스팸 필터 구현

구현 내용:
1. 텍스트 전처리 파이프라인 (특수문자 제거, 소문자 변환, 불용어 제거)
2. TF-IDF 벡터화 + MultinomialNB 스팸 분류기
3. 특성 중요도 분석 (스팸/정상 판별에 기여하는 핵심 단어)
4. 오분류 분석 (어떤 메일이 왜 잘못 분류되었는지)
5. 다양한 나이브 베이즈 변형 비교

데이터: 직접 생성한 스팸/정상 데이터셋
참고 논문: Metsis et al. (2006), Rennie et al. (2003)
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import string
import re
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.naive_bayes import MultinomialNB, BernoulliNB, ComplementNB
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (accuracy_score, classification_report,
                             confusion_matrix, roc_curve, auc,
                             precision_recall_curve)
from sklearn.pipeline import Pipeline
import warnings
warnings.filterwarnings('ignore')


# ============================================================
# 1. 데이터 생성
# ============================================================

def create_spam_dataset():
    """
    스팸/정상(ham) 이메일 데이터셋을 생성한다.
    실제 스팸 패턴을 반영하여 다양한 유형의 데이터를 포함한다.
    """
    spam_emails = [
        "Congratulations! You have been selected to receive a FREE gift card worth $500",
        "WINNER! You won $1,000,000 in our lottery! Claim your prize NOW!",
        "Free Viagra pills! Order now and get 50% discount on all medications",
        "Make money fast! Earn $5000 per week from home with this simple trick",
        "URGENT: Your bank account has been compromised. Click here immediately",
        "Buy cheap watches, handbags and electronics at wholesale prices today",
        "You are a winner of our international email lottery program claim now",
        "Free trial offer! Get premium membership absolutely free for 30 days",
        "Double your investment! Guaranteed returns of 200% in just one month",
        "Hot singles in your area want to meet you tonight! Click here",
        "Lose weight fast with our miracle diet pill! No exercise needed!",
        "Get paid to take surveys online! Easy money from the comfort of home",
        "Exclusive offer: free iPhone 15 Pro! Just pay shipping and handling",
        "Your PayPal account has been limited. Verify your identity now",
        "SPAM: Buy one get one free! Limited time clearance sale everything must go",
        "Free credit report! Check your score instantly no credit card required",
        "Work from home opportunity! Be your own boss and earn unlimited income",
        "Nigerian prince needs your help transferring $10 million dollars",
        "You have been pre-approved for a platinum credit card! Apply now",
        "Free vacation package to Hawaii! All inclusive resort stay for two",
        "Cheap prescription drugs online! No prescription needed fast delivery",
        "Congratulations on being our 1000th visitor! Claim your special prize",
        "ALERT: Unusual activity detected on your account please verify",
        "Make $500 daily posting links on social media from your phone",
        "Free casino bonus! Get $100 free chips when you sign up today",
        "Miracle weight loss supplement burns fat while you sleep guaranteed",
        "Earn your degree online in just 6 weeks! Accredited university diplomas",
        "Secret investment strategy revealed! Wall Street does not want you to know",
        "Free trial of premium cable channels! Watch movies sports and more",
        "URGENT: IRS notification you owe back taxes click here to resolve",
        "Amazing anti aging cream! Look 20 years younger in just one week",
        "Home business opportunity! Start your own online store with zero investment",
        "You qualified for government grant money! Claim your $25000 now",
        "Free smartphone upgrade! Trade in your old phone for latest model",
        "WINNER WINNER! You have been randomly selected for cash reward",
        "Diet pills that actually work! Lose 30 pounds in 30 days guaranteed",
        "Cheap flights and hotel deals! Save up to 80% on travel bookings",
        "Your computer has been infected! Download our free antivirus now",
        "Bitcoin investment opportunity! Turn $100 into $10000 this month",
        "Free gift with every purchase! Shop now and save big today",
    ]

    ham_emails = [
        "Hi John, are we still meeting for lunch tomorrow at noon?",
        "Please find attached the quarterly report for your review",
        "The team meeting has been rescheduled to 3pm on Thursday",
        "Thanks for sending the project proposal. I will review it tonight",
        "Can you pick up the kids from school today? I have a late meeting",
        "The client approved our design mockups. Great work everyone!",
        "I just submitted the expense report for last month's trip",
        "Let's catch up this weekend. Maybe grab coffee on Saturday morning?",
        "The new software update is available. Please install before Friday",
        "Happy birthday! Hope you have a wonderful celebration today",
        "I will be working remotely on Monday. You can reach me by email",
        "The conference registration deadline is next week. Have you signed up?",
        "Thanks for your help with the presentation. It went really well",
        "Can you send me the meeting minutes from yesterday's standup?",
        "I noticed a bug in the login page. Can we fix it before release?",
        "The kitchen is out of coffee. Can someone order more supplies?",
        "Great job on closing the deal with the new client this week!",
        "Please review the updated privacy policy and provide feedback",
        "My flight lands at 6pm. Can someone pick me up from the airport?",
        "The code review for the new feature is scheduled for tomorrow",
        "I finished the data analysis. The results are in the shared drive",
        "Can we discuss the budget allocation for next quarter this week?",
        "The office will be closed on Friday for the holiday weekend",
        "I need your signature on the contract before end of day today",
        "The networking event is tonight at the downtown convention center",
        "Please update your availability in the shared calendar for next week",
        "The server maintenance window is scheduled for Sunday 2am to 6am",
        "I really enjoyed the workshop yesterday. Learned a lot about Python",
        "Can you recommend a good restaurant for the team dinner tonight?",
        "The product launch is on track. All deliverables are completed",
        "I will be on vacation next week. Sarah will cover for me",
        "The new intern starts on Monday. Please help them get settled in",
        "Thanks for the ride home yesterday. Really appreciate your help",
        "Can we move the weekly sync to Tuesday instead of Wednesday?",
        "The quarterly results exceeded our targets by fifteen percent",
        "Please remember to submit your timesheet by end of day Friday",
        "I found an interesting article about machine learning. Sharing the link",
        "The air conditioning in the office is not working. I called maintenance",
        "Good morning team! Here is the agenda for today's planning session",
        "I am heading to the gym after work. Want to join me for a workout?",
        "The library book is due next Tuesday. Don't forget to return it",
        "Can you check if the shipment arrived at the warehouse today?",
        "The customer feedback survey results are ready for review",
        "I made reservations for our anniversary dinner on Saturday night",
        "The test results came back normal. Doctor says everything looks good",
        "Please prepare the slides for the board meeting next Wednesday",
        "I just finished reading the book you recommended. It was great",
        "The wifi password for the guest network has been changed",
        "Can you help me move the boxes from storage to the third floor?",
        "The recycling bins need to be emptied. Can facilities handle it?",
        "I saw your email about the project timeline. Let me check my schedule",
        "The parking lot will be repaved this weekend. Use the side entrance",
        "Thanks for organizing the team building event. Everyone had fun",
        "The printer on the second floor is jammed again. I called IT support",
        "Please check the inventory levels for the end of month report",
        "I updated the shared document with the latest pricing information",
        "The emergency drill is scheduled for next Tuesday at 10am",
        "Can you proof read this email before I send it to the client?",
        "The new policy takes effect next month. Please read the memo",
        "I ordered lunch for the meeting. Pizza and salads should arrive by noon",
    ]

    # 데이터프레임 생성
    texts = spam_emails + ham_emails
    labels = [1] * len(spam_emails) + [0] * len(ham_emails)
    df = pd.DataFrame({'text': texts, 'label': labels})
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    return df


# ============================================================
# 2. 텍스트 전처리
# ============================================================

def preprocess_text(text):
    """
    텍스트 전처리: 소문자 변환, 특수문자 제거, 숫자 처리

    매개변수:
        text: 원본 텍스트 문자열
    반환값:
        전처리된 텍스트 문자열
    """
    # 소문자 변환
    text = text.lower()

    # 숫자를 NUM 토큰으로 대체 (금액 패턴 보존)
    text = re.sub(r'\$[\d,]+', 'MONEY', text)
    text = re.sub(r'\d+%', 'PERCENT', text)
    text = re.sub(r'\d+', 'NUM', text)

    # 특수 문자 제거
    text = re.sub(r'[^\w\s]', ' ', text)

    # 다중 공백을 단일 공백으로
    text = re.sub(r'\s+', ' ', text).strip()

    return text


# ============================================================
# 3. 특성 중요도 분석
# ============================================================

def analyze_feature_importance(model, vectorizer, n_top=15):
    """
    스팸/정상 분류에 가장 중요한 단어를 식별한다.

    나이브 베이즈에서 log P(w | spam) - log P(w | ham)이 큰 단어가
    스팸 판별에 중요한 단어이다.

    매개변수:
        model: 학습된 나이브 베이즈 모델
        vectorizer: 학습된 벡터화기
        n_top: 표시할 상위 단어 수
    반환값:
        (스팸 상위 단어, 정상 상위 단어, 중요도 배열)
    """
    feature_names = vectorizer.get_feature_names_out()

    # log P(w | c) 값 추출
    log_probs = model.feature_log_prob_

    # 클래스 0 = 정상(ham), 클래스 1 = 스팸(spam)
    log_prob_ham = log_probs[0]
    log_prob_spam = log_probs[1]

    # 스팸 판별력 = log P(w | spam) - log P(w | ham)
    spam_importance = log_prob_spam - log_prob_ham

    # 스팸 판별에 중요한 단어 (양수: 스팸 지표)
    spam_top_idx = np.argsort(spam_importance)[-n_top:][::-1]
    spam_words = [(feature_names[i], spam_importance[i]) for i in spam_top_idx]

    # 정상 판별에 중요한 단어 (음수: 정상 지표)
    ham_top_idx = np.argsort(spam_importance)[:n_top]
    ham_words = [(feature_names[i], spam_importance[i]) for i in ham_top_idx]

    return spam_words, ham_words, spam_importance


# ============================================================
# 4. 오분류 분석
# ============================================================

def analyze_misclassifications(df_test, y_test, y_pred, y_proba):
    """
    오분류된 이메일을 분석한다.

    매개변수:
        df_test: 테스트 데이터프레임
        y_test: 실제 레이블
        y_pred: 예측 레이블
        y_proba: 예측 확률
    """
    misclassified = y_test != y_pred
    n_misclassified = np.sum(misclassified)

    print(f"\n오분류 분석: {n_misclassified}개 오분류 (총 {len(y_test)}개 중)")
    print("-" * 60)

    if n_misclassified == 0:
        print("  오분류된 이메일이 없습니다!")
        return

    test_texts = df_test['text'].values
    mis_indices = np.where(misclassified)[0]

    # FP (정상 -> 스팸) 분석
    fp_mask = (y_test == 0) & (y_pred == 1)
    fp_indices = np.where(fp_mask)[0]
    print(f"\n  FP (정상 메일을 스팸으로 오분류): {len(fp_indices)}개")
    for idx in fp_indices[:3]:
        print(f"    [{idx}] 스팸 확률: {y_proba[idx, 1]:.4f}")
        print(f"    텍스트: {test_texts[idx][:80]}...")

    # FN (스팸 -> 정상) 분석
    fn_mask = (y_test == 1) & (y_pred == 0)
    fn_indices = np.where(fn_mask)[0]
    print(f"\n  FN (스팸 메일을 정상으로 오분류): {len(fn_indices)}개")
    for idx in fn_indices[:3]:
        print(f"    [{idx}] 스팸 확률: {y_proba[idx, 1]:.4f}")
        print(f"    텍스트: {test_texts[idx][:80]}...")


# ============================================================
# 5. 메인 실행
# ============================================================

def main():
    print("=" * 70)
    print("완전한 스팸 필터 구현")
    print("TF-IDF + Naive Bayes 기반")
    print("=" * 70)

    np.random.seed(42)

    # --------------------------------------------------------
    # 5.1 데이터 준비
    # --------------------------------------------------------
    print("\n[1] 데이터 준비")
    df = create_spam_dataset()
    print(f"  전체 데이터: {len(df)}개")
    print(f"  스팸: {(df['label'] == 1).sum()}개, 정상: {(df['label'] == 0).sum()}개")

    # 전처리
    df['clean_text'] = df['text'].apply(preprocess_text)

    print(f"\n  전처리 예시:")
    for i in range(3):
        print(f"    원본: {df['text'].iloc[i][:60]}...")
        print(f"    전처리: {df['clean_text'].iloc[i][:60]}...")
        print()

    # 학습/테스트 분할
    X_train_df, X_test_df, y_train, y_test = train_test_split(
        df[['text', 'clean_text']], df['label'],
        test_size=0.25, random_state=42, stratify=df['label']
    )

    print(f"  학습: {len(X_train_df)}개, 테스트: {len(X_test_df)}개")

    # --------------------------------------------------------
    # 5.2 TF-IDF 벡터화 + MultinomialNB
    # --------------------------------------------------------
    print("\n[2] TF-IDF + MultinomialNB 스팸 필터")
    print("-" * 50)

    # TF-IDF 벡터화
    tfidf = TfidfVectorizer(
        max_features=5000,
        stop_words='english',
        ngram_range=(1, 2),    # 유니그램 + 바이그램
        min_df=2,              # 최소 2개 문서에 출현
        sublinear_tf=True      # TF에 로그 변환 적용 (Rennie 2003)
    )

    X_train_tfidf = tfidf.fit_transform(X_train_df['clean_text'])
    X_test_tfidf = tfidf.transform(X_test_df['clean_text'])

    print(f"  어휘 크기: {X_train_tfidf.shape[1]}개")

    # MultinomialNB 학습
    mnb = MultinomialNB(alpha=0.1)
    mnb.fit(X_train_tfidf, y_train)
    y_pred_mnb = mnb.predict(X_test_tfidf)
    y_proba_mnb = mnb.predict_proba(X_test_tfidf)

    acc_mnb = accuracy_score(y_test, y_pred_mnb)
    print(f"\n  MultinomialNB 정확도: {acc_mnb:.4f}")
    print(classification_report(y_test, y_pred_mnb,
                                target_names=['정상(Ham)', '스팸(Spam)']))

    # --------------------------------------------------------
    # 5.3 다양한 나이브 베이즈 변형 비교
    # --------------------------------------------------------
    print("\n[3] 나이브 베이즈 변형 비교")
    print("-" * 50)

    models = {
        'MultinomialNB': MultinomialNB(alpha=0.1),
        'BernoulliNB': BernoulliNB(alpha=0.1),
        'ComplementNB': ComplementNB(alpha=0.1),
        'MNB+Boolean': MultinomialNB(alpha=0.1),  # Metsis (2006) MNBB
    }

    model_results = {}
    for name, model in models.items():
        if name == 'MNB+Boolean':
            # 이진화된 특성 사용 (Metsis 2006 최우수 변형)
            tfidf_bool = TfidfVectorizer(
                max_features=5000, stop_words='english',
                binary=True, ngram_range=(1, 2), min_df=2
            )
            X_train_bool = tfidf_bool.fit_transform(X_train_df['clean_text'])
            X_test_bool = tfidf_bool.transform(X_test_df['clean_text'])
            model.fit(X_train_bool, y_train)
            y_pred = model.predict(X_test_bool)
            y_proba = model.predict_proba(X_test_bool)
        else:
            model.fit(X_train_tfidf, y_train)
            y_pred = model.predict(X_test_tfidf)
            y_proba = model.predict_proba(X_test_tfidf)

        acc = accuracy_score(y_test, y_pred)
        model_results[name] = {
            'accuracy': acc,
            'y_pred': y_pred,
            'y_proba': y_proba
        }
        print(f"  {name:20s}: 정확도 {acc:.4f}")

    # --------------------------------------------------------
    # 5.4 특성 중요도 분석
    # --------------------------------------------------------
    print("\n[4] 특성 중요도 분석 (스팸/정상 판별 핵심 단어)")
    print("-" * 50)

    spam_words, ham_words, importance = analyze_feature_importance(mnb, tfidf, n_top=15)

    print("\n  스팸 지표 단어 (log P(w|spam) - log P(w|ham) 상위):")
    for word, score in spam_words:
        print(f"    {word:20s}: {score:+.4f}")

    print("\n  정상 지표 단어 (log P(w|spam) - log P(w|ham) 하위):")
    for word, score in ham_words:
        print(f"    {word:20s}: {score:+.4f}")

    # --------------------------------------------------------
    # 5.5 오분류 분석
    # --------------------------------------------------------
    print("\n[5] 오분류 분석")
    analyze_misclassifications(
        X_test_df.reset_index(drop=True),
        y_test.values, y_pred_mnb, y_proba_mnb
    )

    # --------------------------------------------------------
    # 5.6 시각화
    # --------------------------------------------------------
    print("\n[6] 시각화 생성 중...")

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # (a) 혼동 행렬
    ax = axes[0, 0]
    cm = confusion_matrix(y_test, y_pred_mnb)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax,
                xticklabels=['Ham', 'Spam'], yticklabels=['Ham', 'Spam'],
                annot_kws={'size': 16})
    ax.set_xlabel('예측 (Predicted)', fontsize=12)
    ax.set_ylabel('실제 (Actual)', fontsize=12)
    ax.set_title(f'(a) 혼동 행렬 (MultinomialNB)\n정확도: {acc_mnb:.4f}', fontsize=13)

    # (b) 스팸/정상 핵심 단어
    ax = axes[0, 1]
    top_n = 10
    all_words = spam_words[:top_n] + ham_words[:top_n]
    words = [w for w, _ in all_words]
    scores = [s for _, s in all_words]
    colors_bar = ['red' if s > 0 else 'steelblue' for s in scores]

    y_pos = range(len(words))
    ax.barh(y_pos, scores, color=colors_bar, alpha=0.7, height=0.7)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(words, fontsize=9)
    ax.axvline(x=0, color='black', linewidth=0.5)
    ax.set_xlabel('log P(w|spam) - log P(w|ham)', fontsize=10)
    ax.set_title('(b) 스팸/정상 판별 핵심 단어\n(빨강: 스팸 지표, 파랑: 정상 지표)',
                 fontsize=12)
    ax.grid(True, alpha=0.3, axis='x')

    # (c) 나이브 베이즈 변형 비교
    ax = axes[1, 0]
    model_names = list(model_results.keys())
    model_accs = [model_results[n]['accuracy'] for n in model_names]
    bar_colors = ['steelblue', 'coral', 'forestgreen', 'purple']

    bars = ax.bar(model_names, model_accs, color=bar_colors[:len(model_names)],
                  alpha=0.8, width=0.6)
    for bar, acc_val in zip(bars, model_accs):
        ax.text(bar.get_x() + bar.get_width() / 2., bar.get_height() + 0.005,
                f'{acc_val:.4f}', ha='center', va='bottom', fontsize=11,
                fontweight='bold')
    ax.set_ylabel('정확도', fontsize=12)
    ax.set_title('(c) 나이브 베이즈 변형 비교\n(Metsis 2006 / Rennie 2003)', fontsize=12)
    ax.set_ylim(0.7, 1.05)
    ax.grid(True, alpha=0.3, axis='y')
    ax.tick_params(axis='x', rotation=10)

    # (d) 스팸 확률 분포
    ax = axes[1, 1]
    spam_probs_ham = y_proba_mnb[y_test.values == 0, 1]  # 실제 정상 메일의 스팸 확률
    spam_probs_spam = y_proba_mnb[y_test.values == 1, 1]  # 실제 스팸 메일의 스팸 확률

    ax.hist(spam_probs_ham, bins=20, alpha=0.6, color='steelblue',
            label='실제 정상(Ham)', density=True)
    ax.hist(spam_probs_spam, bins=20, alpha=0.6, color='red',
            label='실제 스팸(Spam)', density=True)
    ax.axvline(x=0.5, color='black', linestyle='--', linewidth=1.5,
               label='결정 경계 (0.5)')
    ax.set_xlabel('P(Spam | email)', fontsize=12)
    ax.set_ylabel('밀도', fontsize=12)
    ax.set_title('(d) 스팸 확률 분포\n(정상 vs 스팸)', fontsize=12)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.suptitle('완전한 스팸 필터: TF-IDF + Naive Bayes',
                 fontsize=15, fontweight='bold', y=1.01)
    plt.tight_layout()
    plt.savefig('D:/26년1학기/기계학습/7장/구현소스/03_spam_filter.png',
                dpi=150, bbox_inches='tight')
    plt.show()

    print("  그래프 저장 완료: 03_spam_filter.png")

    # --------------------------------------------------------
    # 5.7 새로운 이메일 예측 데모
    # --------------------------------------------------------
    print("\n[7] 새로운 이메일 예측 데모")
    print("-" * 50)

    new_emails = [
        "Congratulations! You won a free trip to Hawaii! Click here to claim",
        "Hi, can we schedule a meeting for next Tuesday to discuss the project?",
        "URGENT: Your account will be suspended unless you verify immediately",
        "Thanks for the update. I will review the document and get back to you",
        "Free pills! Buy cheap medications online without prescription needed",
        "The team lunch is confirmed for Friday noon at the Italian restaurant",
    ]

    new_clean = [preprocess_text(e) for e in new_emails]
    new_tfidf = tfidf.transform(new_clean)
    new_pred = mnb.predict(new_tfidf)
    new_proba = mnb.predict_proba(new_tfidf)

    for email, pred, proba in zip(new_emails, new_pred, new_proba):
        label = "스팸" if pred == 1 else "정상"
        confidence = max(proba)
        print(f"\n  이메일: \"{email[:60]}...\"")
        print(f"  분류: {label} (확신도: {confidence:.4f})")
        print(f"  P(Ham)={proba[0]:.4f}, P(Spam)={proba[1]:.4f}")

    print("\n" + "=" * 70)
    print("실행 완료")
    print("=" * 70)


if __name__ == "__main__":
    main()
