import streamlit as st

st.title("현수의 페이지!")
st.subheader("Hello, world!")



# st.caption("the page for simbudget")
# name=st.text_input("이름을 입력해주세요.")

# if name != "":
#     st.write(f"#**{name}**님 안녕하세요!")
#     st.balloons()
#     #st.snow()
# st.code("sudo apt-get update")
# st.latex("1\\times 2=3,x+3=2")
# st.latex(r"1\times 2=3, x+3=2")
# st.divider()
# st.write("---")
# ##########################################
# #이미지 비디오 불러오기

st.image("a.jpg")
# st.image("https://img.freepik.com/free-vector/flat-design-mountain-landscape_23-2149172160.jpg?size=626&ext=jpg&ga=GA1.1.386372595.1697760000&semt=ais",width=700 )
# st.video("https://www.youtube.com/watch?v=JUjpvu3mGGY", start_time=100)
st.video("https://youtu.be/qPbffXgERvM")

# st.divider()

# st.title("Interactive Widget")
# id = st.text_input("아이디를 입력해 주세요")
# pw = st.text_input("비밀번호를 입력해 주세요!", type="password")



# real_id = "pypy21"
# real_pw = "123456"

# if id == real_id and pw == real_pw :
#     st.write("로그인 성공")
# else:
#     st.write("로그인 실패! 아이디 혹은 패스워드를 다시 확인해주세요. ")