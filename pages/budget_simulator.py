import streamlit as st
import numpy as np
import pandas as pd
import unicodedata

result_text = '''예산과 단가를 입력한 후\n계산하기 버튼을 누르면,
예산에 딱 맞게 물건을\n살 수 있는 방법을 찾아줍니다.\n
물품 이름은 안 쓰셔도 작동합니다.
단가가 0인 품목은 자동으로 제외합니다.\n
물품 추가 버튼을 눌러\n물품을 추가할 수도 있고,
체크 박스의 체크 표시를 해제하면\n잠시 계산에서 제외할 수도 있습니다.
***최대구매 제한은 아직 불가능합니다.(알고리즘 추가 중)***
'''
# ＊스타일 구역＊ Streamlit 페이지에 CSS를 추가
# 모든 숫자 입력란의 텍스트를 오른쪽으로 정렬합니다.
# 폰트 및 크기 설정
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Nanum+Gothic+Coding&display=swap');
        .stTextInput, .stButton > button, .stSelectbox, .stDateInput, .stTimeInput {
            font-family: 'Nanum Gothic Coding', monospace !important;}
        /* 텍스트 영역의 클래스 이름을 기반으로 스타일 지정 */
        input[type="number"] {text-align: right;}
        h1{text-align: center;}
        input[type="number"], textarea[aria-label="Results"], p, input[type="text"] {
            font-family: Nanum Gothic Coding, monospace; /* 원하는 폰트로 변경 */
            font-size: 16px; /* 폰트 크기 설정 */}
        textarea[aria-label="Results"]{color: #FFC83D;}
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

# 문자열을 출력 길이에 맞게 자르는 함수(텍스트박스, 콘솔 출력용)
def cut_string(org_s, max_length,pad_LR="R"):
    cut_s, length = '', 0
    for char in org_s:
        char_length = get_print_length(char)
        if length + char_length > max_length:
            break
        cut_s += char
        length += char_length
    diff = max_length-length
    if diff>0:
        if pad_LR == "L": return diff * " " + cut_s
        if pad_LR == "R": return cut_s + diff * " "
    else: return cut_s

# 아이템 활성화/비활성화 업데이트 함수(스트림릿 위젯 제어용)
def update_item_availability(i, budget):
    item_price = st.session_state.get(f"item_price_{i}", 0)
    if budget > 0 and item_price > 0 and item_price <= budget:
        max_quantity = budget // item_price
        st.session_state[f"item_max_{i}"] = max_quantity
        st.session_state[f"item_max_max_value_{i}"] = max_quantity
        st.session_state[f"item_min_min_value_{i}"] = max_quantity
        st.session_state[f"item_disabled_{i}"] = False
    else: st.session_state[f"item_disabled_{i}"] = True

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
def on_min_change(index,min_quantities,item_prices):
    # 현재 아이템의 최소, 최대 구매량 및 단가 가져오기
    current_min = st.session_state.get(f'item_min_{index}', 0)
    current_max = st.session_state.get(f'item_max_{index}', 0)
    current_price = st.session_state.get(f'item_price_{index}', 0)
    budget_input = st.session_state.get("budget")

    # 모든 아이템에 대해 최소 구매량과 단가를 곱한 총액 계산
    total_min_cost = sum(a * b for a, b in zip(min_quantities, item_prices))

    # 예산 초과 시 조정
    if total_min_cost > budget_input and current_price!=0:
        # 예산 초과분 계산
        over_budget = total_min_cost - budget_input

        # 현재 아이템의 구매량을 줄여서 예산을 맞추기
        reduce_by = min(current_min, (over_budget + current_price - 1) // current_price)
        new_min = current_min - reduce_by
        st.session_state[f'item_min_{index}'] = new_min

    # 최소 구매량이 최대 구매량을 초과하는 경우 조정
    elif current_min > current_max:
        st.session_state[f'item_min_{index}'] = current_max
    
def on_max_change(index):
    current_max = st.session_state.get(f"item_max_{index}", 0)
    current_min = st.session_state.get(f'item_min_{index}', 0)
    current_price = st.session_state.get(f'item_price_{index}', 0)
    budget = st.session_state.get("budget")
    #에러처리
    #최댜구매개수 * 단가가 예산을 넘는 경우 가능한 최대값으로 지정, 에러메시지
    if (current_price * current_max) > budget :
        st.session_state[f'item_max_{index}'] = budget//current_price
    #위 조건을 통과한 것 중 최대구매개수가 최소구매값보다 작으면, 최소구매값과 일치.
    elif current_min > current_max:
        st.session_state[f'item_max_{index}'] = current_min
    
# 예산 계산 함수
def calculate_budget(budget, labels, prices, minis, maxis):
    try:
        text_out = f'사용해야 할 예산은 {format(budget,",")}원입니다.\n'

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
        text_out += '_' * 24 + '정렬된 데이터'+ '_' * 24 + '\n'
        for n_prt in range(item_count):
            label = cut_string(labels[n_prt], 28)                
            text_out += f"품목 #{n_prt + 1:02d} {label} = {prices[n_prt]:7,d} 원({minis[n_prt]:3d} ~ {maxis[n_prt]:3d})\n"
        text_out += '_' * 61 + '\n'

        # 기본 구매량을 구매한 후 남는 예산을 예산으로 잡고 전 예산을 저장합니다.
        total_budget = budget
        fixed_budget = sum(a * b for a, b in zip(minis, prices))
        budget -= fixed_budget

        # 최대 개수에 대해 마지막 바로 앞 노드에서 잔액이 최대치보다 클 경우: 마지막 노드는 최대치만큼 먼저 구입하고 잔액/ 마지막 바로 앞 노드의 단가로 갯수 결정
        # 각 노드에서 최대치를 넘었는지 검사.



        # _____CORE_CALCULATE THE BUDGET
        while not (node == -1 and is_overrun == True):
            # Set the left money after buy first item to left[0] according to list qnty[0]
            balances[0] = budget - (quantity[0] * prices[0])
            # Set the left money after buy items to left[n] according to list qnty[n]
            for n in range(1, last_index):
                balances[n] = balances[n - 1] - (quantity[n] * prices[n])
            # With the left money, calculates How many items(Last one) can be bought.
            quantity[last_index] = balances[last_index - 1] // prices[last_index]
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

        # 계산 결과 출력 부분
        if len(case_exact) == 0: # 완벽한 결과가 없으면 근사치 리스트를 결과로 설정
            text_out += f'{total_budget:,d}원의 예산에 맞게 구입할 방법이 없습니다.\n'
            text_out += '예산에 근접한 구입 계획은 아래와 같습니다.\n'
            list_show = case_close

        else: # 완벽한 결과가 있으면 결과로 설정
            text_out += f'{total_budget:7,d}원의 예산에 맞는 {len(case_exact):,d}개의 완벽한 방법을 찾았습니다.\n'
            list_show = case_exact
        
        # 모든 행에 더하기
        list_show = (np.array(list_show) + np.array(minis)).tolist()



        # 헤더 출력
        list_header = []
        text_out += ' '
        for n_title in range(0, item_count):
            list_header.append(f'#{n_title + 1:02d}')
            text_out += f'___#{n_title + 1:02d} '
        text_out += '\n'

        # 케이스 리스트 출력
        for n_caseshow in list_show:
            sum_show = 0
            for n_index, n_itemshow in enumerate(n_caseshow):
                sum_show += n_itemshow * prices[n_index]
                text_out += f' {n_itemshow:4d}개'
            text_out += f"   {format(sum_show, '7,d')} 원\n"
        text_out += f'이 프로그램은 {case_count + 1}개의 케이스를 계산했습니다.\n'
        return text_out, list_header, list_show, prices # 결과를 리턴

    except:
        return '에러입니다.', [], [], prices # 에러 처리된 결과를 리턴

# 웹 앱 UI 구현
result_header, result_list, result_prices = [], [], []

st.title("👌알잘딱깔센 예산 0원 만들기😊")

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
                                   on_change=on_min_change(i,min_quantities,item_prices),
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
        # 체크박스를 만들고 session state value를 만듭니다.
        item_usable = st.checkbox(f'물품{i+1}', label_visibility='collapsed', 
                                  key=f'item_usable_{i}',
                                  value=st.session_state.get(f'item_usable_{i}', True))
        st.write("")

    # 체크박스에 체크가 되어 있고 가격이 0보다 크면 리스트에 다음을 추가합니다.(이름,가격,최소,최대)
    if item_usable and item_price > 0:
        item_names.append(item_name if item_name else '')
        item_prices.append(item_price)
        min_quantities.append(item_min)
        max_quantities.append(item_max)

col_left,col_label_fixed, col_right = st.columns([2,6,2])

# 물품추가 버튼 클릭 시 호출되는 함수
def add_item():
    st.session_state.item_count += 1

# 물품추가 버튼에 콜백 함수 연결
with col_left:
    if st.button("물품추가", on_click=add_item):
        pass

with col_label_fixed:
    fixed_budget = sum(a * b for a, b in zip(min_quantities, item_prices))
    max_limit= sum(a * b for a, b in zip(max_quantities, item_prices))
    st.write(f"확정: {fixed_budget:,d}원(남은 예산: {(budget_input - fixed_budget):,d}원) 구매제한: {max_limit:,d}원")

#quantity = []
# 계산 버튼 클릭 이벤트 핸들러
with col_right:
    if st.button("계산하기"):
        if budget_input == "" or budget_input <= 0: result_text = '예산을 정확히 입력하세요.'
        elif len(item_prices) <= 1: result_text = '최소 2종류 이상의 단가를 입력하세요.'
        elif min(item_prices) <= 0: result_text = '단가가 0보다 작거나 같습니다.'
        elif max(item_prices) > budget_input: result_text = '예산이 부족합니다.'
        elif max_limit < budget_input: result_text = '최대구매가 예산보다 작아 예산을 쓸 수 없습니다.'
        elif fixed_budget > budget_input: result_text = '최소구매가 예산보다 많아 예산을 쓸 수 없습니다.'
        else:
            # 스피너를 표시하면서 계산 진행
            with st.spinner('계산 중...'):
                # 계산 결과를 구합니다.
                result_text, result_header,result_list, result_prices = calculate_budget(budget_input, item_names, item_prices,min_quantities,max_quantities)
st.text_area("Results", result_text, height=300)

# 새로운 열 '금액'을 계산하고 데이터프레임에 추가합니다.
try:
    df = pd.DataFrame(result_list, columns=result_header)
    df['금액'] = df.mul(result_prices).sum(axis=1)
    if df.__len__() != 0: st.dataframe(df,hide_index=True) # 결과를 화면에 표시합니다.
except:
    pass