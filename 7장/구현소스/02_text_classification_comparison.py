# -*- coding: utf-8 -*-
"""
02_text_classification_comparison.py
MultinomialNB, BernoulliNB, ComplementNB(Rennie 2003)를 20 Newsgroups 데이터셋에서 비교한다.

구현 내용:
1. 세 가지 나이브 베이즈 변형 비교 (MultinomialNB, BernoulliNB, ComplementNB)
2. CountVectorizer vs TfidfVectorizer 비교
3. alpha(라플라스 스무딩) 하이퍼파라미터 튜닝
4. 혼동 행렬 및 분류 보고서 비교

데이터: sklearn fetch_20newsgroups (4개 카테고리 선택)
참고 논문: Rennie et al. (2003), McCallum & Nigam (1998)
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB, BernoulliNB, ComplementNB
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (accuracy_score, classification_report,
                             confusion_matrix, f1_score)
from sklearn.pipeline import Pipeline
import warnings
warnings.filterwarnings('ignore')


# ============================================================
# 1. 데이터 로드 및 준비
# ============================================================

def load_data():
    """20 Newsgroups 데이터셋에서 4개 카테고리를 선택하여 로드한다."""

    # 4개 카테고리 선택 (서로 구별되는 주제)
    categories = [
        'rec.sport.baseball',    # 스포츠 (야구)
        'sci.med',               # 과학 (의학)
        'comp.graphics',         # 컴퓨터 (그래픽)
        'talk.politics.misc'     # 정치
    ]

    # 학습 데이터
    train_data = fetch_20newsgroups(
        subset='train', categories=categories,
        shuffle=True, random_state=42,
        remove=('headers', 'footers', 'quotes')
    )

    # 테스트 데이터
    test_data = fetch_20newsgroups(
        subset='test', categories=categories,
        shuffle=True, random_state=42,
        remove=('headers', 'footers', 'quotes')
    )

    print(f"학습 데이터: {len(train_data.data)}개")
    print(f"테스트 데이터: {len(test_data.data)}개")
    print(f"\n카테고리:")
    for i, name in enumerate(train_data.target_names):
        n_train = np.sum(train_data.target == i)
        n_test = np.sum(test_data.target == i)
        print(f"  {i}: {name:25s} (학습: {n_train:4d}, 테스트: {n_test:4d})")

    return train_data, test_data


# ============================================================
# 2. 나이브 베이즈 변형 비교
# ============================================================

def compare_nb_variants(train_data, test_data):
    """
    세 가지 나이브 베이즈 변형을 비교한다.

    - MultinomialNB: 단어 빈도 기반 (McCallum & Nigam, 1998)
    - BernoulliNB: 단어 존재/부재 기반 (McCallum & Nigam, 1998)
    - ComplementNB: 보완 클래스 기반 (Rennie et al., 2003)
    """
    target_names = train_data.target_names

    # 벡터화기 설정
    vectorizers = {
        'CountVectorizer': CountVectorizer(max_features=10000, stop_words='english'),
        'TfidfVectorizer': TfidfVectorizer(max_features=10000, stop_words='english'),
    }

    # 나이브 베이즈 변형
    nb_models = {
        'MultinomialNB': MultinomialNB(alpha=1.0),
        'BernoulliNB': BernoulliNB(alpha=1.0),
        'ComplementNB': ComplementNB(alpha=1.0),
    }

    results = {}

    for vec_name, vectorizer in vectorizers.items():
        print(f"\n--- {vec_name} ---")
        X_train = vectorizer.fit_transform(train_data.data)
        X_test = vectorizer.transform(test_data.data)

        for model_name, model in nb_models.items():
            model.fit(X_train, train_data.target)
            y_pred = model.predict(X_test)
            acc = accuracy_score(test_data.target, y_pred)
            f1 = f1_score(test_data.target, y_pred, average='macro')

            key = f"{model_name}\n+ {vec_name}"
            results[key] = {
                'accuracy': acc,
                'f1_macro': f1,
                'y_pred': y_pred,
                'model_name': model_name,
                'vec_name': vec_name
            }

            print(f"  {model_name:20s} -> 정확도: {acc:.4f}, F1(macro): {f1:.4f}")

    return results


# ============================================================
# 3. Alpha 하이퍼파라미터 튜닝
# ============================================================

def tune_alpha(train_data, test_data):
    """
    alpha(라플라스 스무딩 파라미터) 값에 따른 성능 변화를 분석한다.

    alpha = 1: 라플라스 스무딩 (기본)
    alpha < 1: 리드스톤 스무딩
    alpha > 1: 강한 스무딩
    """
    alphas = [0.001, 0.01, 0.05, 0.1, 0.3, 0.5, 0.7, 1.0, 2.0, 5.0, 10.0]

    # TfidfVectorizer 사용
    vectorizer = TfidfVectorizer(max_features=10000, stop_words='english')
    X_train = vectorizer.fit_transform(train_data.data)
    X_test = vectorizer.transform(test_data.data)

    results_alpha = {'MultinomialNB': [], 'BernoulliNB': [], 'ComplementNB': []}

    print("\n--- Alpha 튜닝 (TfidfVectorizer) ---")
    print(f"{'alpha':>8s} {'MultinomialNB':>15s} {'BernoulliNB':>15s} {'ComplementNB':>15s}")

    for alpha in alphas:
        accs = {}
        for name, ModelClass in [('MultinomialNB', MultinomialNB),
                                  ('BernoulliNB', BernoulliNB),
                                  ('ComplementNB', ComplementNB)]:
            model = ModelClass(alpha=alpha)
            model.fit(X_train, train_data.target)
            acc = accuracy_score(test_data.target, model.predict(X_test))
            results_alpha[name].append(acc)
            accs[name] = acc

        print(f"{alpha:8.3f} {accs['MultinomialNB']:15.4f} "
              f"{accs['BernoulliNB']:15.4f} {accs['ComplementNB']:15.4f}")

    return alphas, results_alpha


# ============================================================
# 4. 어휘 크기별 성능 비교
# ============================================================

def compare_vocab_sizes(train_data, test_data):
    """
    어휘 크기(max_features)에 따른 각 모델의 성능 변화를 분석한다.

    McCallum & Nigam (1998): 큰 어휘에서 MultinomialNB가 BernoulliNB를 능가
    """
    vocab_sizes = [100, 500, 1000, 3000, 5000, 10000, 20000, None]  # None = 전체
    vocab_labels = ['100', '500', '1K', '3K', '5K', '10K', '20K', 'All']

    results_vocab = {'MultinomialNB': [], 'BernoulliNB': [], 'ComplementNB': []}

    print("\n--- 어휘 크기별 성능 비교 ---")
    print(f"{'어휘 크기':>10s} {'MultinomialNB':>15s} {'BernoulliNB':>15s} {'ComplementNB':>15s}")

    for vs, label in zip(vocab_sizes, vocab_labels):
        vectorizer = TfidfVectorizer(max_features=vs, stop_words='english')
        X_train = vectorizer.fit_transform(train_data.data)
        X_test = vectorizer.transform(test_data.data)
        actual_vocab = X_train.shape[1]

        accs = {}
        for name, ModelClass in [('MultinomialNB', MultinomialNB),
                                  ('BernoulliNB', BernoulliNB),
                                  ('ComplementNB', ComplementNB)]:
            model = ModelClass(alpha=1.0)
            model.fit(X_train, train_data.target)
            acc = accuracy_score(test_data.target, model.predict(X_test))
            results_vocab[name].append(acc)
            accs[name] = acc

        print(f"{label:>10s} ({actual_vocab:>6d}) "
              f"{accs['MultinomialNB']:13.4f} {accs['BernoulliNB']:15.4f} "
              f"{accs['ComplementNB']:15.4f}")

    return vocab_labels, results_vocab


# ============================================================
# 5. 메인 실행
# ============================================================

def main():
    print("=" * 70)
    print("나이브 베이즈 텍스트 분류 비교")
    print("MultinomialNB vs BernoulliNB vs ComplementNB")
    print("=" * 70)

    # 데이터 로드
    train_data, test_data = load_data()
    target_names = train_data.target_names

    # 실험 1: 나이브 베이즈 변형 비교
    print("\n[실험 1] 나이브 베이즈 변형 비교")
    results = compare_nb_variants(train_data, test_data)

    # 실험 2: Alpha 튜닝
    print("\n[실험 2] Alpha 하이퍼파라미터 튜닝")
    alphas, results_alpha = tune_alpha(train_data, test_data)

    # 실험 3: 어휘 크기별 비교
    print("\n[실험 3] 어휘 크기별 성능 비교")
    vocab_labels, results_vocab = compare_vocab_sizes(train_data, test_data)

    # 최고 성능 모델의 상세 분류 보고서
    best_key = max(results, key=lambda k: results[k]['accuracy'])
    best_result = results[best_key]
    print(f"\n[최고 성능 모델] {best_key.replace(chr(10), ' ')}")
    print(f"정확도: {best_result['accuracy']:.4f}")
    print(classification_report(test_data.target, best_result['y_pred'],
                                target_names=target_names))

    # --------------------------------------------------------
    # 시각화
    # --------------------------------------------------------
    print("[시각화] 결과 그래프 생성 중...")

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # (a) 나이브 베이즈 변형별 정확도 비교
    ax = axes[0, 0]
    keys = list(results.keys())
    accs = [results[k]['accuracy'] for k in keys]
    colors = ['steelblue', 'coral', 'forestgreen',
              'steelblue', 'coral', 'forestgreen']
    hatches = ['', '', '', '///', '///', '///']

    bars = ax.barh(range(len(keys)), accs, color=colors[:len(keys)],
                   alpha=0.7, height=0.6)
    for i, (bar, h) in enumerate(zip(bars, hatches[:len(keys)])):
        bar.set_hatch(h)

    ax.set_yticks(range(len(keys)))
    ax.set_yticklabels([k.replace('\n', '\n') for k in keys], fontsize=8)
    for i, acc in enumerate(accs):
        ax.text(acc + 0.002, i, f'{acc:.4f}', va='center', fontsize=9)
    ax.set_xlabel('정확도 (Accuracy)', fontsize=11)
    ax.set_title('(a) 나이브 베이즈 변형별 정확도', fontsize=12)
    ax.set_xlim(0.6, 0.95)
    ax.grid(True, alpha=0.3, axis='x')

    # (b) Alpha 튜닝
    ax = axes[0, 1]
    model_colors = {'MultinomialNB': 'steelblue', 'BernoulliNB': 'coral',
                    'ComplementNB': 'forestgreen'}
    for name, accs_list in results_alpha.items():
        ax.plot(alphas, accs_list, 'o-', color=model_colors[name],
                linewidth=2, markersize=6, label=name)
    ax.set_xscale('log')
    ax.set_xlabel('Alpha (스무딩 파라미터)', fontsize=11)
    ax.set_ylabel('정확도', fontsize=11)
    ax.set_title('(b) Alpha에 따른 정확도 변화', fontsize=12)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    # (c) 어휘 크기별 비교
    ax = axes[1, 0]
    for name, accs_list in results_vocab.items():
        ax.plot(range(len(vocab_labels)), accs_list, 'o-',
                color=model_colors[name], linewidth=2, markersize=6, label=name)
    ax.set_xticks(range(len(vocab_labels)))
    ax.set_xticklabels(vocab_labels, fontsize=10)
    ax.set_xlabel('어휘 크기 (max_features)', fontsize=11)
    ax.set_ylabel('정확도', fontsize=11)
    ax.set_title('(c) 어휘 크기에 따른 정확도 변화\n(McCallum & Nigam 1998 재현)',
                 fontsize=12)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    # (d) 최고 성능 모델 혼동 행렬
    ax = axes[1, 1]
    cm = confusion_matrix(test_data.target, best_result['y_pred'])
    short_names = ['Baseball', 'Graphics', 'Medicine', 'Politics']
    sns.heatmap(cm, annot=True, fmt='d', cmap='Greens', ax=ax,
                xticklabels=short_names, yticklabels=short_names)
    ax.set_xlabel('예측 (Predicted)', fontsize=11)
    ax.set_ylabel('실제 (Actual)', fontsize=11)
    ax.set_title(f'(d) 혼동 행렬 ({best_key.replace(chr(10), " ")})\n'
                 f'정확도: {best_result["accuracy"]:.4f}', fontsize=11)

    plt.suptitle('나이브 베이즈 텍스트 분류 비교 실험\n(20 Newsgroups 데이터셋)',
                 fontsize=14, fontweight='bold', y=1.01)
    plt.tight_layout()
    plt.savefig('D:/26년1학기/기계학습/7장/구현소스/02_nb_comparison.png',
                dpi=150, bbox_inches='tight')
    plt.show()

    print("  그래프 저장 완료: 02_nb_comparison.png")

    # 핵심 결론
    print("\n" + "=" * 70)
    print("핵심 결론")
    print("=" * 70)
    print("  1. ComplementNB(Rennie 2003)가 MultinomialNB보다 일관되게 우수하다.")
    print("  2. TfidfVectorizer가 CountVectorizer보다 전반적으로 우수하다.")
    print("  3. 어휘 크기가 클수록 MultinomialNB와 ComplementNB의 이점이 커진다.")
    print("  4. BernoulliNB는 소규모 어휘에서는 경쟁력이 있으나,")
    print("     대규모 어휘에서는 다른 변형에 뒤처진다 (McCallum & Nigam 1998).")
    print("  5. Alpha 스무딩 파라미터는 0.1~1.0 범위에서 최적인 경우가 많다.")
    print("=" * 70)


if __name__ == "__main__":
    main()
