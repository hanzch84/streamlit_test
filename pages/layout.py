import streamlit as st
st.set_page_config(layout="centered")


st.title("Layout")


# 두 개의 컬럼 생성
left_column, right_column = st.columns(2)

# 첫 번째 입력 창
with left_column:
    input1 = st.text_input("첫 번째 입력 창", value="")

# 두 번째 입력 창
with right_column:
    input2 = st.text_input("두 번째 입력 창", value="")

# 입력된 내용 표시
st.write("첫 번째 입력:", input1)
st.write("두 번째 입력:", input2)
