# -*- coding: utf-8 -*-
"""슬라이드 콘텐츠 Part 2 — 8.3 / 8.4 / 8.5 (전처리·모델링)"""

SLIDES_2 = []

# ============================================================
# 8.3 섹션 커버
# ============================================================
SLIDES_2.append({
    'kind': 'section_cover',
    'ko': {
        'num': '8.3',
        'section': 'SECTION 8.3',
        'title': '전처리: 범주형 데이터',
        'subtitle': '종속변수 변환 → object 변수 식별 → education / occupation / native-country 처리',
        'notes': '8.3절은 본 장에서 가장 비중이 큰 부분으로, 범주형 데이터를 어떻게 전처리하는지를 다룹니다. '
                 '핵심은 세 가지 변수(education, occupation, native-country)를 각각 다른 방법으로 처리하는 실습입니다. '
                 '이 부분만 확실히 이해하셔도 데이터 전처리의 핵심 패턴을 익힌 것입니다.'
    },
    'cn': {
        'num': '8.3',
        'section': 'SECTION 8.3',
        'title': '预处理:类别数据',
        'subtitle': '因变量转换 → 识别 object 变量 → education / occupation / native-country 处理',
        'notes': '8.3 节是本章篇幅最大的部分,讲解如何预处理类别数据。'
                 '核心是用三种不同方法分别处理三个变量:education、occupation、native-country。'
                 '掌握这一节就掌握了数据预处理的核心范式。'
    }
})

SLIDES_2.append({
    'kind': 'code',
    'ko': {
        'header': '8.3 종속변수 변환 + object형 변수 식별',
        'subtitle': 'class : <=50K → 0, >50K → 1   ·   obj_list 추출',
        'code': [
            '# (1) 종속변수 class 를 0/1 로 변환 — 차후 해석 일관성',
            "data['class'] = data['class'].map({'<=50K': 0, '>50K': 1})",
            '',
            '# (2) 변수별 자료형 확인 (for 루프)',
            'for i in data.columns:',
            '    print(i, data[i].dtype)',
            '',
            '# (3) object형 변수 이름만 별도 리스트로 모으기',
            'obj_list = []',
            'for i in data.columns:',
            "    if data[i].dtype == 'object':",
            '        obj_list.append(i)',
            '',
            '# 결과: 8개의 object형 독립변수',
            "# ['workclass', 'education', 'marital-status', 'occupation',",
            "#  'relationship', 'race', 'sex', 'native-country']",
            '',
            '# (4) 각 object 변수의 고윳값 개수 확인',
            'for i in obj_list:',
            '    print(i, data[i].nunique())',
            '#   workclass 8        education 16        marital-status 7',
            '#   occupation 14      relationship 6      race 5',
            '#   sex 2              native-country 41',
        ],
        'notes': '먼저 종속변수 class를 0과 1로 변환합니다. <=50K는 0, >50K는 1로 매핑합니다. '
                 '원본 데이터의 class 값에는 사실 앞에 공백이 하나 들어있지만, 8.2절에서 skipinitialspace=True로 이미 제거했기 때문에 그대로 비교할 수 있습니다. '
                 '다음으로 모든 변수의 자료형을 for 루프로 확인합니다. 변수가 13개 정도면 눈으로도 구분할 수 있지만, 100개 이상이면 자동화가 필수입니다. '
                 '그래서 if 조건을 추가해 object형 변수만 obj_list에 모읍니다. 결과적으로 8개의 object형 독립변수가 나옵니다. '
                 '마지막으로 각 변수의 고윳값 개수를 nunique 함수로 확인합니다. '
                 'workclass는 8가지, education은 16가지, native-country는 무려 41가지나 됩니다. '
                 '값의 종류가 10개 미만이면 그대로 더미 변수로 가도 큰 부담이 없지만, 10개 이상인 education, occupation, native-country는 별도의 처리 전략을 세워야 합니다. '
                 '이 세 변수가 다음 슬라이드들의 주제입니다.'
    },
    'cn': {
        'header': '8.3 因变量转换 + 识别 object 型变量',
        'subtitle': 'class:<=50K → 0, >50K → 1   ·   提取 obj_list',
        'code': [
            '# (1) 把因变量 class 转为 0/1,便于后续解释',
            "data['class'] = data['class'].map({'<=50K': 0, '>50K': 1})",
            '',
            '# (2) 用 for 循环检查每个变量的类型',
            'for i in data.columns:',
            '    print(i, data[i].dtype)',
            '',
            '# (3) 把 object 型变量名收集到列表',
            'obj_list = []',
            'for i in data.columns:',
            "    if data[i].dtype == 'object':",
            '        obj_list.append(i)',
            '',
            '# 结果:8 个 object 型自变量',
            "# ['workclass', 'education', 'marital-status', 'occupation',",
            "#  'relationship', 'race', 'sex', 'native-country']",
            '',
            '# (4) 检查每个 object 变量的唯一值个数',
            'for i in obj_list:',
            '    print(i, data[i].nunique())',
            '#   workclass 8        education 16        marital-status 7',
            '#   occupation 14      relationship 6      race 5',
            '#   sex 2              native-country 41',
        ],
        'notes': '首先把因变量 class 转为 0/1:<=50K → 0,>50K → 1。'
                 '原数据 class 值前实际有一个空格,但 8.2 节已用 skipinitialspace=True 去除,所以可直接比较。'
                 '其次用 for 循环检查所有变量的类型。变量约 13 个时肉眼就能区分,但若超过 100 个,自动化是必须的。'
                 '因此再加 if 条件,只把 object 型收集到 obj_list,得到 8 个变量。'
                 '最后用 nunique 函数查看每个变量的唯一值数量:'
                 'workclass 8 种、education 16 种、native-country 多达 41 种。'
                 '若取值不足 10 种,直接做独热不会有太大负担;'
                 '但 ≥ 10 种的 education、occupation、native-country 需要单独制定策略——这正是后面三张幻灯片的主题。'
    }
})

SLIDES_2.append({
    'kind': 'two_card',
    'ko': {
        'header': '8.3.3 education 변수 처리 — 서열화 활용',
        'subtitle': '이미 동일 정보의 서열형 변수 education-num이 존재 → drop',
        'left_title': '값의 분포 확인',
        'left_items': [
            "data['education'].value_counts()",
            '',
            'HS-grad         15784   (고졸)',
            'Some-college    10878   (대학중퇴/재학)',
            'Bachelors        8025   (학사)',
            'Masters          2657   (석사)',
            'Assoc-voc        2061',
            '11th             1812',
            '… (전 16개 카테고리)',
            'Doctorate         594   (박사)',
            'Preschool          83   (유치원)',
        ],
        'right_title': '핵심 통찰: 이미 서열화 되어 있다',
        'right_items': [
            '서열형 범주: 학력은 자연스러운 순서가 있음',
            '   Preschool < 1st-4th < … < Bachelors < … < Doctorate',
            '데이터에 education-num 변수가 이미 존재!',
            '   1=Preschool, 2=1st-4th, …, 16=Doctorate',
            '확인 코드:',
            "for i in np.sort(data['education-num'].unique()):",
            "    print(i, data[data['education-num']==i]['education'].unique())",
            '→ 완벽히 1대1 매핑됨 (중복 정보)',
            "data.drop('education', axis=1, inplace=True)",
        ],
        'notes': 'education 변수는 16개의 카테고리를 가집니다. 미국 교육 시스템이라 완전히 이해하기는 어렵지만, 초중고에 해당하는 1~12학년과 Bachelors, Masters 같은 학위가 섞여 있습니다. '
                 '여기서 중요한 점은 학력이 서열형 데이터라는 것입니다. 즉 "유치원 < 초등학교 < … < 학사 < 석사 < 박사" 같은 자연스러운 순서가 있습니다. '
                 '서열형 데이터는 단순히 숫자로 바꾸어도 모델에 의미를 잘 전달할 수 있습니다. '
                 '그런데 우연찮게도 이 데이터에는 education-num이라는 변수가 이미 준비되어 있습니다. '
                 '확인 코드로 매핑을 확인해 보면 1=Preschool, 2=1st-4th, …, 16=Doctorate로 완벽히 1대1 매핑됩니다. '
                 '같은 정보가 두 변수로 중복되어 있으므로 education 변수는 drop 함수로 제거합니다. '
                 '이것이 첫 번째 처리 패턴입니다 — 이미 서열화된 다른 변수가 있으면 그것을 활용하고 원본은 제거하는 방식.'
    },
    'cn': {
        'header': '8.3.3 处理 education 变量 — 利用序数化',
        'subtitle': '已存在等价的序数变量 education-num → 直接 drop',
        'left_title': '查看取值分布',
        'left_items': [
            "data['education'].value_counts()",
            '',
            'HS-grad         15784   (高中毕业)',
            'Some-college    10878   (大学肄业/在读)',
            'Bachelors        8025   (学士)',
            'Masters          2657   (硕士)',
            'Assoc-voc        2061',
            '11th             1812',
            '… (共 16 个类别)',
            'Doctorate         594   (博士)',
            'Preschool          83   (幼儿园)',
        ],
        'right_title': '关键洞察:已经被序数化',
        'right_items': [
            '序数型类别:学历有天然顺序',
            '   Preschool < 1st-4th < … < Bachelors < … < Doctorate',
            '数据集中已存在 education-num 变量!',
            '   1=Preschool, 2=1st-4th, …, 16=Doctorate',
            '确认代码:',
            "for i in np.sort(data['education-num'].unique()):",
            "    print(i, data[data['education-num']==i]['education'].unique())",
            '→ 完美 1:1 映射 (信息重复)',
            "data.drop('education', axis=1, inplace=True)",
        ],
        'notes': 'education 变量有 16 类。美国教育体系难以完全理解,但其中混有相当于小学到高中的 1~12 年级和学士、硕士等学位。'
                 '关键点在于学历是序数型数据,有"幼儿园 < 小学 < … < 学士 < 硕士 < 博士"这样的自然顺序。'
                 '序数型数据即便简单转为数字也能清晰传达含义。'
                 '巧的是数据中已存在 education-num 这个变量。'
                 '通过验证代码可见:1=Preschool、2=1st-4th、…、16=Doctorate,完全 1:1 映射。'
                 '由于两个变量信息重复,可用 drop 函数移除 education。'
                 '这是第一种处理模式——若已有等价的序数变量,直接利用并删除原变量。'
    }
})

SLIDES_2.append({
    'kind': 'two_card',
    'ko': {
        'header': '8.3.4 occupation 변수 처리 — 그대로 더미 변수로',
        'subtitle': '14개 카테고리, 서열 없음 → 더미 변수가 가장 자연스러움',
        'left_title': '값의 분포',
        'left_items': [
            "data['occupation'].value_counts()",
            '',
            'Prof-specialty       6172',
            'Craft-repair         6112',
            'Exec-managerial      6086',
            'Adm-clerical         5611',
            'Sales                5504',
            'Other-service        4923',
            'Machine-op-inspct    3022',
            '… (총 14개)',
            'Armed-Forces           15',
        ],
        'right_title': '판단과 처리 방침',
        'right_items': [
            '특징: 비슷한 직업끼리 이미 묶여 있음',
            '   예) Farming-fishing 한 묶음',
            '서열성 없음: 어느 직업이 위/아래라고 할 수 없음',
            '카테고리 수 14개 → 더미 변수로 14개 추가',
            '→ 감당 가능한 수준',
            '',
            '✅ 별도 처리 없이 8.4절에서 더미 변수로 일괄 변환',
            '   pd.get_dummies(data, drop_first=True)',
        ],
        'notes': 'occupation 변수는 14개의 직업군을 가집니다. '
                 '먼저 value_counts로 분포를 보면, 비슷한 직업들이 이미 묶인 형태로 정리되어 있는 것을 알 수 있습니다. '
                 '예를 들어 Farming(농사)과 Fishing(어업)이 Farming-fishing이라는 하나의 카테고리로 묶여 있습니다. '
                 '그리고 직업 간에는 서열이 없습니다. Sales가 Craft-repair보다 위라거나 아래라고 할 수 없죠. '
                 '따라서 education처럼 서열화는 부적절하고, 더미 변수로 변환하는 것이 가장 자연스럽습니다. '
                 '14개 카테고리는 더미 변수로 만들어도 14개 정도의 변수가 추가될 뿐이므로 충분히 감당할 수 있는 수준입니다. '
                 '그래서 별도의 처리 없이 8.4절에서 pd.get_dummies로 일괄 변환합니다. '
                 '이것이 두 번째 처리 패턴입니다 — 카테고리 수가 적당하면 그냥 더미 변수로.'
    },
    'cn': {
        'header': '8.3.4 处理 occupation 变量 — 直接独热',
        'subtitle': '14 个类别且无序数关系 → 独热编码最自然',
        'left_title': '取值分布',
        'left_items': [
            "data['occupation'].value_counts()",
            '',
            'Prof-specialty       6172',
            'Craft-repair         6112',
            'Exec-managerial      6086',
            'Adm-clerical         5611',
            'Sales                5504',
            'Other-service        4923',
            'Machine-op-inspct    3022',
            '… (共 14 个)',
            'Armed-Forces           15',
        ],
        'right_title': '判断与处理策略',
        'right_items': [
            '特征:相似职业已被合并',
            '   如 Farming-fishing 合为一类',
            '无序数性:难以说哪个职业更高/更低',
            '类别数 14 → 独热后增加 14 个变量',
            '→ 可以接受',
            '',
            '✅ 不另作处理,8.4 节统一独热',
            '   pd.get_dummies(data, drop_first=True)',
        ],
        'notes': 'occupation 变量有 14 类。'
                 '先用 value_counts 查看分布,可见相似职业已被合并。'
                 '例如 Farming(农)与 Fishing(渔)被合为 Farming-fishing。'
                 '职业之间没有序数关系——不能说 Sales 高于或低于 Craft-repair。'
                 '因此不像 education 那样适合序数化,直接独热最自然。'
                 '14 类做独热只增加 14 个变量,负担不大。'
                 '所以无需单独处理,留待 8.4 节用 pd.get_dummies 统一处理。'
                 '这是第二种处理模式——类别数量适中时直接独热。'
    }
})

SLIDES_2.append({
    'kind': 'three_card',
    'ko': {
        'header': '8.3.5 native-country 변수 처리 — 평균값 치환',
        'subtitle': '41개 국가 + United-States 90% → 어떤 방법이 가장 좋은가?',
        'cards': [
            ('① 후보 1 : Others로 묶기',
             '• United-States가 약 90% → 나머지를 Others로\n• 데이터 간소화 ✓\n• 정보 손실 ✗\n• groupby class 평균 확인 결과,\n   미국(0.24) vs 다른 국가들이 \n   매우 다양 → 부적합'),
            ('② 후보 2 : 지역(대륙)별 묶기',
             '• North America / Asia / Europe …\n• 같은 지역끼리 class 평균이 비슷해야 함\n• 그러나 France 0.42 vs Portugal 0.18\n   Cuba 0.25 vs Dominican R. 0.05\n• 지역 내 편차가 크므로 → 부적합'),
            ('③ ✅ 후보 3 : groupby 평균값 치환 (채택)',
             '• country_group = data.groupby(\n        \'native-country\').mean()[\'class\']\n• 각 국가 → 그 국가의 class 평균값으로 치환\n• 트리 모델은 이런 변환에 강건함\n• ⚠ 답을 일부 밀어넣는 셈 → 오버피팅 주의'),
        ],
        'punch': '국가 41개를 평균값으로 치환 → 변수 1개로 압축 + 의미 보존 (단, 오버피팅 주의)',
        'notes': 'native-country는 41개 국가가 있고 United-States가 압도적으로 많은 90%를 차지합니다. '
                 '이 변수를 처리하는 데는 세 가지 방법을 검토해야 합니다. '
                 '첫 번째는 단순히 미국 외 모든 국가를 Others로 묶는 방법입니다. 데이터가 간소화되지만 정보 손실이 큽니다. '
                 'groupby로 국가별 class 평균을 보면 미국이 0.24인데 다른 국가들은 매우 다양합니다. '
                 '두 번째는 대륙별로 묶는 방법입니다. 같은 지역 국가끼리 class 평균이 비슷해야 의미가 있는데, 같은 유럽인 France는 0.42, Portugal은 0.18로 큰 차이를 보입니다. '
                 'Cuba 0.25와 Dominican Republic 0.05도 마찬가지로 큰 차이입니다. 지역 내 편차가 너무 커서 부적합합니다. '
                 '세 번째 방법은 각 국가를 그 국가의 class 평균값으로 치환하는 것입니다. '
                 '예를 들어 France는 0.42, United-States는 0.24로 바꿉니다. 이 방법이 채택됩니다. '
                 '단, 이 방법은 종속변수 정보를 독립변수에 일부 밀어넣는 셈이라 오버피팅 위험이 있다는 점은 8.7절에서 다시 다룹니다.'
    },
    'cn': {
        'header': '8.3.5 处理 native-country 变量 — 用均值替换',
        'subtitle': '41 个国家 + United-States 占 90% → 哪种方法最好?',
        'cards': [
            ('① 候选 1:合并为 Others',
             '• United-States 约 90%,其余合为 Others\n• 数据简化 ✓\n• 信息损失 ✗\n• 用 groupby 看 class 均值,\n   美国 (0.24) 与其他国家差异大 → 不合适'),
            ('② 候选 2:按地区(大洲)合并',
             '• North America / Asia / Europe …\n• 需要同区国家的 class 均值相近\n• 但 France 0.42 vs Portugal 0.18\n   Cuba 0.25 vs Dominican R. 0.05\n• 区内差异过大 → 不合适'),
            ('③ ✅ 候选 3:groupby 均值替换 (采用)',
             '• country_group = data.groupby(\n        \'native-country\').mean()[\'class\']\n• 把每个国家替换为其 class 均值\n• 树模型对此类转换较稳健\n• ⚠ 等于把答案塞进自变量 → 注意过拟合'),
        ],
        'punch': '把 41 个国家替换为均值 → 压缩为 1 个变量,保留信息 (但需警惕过拟合)',
        'notes': 'native-country 共 41 国,且 United-States 占据约 90% 的压倒性份额。'
                 '处理这一变量需要考量三种方法:'
                 '第一种是把美国以外都合为 Others——数据更简化但信息损失大;'
                 '通过 groupby 看 class 均值,美国为 0.24,而其他国家差异极大。'
                 '第二种是按大洲合并:同地区国家 class 均值需要相近才有意义,'
                 '但同为欧洲的 France 0.42 与 Portugal 0.18 差距巨大,'
                 'Cuba 0.25 与 Dominican Republic 0.05 同样差距悬殊,故区内差异过大,不合适。'
                 '第三种则是把每个国家替换为该国 class 的均值——例如 France 替为 0.42,United-States 替为 0.24。这种方法被采纳。'
                 '不过该方法相当于把因变量信息部分塞进自变量,有过拟合风险,这点会在 8.7 节再讨论。'
    }
})

SLIDES_2.append({
    'kind': 'code',
    'ko': {
        'header': '8.3.5 native-country 평균값 치환 — 코드',
        'subtitle': 'groupby → reset_index → merge 패턴',
        'code': [
            '# (1) 국가별 class 평균값 계산',
            "country_group = data.groupby('native-country').mean()['class']",
            '',
            '# (2) 인덱스를 컬럼으로 빼서 merge 가능하게 만들기',
            'country_group = country_group.reset_index()',
            '',
            '# (3) 원본 데이터와 left-join으로 합치기',
            "data = data.merge(country_group,",
            "                  on='native-country', how='left')",
            '',
            '# (4) 컬럼 이름 정리 — class_x, class_y 충돌 해결',
            "data.drop('native-country', axis=1, inplace=True)",
            'data = data.rename(columns={',
            "    'class_x': 'class',",
            "    'class_y': 'native-country'",
            '})',
            '',
            '# 결과:',
            '#   native-country 변수 = 해당 국가의 class 평균 (실수)',
            '#   예) France → 0.421053  /  United-States → 0.243977',
        ],
        'notes': '국가별 class 평균값을 구해 원본에 합치는 코드입니다. '
                 '먼저 groupby로 국가별 class 평균을 계산하고, reset_index로 인덱스를 컬럼으로 변환합니다. '
                 'reset_index를 사용하지 않으면 국가 이름이 인덱스에 들어가 있어 merge 시 키로 쓸 수 없습니다. '
                 '그다음 merge 함수로 native-country를 키로 left join 합니다. '
                 '여기서 한 가지 문제가 발생하는데, 양쪽 데이터프레임에 모두 class 컬럼이 있어서 자동으로 class_x와 class_y로 이름이 바뀝니다. '
                 '우리는 class_y(국가별 평균값)를 원래 native-country 자리에 넣고 싶으므로, 기존 native-country 컬럼은 drop하고 rename으로 컬럼 이름을 정리합니다. '
                 '결과적으로 native-country는 더 이상 문자열이 아니라 0~1 사이의 실수값(해당 국가의 class 평균)을 가지게 됩니다.'
    },
    'cn': {
        'header': '8.3.5 native-country 均值替换 — 代码',
        'subtitle': 'groupby → reset_index → merge 模式',
        'code': [
            '# (1) 计算每个国家的 class 均值',
            "country_group = data.groupby('native-country').mean()['class']",
            '',
            '# (2) 用 reset_index 把索引变为列,以便 merge',
            'country_group = country_group.reset_index()',
            '',
            '# (3) 用 left-join 与原数据合并',
            "data = data.merge(country_group,",
            "                  on='native-country', how='left')",
            '',
            '# (4) 整理列名 — 解决 class_x、class_y 冲突',
            "data.drop('native-country', axis=1, inplace=True)",
            'data = data.rename(columns={',
            "    'class_x': 'class',",
            "    'class_y': 'native-country'",
            '})',
            '',
            '# 结果:',
            '#   native-country 变量 = 该国 class 平均 (浮点数)',
            '#   如 France → 0.421053  /  United-States → 0.243977',
        ],
        'notes': '本段代码计算每个国家的 class 均值并合并回原数据。'
                 '先用 groupby 取每国均值,再用 reset_index 把索引变为列。'
                 '不调用 reset_index,国家名仍在索引上,无法作为 merge 的键。'
                 '随后用 merge 以 native-country 为键做 left join。'
                 '此处会出现一个问题:两边都有 class 列,自动改名为 class_x、class_y。'
                 '我们要把 class_y(各国均值)放回 native-country 位置,因此先 drop 原 native-country 列,'
                 '再用 rename 整理列名。'
                 '最终 native-country 不再是字符串,而是 0~1 之间的浮点数(该国的 class 均值)。'
    }
})

# ============================================================
# 8.4
# ============================================================
SLIDES_2.append({
    'kind': 'section_cover',
    'ko': {
        'num': '8.4',
        'section': 'SECTION 8.4',
        'title': '전처리: 결측치 처리 & 더미 변수 변환',
        'subtitle': 'fillna 3종 + pd.get_dummies(drop_first=True)',
        'notes': '8.4절은 전처리의 마지막 단계로, 결측치를 처리하고 남아있는 범주형 변수를 더미 변수로 변환합니다. '
                 '결측치 처리는 변수의 특성에 따라 세 가지 다른 방법을 사용합니다.'
    },
    'cn': {
        'num': '8.4',
        'section': 'SECTION 8.4',
        'title': '预处理:缺失值处理 & 独热编码',
        'subtitle': 'fillna 三种方法 + pd.get_dummies(drop_first=True)',
        'notes': '8.4 节是预处理的最后一步:处理缺失值并对剩余类别变量进行独热编码。'
                 '依据变量特性采用三种不同方法填补缺失值。'
    }
})

SLIDES_2.append({
    'kind': 'table',
    'ko': {
        'header': '8.4 결측치 처리 전략 — 변수별 맞춤 처리',
        'subtitle': 'data.isna().mean() 으로 결측 비율 확인 후 변수마다 다르게 처리',
        'headers': ['변수', '결측 비율', '처리 방법', '근거'],
        'rows': [
            ['native-country', '1.7%', '-99 로 채우기 (fillna)',
             '이미 평균값으로 변환됨, 트리 모델은 임의값에 강건'],
            ['workclass', '5.7%', '"Private" 으로 채우기',
             'Private이 약 70%로 압도적, 최빈값 대체'],
            ['occupation', '5.8%', '"Unknown" 텍스트로 채우기',
             '특정 값이 압도적이지 않음 → 별도 카테고리 신설'],
            ['(나머지 11개)', '0%', '처리 불필요', '결측치 없음'],
        ],
        'col_widths': [2.5, 1.5, 3.5, 4.7],
        'notes': '결측치 처리 전략을 정리한 표입니다. '
                 'data.isna().mean()으로 보면 세 변수에 결측이 있습니다. '
                 'native-country는 8.3절에서 이미 평균값으로 변환되어 숫자가 되었으므로 -99 같은 임의의 숫자로 채울 수 있습니다. '
                 '여기서 "왜 평균이나 중앙값이 아닌 -99인가?"라는 의문이 생길 수 있는데, 트리 기반 모델은 이런 임의값에 강건합니다. '
                 '단 선형 모델에서는 -99 같은 값이 데이터 왜곡을 불러일으킬 수 있으니 주의해야 합니다. '
                 'workclass는 Private이 약 70%로 압도적이라 최빈값인 Private으로 채웁니다. '
                 '70%가 좀 아쉽긴 하지만 연습 차원에서 사용합니다. '
                 'occupation은 어떤 특정 값이 압도적이지 않으므로 최빈값 대체가 적절치 않아 "Unknown"이라는 별도 카테고리를 신설합니다. '
                 '이렇게 변수의 특성에 따라 결측치 처리를 다르게 하는 것이 머신러닝 전처리의 핵심입니다.'
    },
    'cn': {
        'header': '8.4 缺失值处理策略 — 因变量制宜',
        'subtitle': '用 data.isna().mean() 查看比例后,按变量分别处理',
        'headers': ['变量', '缺失比例', '处理方法', '依据'],
        'rows': [
            ['native-country', '1.7%', '用 -99 填充 (fillna)',
             '已转为均值数字,树模型对任意值稳健'],
            ['workclass', '5.7%', '用 "Private" 填充',
             'Private 约 70% 占绝对多数,众数填充'],
            ['occupation', '5.8%', '用 "Unknown" 文本填充',
             '没有压倒性的取值 → 新增一个类别'],
            ['(其余 11 个)', '0%', '无需处理', '无缺失'],
        ],
        'col_widths': [2.5, 1.5, 3.5, 4.7],
        'notes': '本张幻灯片汇总缺失值处理策略。'
                 '用 data.isna().mean() 可见三个变量含缺失。'
                 'native-country 在 8.3 节已被替换为均值(数值),可用 -99 等任意数填充。'
                 '为何不用均值或中位数?——因为树模型对任意值都稳健;'
                 '不过线性模型中 -99 这类值会扭曲数据,需要注意。'
                 'workclass 中 Private 约占 70%,以众数填充。70% 略显不足,但出于练习目的可以接受。'
                 'occupation 没有压倒性取值,因此不适合众数填充,而是新建一个 "Unknown" 类别。'
                 '依据变量特性差异化处理缺失值,正是机器学习预处理的核心。'
    }
})

SLIDES_2.append({
    'kind': 'code',
    'ko': {
        'header': '8.4 결측치 fillna 코드 + 더미 변수 변환',
        'subtitle': '최종 전처리 — pd.get_dummies(drop_first=True) 1줄로 마무리',
        'code': [
            '# (1) 결측 비율 확인',
            'data.isna().mean()',
            '#   workclass         0.057307',
            '#   occupation        0.057512',
            '#   native-country    0.017546',
            '',
            '# (2) 변수별 결측치 채우기',
            "data['native-country'] = data['native-country'].fillna(-99)",
            "data['workclass'] = data['workclass'].fillna('Private')",
            "data['occupation'] = data['occupation'].fillna('Unknown')",
            '',
            '# (3) 모든 결측치 해결 후 — 더미 변수 변환 (1줄!)',
            'data = pd.get_dummies(data, drop_first=True)',
            '#   drop_first=True : 다중공선성 방지를 위해',
            '#                     첫 더미 컬럼 자동 제거',
            '#   (예) workclass_Federal-gov, workclass_Local-gov, …',
            '#         workclass_Private 은 제거됨 (= 모두 0이면 Private)',
        ],
        'notes': '결측치를 처리하는 fillna 코드와 더미 변수 변환 코드입니다. '
                 'fillna 함수는 결측치를 인자값으로 채워주는 함수로, 변수마다 다른 값을 사용합니다. '
                 'native-country는 -99, workclass는 "Private", occupation은 "Unknown"으로 채웁니다. '
                 '모든 결측치가 해결되면 마지막으로 pd.get_dummies로 모든 범주형 변수를 한 번에 더미 변수로 변환합니다. '
                 '여기서 drop_first=True 옵션이 중요한데, 이는 다중공선성 방지를 위해 첫 번째 더미 컬럼을 자동으로 제거하는 옵션입니다. '
                 '예를 들어 workclass에 Federal-gov, Local-gov, Private 등이 있으면 workclass_Private 컬럼은 제거되고, 나머지 모든 더미 컬럼이 0이면 자동으로 Private이라는 의미가 됩니다. '
                 '이 한 줄로 8개의 범주형 변수가 모두 적절한 수의 더미 변수로 변환되며, 전처리가 완료됩니다.'
    },
    'cn': {
        'header': '8.4 fillna 代码 + 独热编码',
        'subtitle': '最终预处理 — 用 pd.get_dummies(drop_first=True) 一行完成',
        'code': [
            '# (1) 查看缺失比例',
            'data.isna().mean()',
            '#   workclass         0.057307',
            '#   occupation        0.057512',
            '#   native-country    0.017546',
            '',
            '# (2) 按变量填充缺失',
            "data['native-country'] = data['native-country'].fillna(-99)",
            "data['workclass'] = data['workclass'].fillna('Private')",
            "data['occupation'] = data['occupation'].fillna('Unknown')",
            '',
            '# (3) 缺失全部处理后 — 独热变换 (一行搞定!)',
            'data = pd.get_dummies(data, drop_first=True)',
            '#   drop_first=True:为防止多重共线性,',
            '#                   自动去掉第一个独热列',
            '#   (例) workclass_Federal-gov, workclass_Local-gov, …',
            '#         workclass_Private 被剔除 (全为 0 即代表 Private)',
        ],
        'notes': '本段是处理缺失值的 fillna 代码与独热编码代码。'
                 'fillna 用给定值填补缺失,各变量使用不同的值:'
                 'native-country 用 -99,workclass 用 "Private",occupation 用 "Unknown"。'
                 '全部缺失处理完后,用 pd.get_dummies 一次性把所有类别变量独热。'
                 'drop_first=True 选项很关键,可避免多重共线性,自动删除第一个独热列。'
                 '例如 workclass 有 Federal-gov、Local-gov、Private 等,workclass_Private 会被删除,'
                 '其他独热列全为 0 时即代表 Private。'
                 '这一行让 8 个类别变量被转换为合适数量的独热变量,预处理完成。'
    }
})

# ============================================================
# 8.5
# ============================================================
SLIDES_2.append({
    'kind': 'section_cover',
    'ko': {
        'num': '8.5',
        'section': 'SECTION 8.5',
        'title': '모델링 및 평가하기',
        'subtitle': 'train_test_split → DecisionTreeClassifier → accuracy_score',
        'notes': '8.5절은 드디어 모델을 학습시키고 평가하는 단계입니다. '
                 'scikit-learn의 train_test_split, DecisionTreeClassifier, accuracy_score 세 함수만 사용합니다. '
                 '이전 장들에서 이미 익숙한 패턴이므로 코드 작성 자체는 어렵지 않습니다.'
    },
    'cn': {
        'num': '8.5',
        'section': 'SECTION 8.5',
        'title': '建模与评估',
        'subtitle': 'train_test_split → DecisionTreeClassifier → accuracy_score',
        'notes': '8.5 节终于进入训练与评估模型的环节。'
                 '只需使用 scikit-learn 的 train_test_split、DecisionTreeClassifier、accuracy_score 三个函数。'
                 '前几章已经熟悉这一模式,代码本身并不难。'
    }
})

SLIDES_2.append({
    'kind': 'code',
    'ko': {
        'header': '8.5 모델링 코드 — 4단계',
        'subtitle': '훈련셋·시험셋 분리 → 학습 → 예측 → 정확도 계산',
        'code': [
            '# (1) 훈련셋 / 시험셋 분리 (test_size=0.4 → 데이터가 크므로 40%)',
            'from sklearn.model_selection import train_test_split',
            '',
            'X_train, X_test, y_train, y_test = train_test_split(',
            "    data.drop('class', axis=1),    # 독립변수",
            "    data['class'],                  # 종속변수",
            '    test_size=0.4,                  # 시험셋 비율',
            '    random_state=100                # 재현성 보장',
            ')',
            '',
            '# (2) 결정 트리 분류 모델 객체 생성',
            'from sklearn.tree import DecisionTreeClassifier',
            'model = DecisionTreeClassifier()        # 매개변수 모두 기본값',
            '',
            '# (3) 학습 + 예측',
            'model.fit(X_train, y_train)             # 학습',
            'pred = model.predict(X_test)            # 예측',
            '',
            '# (4) 정확도 계산',
            'from sklearn.metrics import accuracy_score',
            'accuracy_score(y_test, pred)',
            '#   결과: 0.8134309259354047  (약 81%)',
        ],
        'notes': '4단계로 진행됩니다. '
                 '먼저 train_test_split으로 데이터를 훈련셋과 시험셋으로 나눕니다. 이번에는 데이터가 비교적 크기 때문에 test_size를 0.4로 설정해 40%를 시험셋으로 분리했습니다. '
                 'random_state=100은 결과 재현을 위한 시드값입니다. '
                 '두 번째 단계는 DecisionTreeClassifier 객체를 생성하는 것입니다. 회귀 문제라면 DecisionTreeRegressor를 쓰지만, 우리는 0과 1 분류이므로 Classifier를 사용합니다. '
                 '괄호 안에 아무것도 넣지 않으면 매개변수가 모두 기본값으로 설정됩니다. '
                 '세 번째는 fit과 predict로 학습하고 예측합니다. '
                 '마지막으로 accuracy_score로 정확도를 계산하면 약 81%의 결과가 나옵니다. '
                 '81%는 나쁘지 않지만, 8.7~8.8절에서 매개변수 튜닝으로 85%까지 올릴 수 있다는 것을 곧 보여드리겠습니다.'
    },
    'cn': {
        'header': '8.5 建模代码 — 四步',
        'subtitle': '训练/测试集划分 → 训练 → 预测 → 计算准确率',
        'code': [
            '# (1) 划分训练/测试集 (数据较大,test_size=0.4)',
            'from sklearn.model_selection import train_test_split',
            '',
            'X_train, X_test, y_train, y_test = train_test_split(',
            "    data.drop('class', axis=1),    # 自变量",
            "    data['class'],                  # 因变量",
            '    test_size=0.4,                  # 测试集比例',
            '    random_state=100                # 保证可复现',
            ')',
            '',
            '# (2) 创建决策树分类模型对象',
            'from sklearn.tree import DecisionTreeClassifier',
            'model = DecisionTreeClassifier()        # 全部使用默认参数',
            '',
            '# (3) 训练 + 预测',
            'model.fit(X_train, y_train)             # 训练',
            'pred = model.predict(X_test)            # 预测',
            '',
            '# (4) 计算准确率',
            'from sklearn.metrics import accuracy_score',
            'accuracy_score(y_test, pred)',
            '#   结果:0.8134309259354047  (约 81%)',
        ],
        'notes': '共四步。'
                 '先用 train_test_split 划分训练集与测试集——数据较大,设 test_size=0.4 把 40% 划为测试集;'
                 'random_state=100 用于结果复现。'
                 '第二步是创建 DecisionTreeClassifier 对象。回归任务用 DecisionTreeRegressor,'
                 '本任务是 0/1 分类,所以选 Classifier。括号留空表示参数全用默认。'
                 '第三步用 fit 和 predict 训练并预测。'
                 '最后用 accuracy_score 计算准确率,得到约 81%。'
                 '81% 不算差,稍后会在 8.7~8.8 节通过超参数调优把它提升到 85%。'
    }
})
