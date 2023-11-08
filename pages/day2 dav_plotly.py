# Plotly와 Streamlit을 사용한 데이터 시각화 애플리케이션
import plotly.express as px  # Plotly Express를 불러옵니다.
import streamlit as st  # Streamlit 라이브러리를 불러옵니다.

st.title("plotly를 활용한 데이터 시각화")

st.subheader("gapminder 데이터")
# 데이터 준비: Plotly Express의 내장 데이터셋인 gapminder를 불러옵니다.
df = px.data.gapminder()

# 산점도 그래프를 생성합니다. 2007년 데이터에 대해 국가별 GDP, 기대 수명 등을 시각화합니다.
fig = px.scatter(
    df.query("year==2007"),  # 2007년 데이터만 필터링합니다.
    x="gdpPercap",  # x축은 1인당 GDP
    y="lifeExp",  # y축은 기대 수명
    size="pop",  # 점의 크기는 인구수를 기준으로 합니다.
    color="continent",  # 색상은 대륙별로 구분합니다.
    hover_name="country",  # 마우스 오버시 나라 이름을 표시합니다.
    log_x=True,  # x축은 로그 스케일로 표시합니다.
    size_max=60,  # 점의 최대 크기를 설정합니다.
)
