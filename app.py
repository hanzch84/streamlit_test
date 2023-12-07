import streamlit as st
st.set_page_config(layout="wide")
st.title("현수의 페이지!")
st.subheader("Hello, world!")

col1, col2, col3 = st.columns(3)

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

col1.image("a.jpg")
col2.image("https://media.licdn.com/dms/image/D5622AQGuxS8pMNND_g/feedshare-shrink_2048_1536/0/1701987220010?e=1704931200&v=beta&t=BI3n2YvwzsdHYCEfqErSi_xMiFhCnngLBa5FqMpxSkM")
col3.image("https://media.licdn.com/dms/image/D5622AQGatP51eua6hw/feedshare-shrink_1280/0/1701987219235?e=1704931200&v=beta&t=EQLltFXtkez6WgGpbwoKekdbNZJ0e6QZh4B_Pztn6q4")
# st.image("https://img.freepik.com/free-vector/flat-design-mountain-landscape_23-2149172160.jpg?size=626&ext=jpg&ga=GA1.1.386372595.1697760000&semt=ais",width=700 )
# st.video("https://www.youtube.com/watch?v=JUjpvu3mGGY", start_time=100)
col_l, col_r = st.columns(2)

col_l.video("https://youtu.be/qPbffXgERvM")
col_r.video("https://youtube.com/shorts/Zqw2fIhj9NM?si=bCD3hyiIGHAYzwnF")
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