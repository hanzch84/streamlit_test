import streamlit as st
import numpy as np
import pandas as pd

result_text = '''예산과 단가를 입력한 후
계산하기 버튼을 누르면,
예산에 딱 맞게 물건을
살 수 있는 방법을 찾아줍니다.
물품 추가 버튼을 눌러
물품을 추가할 수도 있고,
체크박스의 체크 표시를 해제하면
잠시 계산에서 제외할 수도 있습니다.
파일로 저장에 체크하면
csv파일로 결과를 다운받습니다.'''
result_header =[]
result_list =[]
result_prices=[]

# Streamlit 페이지에 CSS를 추가하여 모든 숫자 입력란의 텍스트를 오른쪽으로 정렬합니다.
st.markdown(
    """
    <style>
        input[type="checkbox"] {
        height: 40px;
    }
        input[type="number"] {
        text-align: right;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 문자열의 출력 길이를 구하는 함수
def get_print_length(s):
    length = 0
    for char in s:
        if '\u0000' <= char <= '\u007F':  # ASCII 문자 범위
            length += 1
        elif '\u0080' <= char <= '\u07FF':  # 2바이트 문자 범위
            length += 2
        elif '\u0800' <= char <= '\uFFFF':  # 3바이트 문자 범위
            length += 2
        else:
            length += 2  # 4바이트 문자 범위
    return length

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

# 예산 계산 함수
def calculate_budget(budget, labels, prices):
    try:
        text = ""
        text += f'Your budget to spend out is ${budget:d}\n'
  
        quantity = [0] * len(labels)  # Set the List to count the quantity of Each Items.
        left = [0] * len(labels)  # Set the List to save left budget after spend (each item * quantity)

        over = False  # It checks budget over error.

        item_length = len(prices)  # check the numbers of item to calculate.
        node_end = item_length - 2  # is the end of node we change quantity manually.
        last_idx = item_length - 1  # is the last number of list index
        node = node_end  # node number sets to node_end(default position)

        case_number = 0  # counts how many cases we checked.

        case_exact = []  # stores the case with no balance.
        case_close = []  # stores the case with balance.

        print('__Generated_Data__')
        # _____PRINT item list
        text += '_' * 17 + '입력된 데이터'+ '_' * 17 + '\n'
        for n_prt in range(item_length):
            label = cut_string(labels[n_prt], 28)
            if get_print_length(label) < 28:
                label += ' '
            text += f'품목 #{n_prt + 1:02d} {label}' + (
                        ' ' * (28 - get_print_length(labels[n_prt]))) + f' $ {prices[n_prt]:6,d} \n'
        
        text += '_' * 47 + '\n'


        # labels와 prices를 결합하여 prices 기준으로 내림차순 정렬
        combined = zip(prices, labels)
        sorted_combined = sorted(combined, reverse=True)

        # 정렬된 데이터를 다시 분리
        prices, labels = zip(*sorted_combined)

        print('__Sorted_Data__')
        # _____PRINT item list
        text += '_' * 17 + '정렬된 데이터'+ '_' * 17 + '\n'
        for n_prt in range(item_length):
            label = cut_string(labels[n_prt], 28)
            if get_print_length(label) < 28:
                label += ' '
            text += f'품목 #{n_prt + 1:02d} {label}' + (
                        ' ' * (28 - get_print_length(labels[n_prt]))) + f' $ {prices[n_prt]:6,d} \n'
        
        text += '_' * 47 + '\n'


        # _____CORE
        while not (node == -1 and over == True):
            # CALCULATE THE BUDGET
            # Set the left money after buy first item to left[0] according to list qnty[0]
            left[0] = budget - (quantity[0] * prices[0])
            # Set the left money after buy items to left[n] according to list qnty[n]
            for n in range(1, last_idx):
                left[n] = left[n - 1] - (quantity[n] * prices[n])
            # With the left money, calculates How many items(Last one) can be bought.
            quantity[last_idx] = int(left[last_idx - 1] / prices[last_idx])
            left[last_idx] = left[last_idx - 1] - (quantity[last_idx] * prices[last_idx])

            #  CHECK ERROR(Over Purchasing)
            #  IF ERROR occurs reset current node's 'qnty'(quantity) to 0.
            # and node up to count up upper node item's 'qnty'(quantity).
            if any([i < 0 for i in left]):
                over = True
                quantity[node] = 0
                node -= 1

            #  IF there is no ERROR, Set over to False.
            # and reset node to the end(index of just before the last item in the list)
            else:
                over = False
                node = node_end
                # SAVE THE RESULT
                # IF Balance is $0, then save it to the case_exact
                # IF Balance is over $0, save it to the case_close
                if (left[last_idx] == 0):
                    case_exact.append(list(quantity))
                elif (left[last_idx] > 0):
                    case_close.append(list(quantity))

            # PREPAIR NEXT CASE
            quantity[node] += 1
            case_number += 1

        # _____Print result of the program.
        if len(case_exact) == 0:
            plural = 's'
            isare = 'are'
            if len(case_close) == 1:
                plural = ''
                isare = 'is'
            # If there is no perfect case. set the close case list to show.
            print('There is no way to spend all of     $', format(budget, '7,d'))
            print('Next best case', plural, ' ', isare, sep='')
            text += f'\u00A0{budget:7,d}원의 예산에 맞게 구입할 방법이 없습니다.\n\n'
            text += '예산에 근접한 구입 계획은 아래와 같습니다.\n\n'
            list_show = case_close

        else:
            # If there are perfect cases. set the exact list to show.
            plural = 's'
            if len(case_exact) == 1:
                plural = ''
            print('FOUND ', len(case_exact), ' PERFECT case', plural, ' to spend $', format(budget, '7,d'), sep='')
            text += f'\u00A0{budget:7,d}원의 예산에 맞는 {len(case_exact)}개의 완벽한 방법을 찾았습니다.\n\n'
            list_show = case_exact

        # Print the title of List.
        print('  ', end='')
        list_header = []
        text += '\u00A0\u00A0'
        for n_title in range(0, item_length):
            print('#', format(n_title + 1, '02d'), '  ', end='', sep='')
            list_header.append(f'#{n_title + 1:02d}')
            text += f'#{n_title + 1:02d}  '
        print('')
        text += '\n\n '

        # List up cases.
        for n_caseshow in list_show:
            sum_show = 0
            for n_index, n_itemshow in enumerate(n_caseshow):
                sum_show += n_itemshow * prices[n_index]
                print(format(n_itemshow, '3d'), 'EA', sep='', end='')
                text += '\u00A0'*(3-len(str(n_itemshow))) + f'{n_itemshow}EA'

            print('   $', format(sum_show, '7,d'), sep='')
            text += '   $' + format(sum_show, '7,d') + '\n\n '

        print('The program has calculated', case_number + 1, 'cases.')
        text += f'이 프로그램은 {case_number + 1}개의 케이스를 계산했습니다.\n'

    except:
        text = '에러입니다.'
        list_header =[]
        list_show =[]


    # 결과를 리턴
    return text, list_header, list_show, prices

# 웹 앱 UI 구현
st.title("👌알잘딱깔센 예산 쓰기")
st.subheader("예산 0원 만들기")

# 예산 입력
budget = st.number_input("예산", min_value=0, help="사용해야하는 예산을 입력하세요.", format="%d")

# session_state를 확인하여 물품 개수를 관리합니다.
if 'item_count' not in st.session_state:
    st.session_state.item_count = 3

# 아이템 섹션 생성 반복문
item_names = []
item_prices = []
col1, col2, col3, col4, col5 = st.columns([2.5, 1, 1, 2, 1])
with col1:
    st.write("물품이름")
with col2:
    st.write("최소구매")
with col3:
    st.write("최대구매")
with col4:
    st.write("물품단가")
with col5:
    st.write("선택")

for i in range(st.session_state.item_count):
    
    with col1:
        # If the checkbox is unchecked, disable the input fields
        is_disabled = not st.session_state.get(f'item_usable_{i}', True)
        item_name = st.text_input(f"물품{i+1} 이름 입력", label_visibility='collapsed',
                                  key=f"item_name_{i}",
                                  placeholder=f"물품{i+1} 이름 입력",
                                  disabled=is_disabled)
    with col2:
        item_min = st.number_input(f"최소 {i+1}", min_value=0, key=f"item_min_{i}",
                                  disabled=is_disabled, format="%d", label_visibility='collapsed')
    with col3:
        item_max = st.number_input(f"최대 {i+1}", min_value=0, key=f"item_max_{i}",
                                  disabled=is_disabled, format="%d", label_visibility='collapsed')
    with col4:
        item_price = st.number_input("",
                                     min_value=0,
                                     key=f"item_price_{i}",
                                     value=0,
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
print(item_names)
print(item_prices)
print(budget)

col_left, col_right = st.columns(2)

# 물품추가 버튼 클릭 시 호출되는 함수
def add_item():
    st.session_state.item_count += 1



# 물품추가 버튼에 콜백 함수 연결
with col_left:
    if st.button("물품추가", on_click=add_item):
        pass

quantity = 0

# 계산 버튼 클릭 이벤트 핸들러
with col_right:
    if st.button("계산하기"):
        if budget == "" or budget <= 0: result_text = '예산을 정확히 입력하세요.'
        elif len(item_prices) == 0: result_text = '단가를 입력하세요.'
        elif min(item_prices) <= 0: result_text = '단가가 0보다 작거나 같습니다.'
        elif max(item_prices) > budget: result_text = '예산이 부족합니다.'
        else:
            # 계산 결과를 구합니다.
            result_text, result_header,result_list, result_prices = calculate_budget(budget, item_names, item_prices)
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

with st.expander('데이터프레임 보기') :
    st.dataframe(df)  