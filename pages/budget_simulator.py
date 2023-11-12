import streamlit as st
import numpy as np
import pandas as pd
import unicodedata

result_text = '''예산과 단가를 입력한 후\n계산하기 버튼을 누르면,
예산에 딱 맞게 물건을\n살 수 있는 방법을 찾아줍니다.\n
물품 추가 버튼을 눌러\n물품을 추가할 수도 있고,
체크 박스의 체크 표시를 해제하면\n잠시 계산에서 제외할 수도 있습니다.
'''

# ＊스타일 구역＊ Streamlit 페이지에 CSS를 추가
# 모든 숫자 입력란의 텍스트를 오른쪽으로 정렬합니다.
# 폰트 및 크기 설정
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
        .stTextInput, .stButton > button, .stSelectbox, .stDateInput, .stTimeInput {
            font-family: 'JetBrains Mono', monospace !important;}
        /* 텍스트 영역의 클래스 이름을 기반으로 스타일 지정 */
        textarea[aria-label="Results"]{
        font-family: JetBrains Mono, monospace; /* 원하는 폰트로 변경 */
        font-size: 12px; /* 폰트 크기 설정 */
        }
        input[type="number"] {
            text-align: right;
            font-family: JetBrains Mono, sans-serif; /* 원하는 폰트로 변경 */
            font-size: 16px; /* 폰트 크기 설정 */}
        p, input[type="text"] {
            font-family: JetBrains Mono, sans-serif; /* 원하는 폰트로 변경 */
            font-size: 16px; /* 폰트 크기 설정 */}
    </style>
    """, unsafe_allow_html=True)

# ＊함수 구역＊
# 문자열의 출력 길이를 구하는 함수(텍스트박스, 콘솔 출력용)
def get_print_length(s):
    screen_length = 0
    for char in s:
        if unicodedata.east_asian_width(char) in ['F', 'W']:
            screen_length+=2
        else:
            screen_length+=1
    return screen_length

# (수정중)문자열을 출력 길이에 맞게 자르는 함수(텍스트박스, 콘솔 출력용)
def cut_string(s, max_length):
    cut_s = ''
    length = 0
    for char in s:
        char_length = get_print_length(char)
        if length + char_length > max_length:
            break
        cut_s += char
        length += char_length
    return cut_s

# 아이템 활성화/비활성화 업데이트 함수(스트림릿 위젯 제어용)
def update_item_availability(i, budget):
    item_price = st.session_state.get(f"item_price_{i}", 0)
    if budget > 0 and item_price > 0 and item_price <= budget:
        max_quantity = budget // item_price
        st.session_state[f"item_max_{i}"] = max_quantity
        st.session_state[f"item_max_max_value_{i}"] = max_quantity
        st.session_state[f"item_min_min_value_{i}"] = max_quantity
        st.session_state[f"item_disabled_{i}"] = False
    else:
        st.session_state[f"item_disabled_{i}"] = True

# 예산 변경 시 호출되는 함수
def on_budget_change():
    budget = st.session_state.get("budget", 0)
    for i in range(st.session_state.item_count):
        update_item_availability(i, budget)

# 단가 변경 시 호출되는 함수
def on_price_change():
    budget = st.session_state.get("budget", 0)
    # 모든 아이템에 대해 update_item_availability 함수를 호출합니다.
    for i in range(st.session_state.item_count):
        update_item_availability(i, budget)

# 아이템의 최소 구매량 입력 필드가 변경될 때 호출되는 함수
def on_min_change(index):
    minis_now = []
    for ii in range(st.session_state.item_count):
        minis_now.append(st.session_state.get(f'item_min_{ii}', 0))
    st.session_state.get(f'item_min_{index}', 0)
    new_min = st.session_state.get(f'item_min_{index}', 0)
    max_val = st.session_state.get(f"item_max_{index}", 0)
    #에러처리
    #최소구매개수 * 단가의 총합이 예산을 넘는 경우 0으로 초기화, 에러메시지
    dot_product = sum(a * b for a, b in zip(minis_now, item_prices))
    if dot_product > budget_input:#st.session_state.get('budget', 0):
        st.session_state[f'item_min_{index}'] = 0
    #위 조건을 통과한 것 중 최소구매개수가 최대구매값보다 크면, 최대구매값과 일치.
    elif new_min >max_val:
        st.session_state[f'item_min_{index}'] = max_val
    #아니면 패스
    
def on_max_change(index):
    new_max = st.session_state.get(f"item_max_{index}", 0)
    min_val = st.session_state.get(f'item_min_{index}', 0)
    price_val = st.session_state.get(f'item_price_{index}', 0)
    budget = st.session_state.get("budget")
    #에러처리
    #최댜구매개수 * 단가가 예산을 넘는 경우 가능한 최대값으로 지정, 에러메시지
    if (price_val * new_max) > budget :
        st.session_state[f'item_max_{index}'] = budget//price_val
    #위 조건을 통과한 것 중 최대구매개수가 최소구매값보다 작으면, 최소구매값과 일치.
    elif min_val > new_max:
        st.session_state[f'item_max_{index}'] = min_val
    #아니면 패스    
    
# 예산 계산 함수
def calculate_budget(budget, labels, prices, minis, maxis):
    try:
        text_out = f'사용해야 할 예산은 {budget:d}원입니다.\n'

        item_count = len(prices)  # 계산해야 할 물품의 종류가 몇 개인지 저장합니다.
        quantity = [0] * item_count  # 각 아이템을 몇 개 살 건지 저장한느 리스트입니다.
        balances = [0] * item_count  # 각 아이템을 개수만큼 사고 난 뒤 남은 예산의 상태를 기록할 리스트입니다.

        last_index = item_count - 1  # 마지막 인덱스 번호를 아이템 개수-1로 정합니다.
        last_node = item_count - 2  # 순차적으로 조작할 마지막 노드를 아이템 개수 -2로 정합니다.(제일 마지막 노드는 '남은 예산/단가'공식으로 해결)
        node = last_node  # 노드(물품 개수 리스트의 기록 위치) 넘버를 마지막 노드에 위치시킵니다.

        is_overrun = False  # 예산을 초과하는지 상태를 체크합니다.
        case_count = 0  # 얼마나 많은 케이스를 검토했는지 체크하는 변수(연산량 확인용)

        case_exact = []  # 잔액 없이 예산을 소진하는 케이스(조합)를 저장하는 리스트
        case_close = []  # 잔액이 남지만 최대한 예산을 소진하는 케이스(조합)를 저장하는 리스트
        
        # labels와 prices를 결합하여 prices 기준으로 내림차순 정렬
        combined = zip(prices, labels, minis, maxis)
        sorted_combined = sorted(combined, reverse=True)

        # 정렬된 데이터를 다시 분리
        prices, labels, minis, maxis = zip(*sorted_combined)

        # 내림차순 정렬된 아이템 데이터를 출력
        text_out += '_' * 18 + '정렬된 데이터'+ '_' * 18 + '\n'
        for n_prt in range(item_count):
            label = cut_string(labels[n_prt], 28)
            if get_print_length(label) < 28:
                label += ' '
            text_out += f"품목 #{n_prt + 1:02d} {label} {' ' * (28 - get_print_length(label))} $ {prices[n_prt]:7,d} ({minis[n_prt]}~{maxis[n_prt]})\n"
        text_out += '_' * 47 + '\n'

        # _____CORE_CALCULATE THE BUDGET
        while not (node == -1 and is_overrun == True):
            # Set the left money after buy first item to left[0] according to list qnty[0]
            balances[0] = budget - (quantity[0] * prices[0])
            # Set the left money after buy items to left[n] according to list qnty[n]
            for n in range(1, last_index):
                balances[n] = balances[n - 1] - (quantity[n] * prices[n])
            # With the left money, calculates How many items(Last one) can be bought.
            quantity[last_index] = int(balances[last_index - 1] / prices[last_index])
            balances[last_index] = balances[last_index - 1] - (quantity[last_index] * prices[last_index])

            #  CHECK ERROR(Over Purchasing)
            #  IF ERROR occurs reset current node's 'qnty'(quantity) to 0.
            # and node up to count up upper node item's 'qnty'(quantity).
            if any([i < 0 for i in balances]):
                is_overrun = True
                quantity[node] = 0
                node -= 1

            #  IF there is no ERROR, Set over to False.
            # and reset node to the end(index of just before the last item in the list)
            else:
                is_overrun = False
                node = last_node
                # SAVE THE RESULT
                # IF Balance is $0, then save it to the case_exact
                # IF Balance is over $0, save it to the case_close
                if (balances[last_index] == 0):
                    case_exact.append(list(quantity))
                elif (balances[last_index] > 0):
                    case_close.append(list(quantity))

            # PREPAIR NEXT CASE
            quantity[node] += 1
            case_count += 1

        # _____Print result of the program.
        if len(case_exact) == 0:
            # If there is no perfect case. set the close case list to show.
            text_out += f'\u00A0{budget:7,d}원의 예산에 맞게 구입할 방법이 없습니다.\n\n'
            text_out += '예산에 근접한 구입 계획은 아래와 같습니다.\n\n'
            list_show = case_close

        else:
            # If there are perfect cases. set the exact list to show.
            text_out += f'\u00A0{budget:7,d}원의 예산에 맞는 {len(case_exact)}개의 완벽한 방법을 찾았습니다.\n\n'
            list_show = case_exact

        # Print the title of List.
        list_header = []
        text_out += '\u00A0\u00A0'
        for n_title in range(0, item_count):
            list_header.append(f'#{n_title + 1:02d}')
            text_out += f'#{n_title + 1:02d}  '
        text_out += '\n'

        # List up cases.
        for n_caseshow in list_show:
            sum_show = 0
            for n_index, n_itemshow in enumerate(n_caseshow):
                sum_show += n_itemshow * prices[n_index]
                text_out += '\u00A0'*(3-len(str(n_itemshow))) + f'{n_itemshow}EA'
            text_out += '   $' + format(sum_show, '7,d') + '\n'
        text_out += f'이 프로그램은 {case_count + 1}개의 케이스를 계산했습니다.\n'

    except:
        text_out = '에러입니다.'
        list_header =[]
        list_show =[]

    # 결과를 리턴
    return text_out, list_header, list_show, prices

# 웹 앱 UI 구현
result_header, result_list, result_prices = [], [], []

st.title("👌알잘딱깔센 예산 0원 만들기")

col_label_budget, col_input_budget = st.columns([2.5,7.5])
with col_label_budget:
    st.subheader("사용할 예산")
with col_input_budget:
    # 예산 입력란
    budget_input = st.number_input("사용할 예산", min_value=0, key="budget", help="사용해야하는 예산을 입력하세요.",
                                on_change=on_budget_change, format="%d", label_visibility='collapsed')

# session_state를 확인하여 물품 개수를 관리합니다.
if 'item_count' not in st.session_state:
    st.session_state.item_count = 5

# 아이템 섹션 생성 반복문
item_names = []
item_prices = []
min_quantities = []
max_quantities = []
hcol1, hcol2, hcol3, hcol4, hcol5 = st.columns([3.5, 1.4, 1.4, 3, 0.7])
with hcol1: st.write("물품이름")
with hcol2: st.write("최소구매")
with hcol3: st.write("최대구매")
with hcol4: st.write("물품단가")
with hcol5: st.write("선택")

for i in range(st.session_state.item_count):
    col1, col2, col3, col4, col5 = st.columns([3.5, 1.4, 1.4, 3, 0.7])
    # 체크박스가 해제되어 있는지 체크해 입력 필드들을 비활성화를 결정합니다.
    is_disabled = not st.session_state.get(f'item_usable_{i}', True)
    with col1:
        item_name = st.text_input(f"물품{i+1} 이름 입력", label_visibility='collapsed',
                                  key=f"item_name_{i}", placeholder=f"물품{i+1} 이름 입력",
                                  disabled=is_disabled)
    with col2:
        item_min = st.number_input(f"최소 {i+1}",
                                   on_change=on_min_change(i),
                                   min_value=0,
                                   max_value=st.session_state.get(f'item_min_max_value_{i}',),
                                   key=f"item_min_{i}",
                                   disabled=is_disabled or st.session_state.get(f"item_disabled_{i}", True),  # 여기에 disabled 상태를 적용합니다.
                                   format="%d", label_visibility='collapsed')
    with col3:
        item_max = st.number_input(f"최대 {i+1}",
                                   on_change=on_max_change(i),
                                   min_value=st.session_state.get(f'item_max_min_value_{i}', 0),
                                   key=f"item_max_{i}",
                                   disabled=is_disabled or st.session_state.get(f"item_disabled_{i}", True),  # 여기에 disabled 상태를 적용합니다.
                                   format="%d", label_visibility='collapsed')
    with col4:
        item_price = st.number_input(f"물품단가{i+1}",
                                     min_value=0,
                                     key=f"item_price_{i}",
                                     value=0,
                                     on_change=on_price_change,  # 여기에 이벤트 핸들러를 연결합니다.
                                     disabled=is_disabled, format="%d", label_visibility='collapsed')
    with col5:
        # Create the checkbox and use the session state value for the default
        item_usable = st.checkbox(f'물품{i+1}', label_visibility='collapsed', 
                                  key=f'item_usable_{i}',
                                  value=st.session_state.get(f'item_usable_{i}', True))
        st.write("")

    # If the checkbox is checked and the price is greater than 0, append to lists
    if item_usable and item_price > 0:
        item_names.append(item_name if item_name else '')
        item_prices.append(item_price)
        min_quantities.append(item_min)
        max_quantities.append(item_min)

col_left,col_label_fixed, col_right = st.columns(3)

# 물품추가 버튼 클릭 시 호출되는 함수
def add_item():
    st.session_state.item_count += 1

# 물품추가 버튼에 콜백 함수 연결
with col_left:
    if st.button("물품추가", on_click=add_item):
        pass

with col_label_fixed:
    st.write(sum(a * b for a, b in zip(min_quantities, item_prices)))

quantity = []



# 계산 버튼 클릭 이벤트 핸들러
with col_right:
    if st.button("계산하기"):
        if budget_input == "" or budget_input <= 0: result_text = '예산을 정확히 입력하세요.'
        elif len(item_prices) == 0: result_text = '단가를 입력하세요.'
        elif min(item_prices) <= 0: result_text = '단가가 0보다 작거나 같습니다.'
        elif max(item_prices) > budget_input: result_text = '예산이 부족합니다.'
        else:
            # 계산 결과를 구합니다.
            result_text, result_header,result_list, result_prices = calculate_budget(budget_input, item_names, item_prices,min_quantities,max_quantities)
st.text_area("Results", result_text, height=300)


# 결과를 화면에 표시합니다.
df = pd.DataFrame(result_list, columns=result_header)

# 새로운 열 '금액'을 계산하고 데이터프레임에 추가하는 함수를 정의합니다.
def calculate_amount(df, prices):
    # 각 열에 대해 가격을 곱하고 합계를 구합니다.
    df['금액'] = df.mul(prices).sum(axis=1)
    return df

# 함수를 사용하여 '금액' 열을 계산하고 데이터프레임에 추가합니다.
try:
    df = calculate_amount(df, result_prices)
except:
    pass

st.dataframe(df)