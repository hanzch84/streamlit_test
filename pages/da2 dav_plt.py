import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import pandas as pd


st.title("데이터 시각화:plt")

x = range(20) # 0, 1, .. 19
y = [value**2 for value in x]+np.random.rand(20)*100


fig, ax = plt.subplots()
ax.plot(x, y)# 꺾은선그래프
st.pyplot(fig)

y1 = [value for value in x]+np.random.rand(20)*100
y2 = [value**3 for value in x]+np.random.rand(20)*100


fig, ax = plt.subplots()
ax.plot(x, y)# 꺾은선그래프


fig, ax = plt.subplots(1, 2)
ax[0].plot(x, y1)
ax[1].plot(x, y2)# 꺾은선그래프

y1 = [value for value in x]+np.random.rand(20)*100
y2 = [value**3 for value in x]+np.random.rand(20)*100


fig, ax = plt.subplots()
ax.plot(x, y)# 꺾은선그래프


fig, ax = plt.subplots(1, 2)
ax[0].plot(x, y1)
ax[1].plot(x, y2)# 꺾은선그래프