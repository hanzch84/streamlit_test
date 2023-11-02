import streamlit as st
import numpy as np
import pandas as pd

# 문자열의 출력 길이를 구하는 함수
def getPrintLength(s):
    let = 0
    for i in s:
        let += len(i)
    return let

# 문자를 길이만큼만 남기고 자르는 함수.
def cutString(s, maxLength):
    cutS = ''
    length = 0
    for char in s:
        charLength = len(char)
        if length + charLength > maxLength: break
        cutS += char
        length += charLength
    return cutS

# 예산 계산 함수
def calculate_budget(budget, labels, prices):
    item_length = len(prices)
    quantity = np.zeros(item_length, dtype=np.int32)
    left = np.zeros(item_length, dtype=np.int32)
    over = False
    node = item_length - 2

    while node != -1 or over != True:
        left[0] = budget - (quantity[0] * prices[0])

        for i in range(1, item_length - 1):
            left[i] = left[i - 1] - (quantity[i] * prices[i])

        quantity[item_length - 1] = int(left[item_length - 2] / prices[item_length - 1])
        left[item_length - 1] = left[item_length - 2] - (quantity[item_length - 1] * prices[item_length - 1])

        if left.any() < 0:
            over = True
            quantity[node] = 0
            node -= 1
        else:
            node = -1

    # 결과를 리턴
    return quantity

# 웹 앱 UI 구현
st.title("👌알잘딱깔센 예산 쓰기")
st.subheader("예산 0 만들기")

# 예산 입력
budget = st.number_input("예산", min_value=10, help="사용해야하는 예산을 입력하세요.")

# session_state를 확인하여 물품 개수를 관리합니다.
if 'item_count' not in st.session_state:
    st.session_state.item_count = 1

# 물품 입력 섹션을 생성합니다.
item_names = []
item_prices = []

for i in range(st.session_state.item_count):
    col_name, col_min, col_max, col_price, col_usable = st.columns([3,1,1,2,1.1])
    with col_name:
        # 고유한 키를 생성하기 위해 인덱스를 사용합니다.
        item_name = st.text_input("", key=f"item_name_{i}",placeholder=f"물품{i+1} 이름 입력")
    with col_min:
        item_min = st.number_input(f"최소 {i+1}", min_value=0, key=f"item_min_{i}")
    with col_max:
        item_max = st.number_input(f"최대 {i+1}", min_value=0, key=f"item_max_{i}")
    with col_price:
        item_price = st.number_input(f"물품 단가 {i+1}", min_value=0, key=f"item_price_{i}",value=10, )
    with col_usable:
        item_usable = st.checkbox(f"물품{i+1}", key=f"item_usable_{i}",value="True")

    
    item_names.append(item_name)
    item_prices.append(item_price)


col_left, col_right, col_aux = st.columns(3)

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
        # 계산 결과를 구합니다.
        quantity = calculate_budget(budget, item_names, item_prices)

    # 결과를 화면에 표시합니다.
    df = pd.DataFrame({
        "품목": item_names,
        "단가": item_prices,
        "수량": quantity
    })



    with col_aux:
        # 파일로 저장하는 기능을 제공합니다.
        if st.checkbox("파일로 저장"):
            df.to_csv("output.csv")
    st.table(df)  

st.write("감사합니다.")