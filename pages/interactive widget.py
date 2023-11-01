import streamlit as st
import time

# 체크박스
if st.checkbox("텍스트를 보여줄까요?"):
    st.write("체크박스가 선택되었습니다!")

# 라디오 버튼
radio_option = st.radio("당신의 선택은?", ["A", "B", "C"])
st.write(f"당신은 {radio_option}을(를) 선택하셨습니다.")

# 멀티선택
options = st.multiselect("어떤 색상을 좋아하나요?", ["Red", "Green", "Blue"])
st.write(f"당신이 선택한 색상: {', '.join(options)}")

# 프로그레스 바
'start your progress'
my_bar = st.progress(0)
for percent_complete in range(100):
    time.sleep(0.01)  # 0.01초마다 프로그레스 바가 업데이트됩니다.
    my_bar.progress(percent_complete + 1)