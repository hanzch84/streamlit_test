import streamlit as st
import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image

# Google Cloud Vision API를 사용하기 위한 라이브러리 import
from google.cloud import vision
st.set_page_config(layout="centered")


image = st.camera_input("#사진을 찍으면 문자를 인식해요!")

# Vision API 인스턴스를 생성합니다.
client = vision.ImageAnnotatorClient()

# 텍스트 인식 요청을 생성합니다.
text_detection_request = vision.types.TextDetectionRequest()
text_detection_request.language_hints.append("ko")
text_detection_request.image.content = image

# 텍스트 인식 요청을 실행합니다.
text_detection_response = client.text_detection(text_detection_request)

# 인식된 텍스트를 출력합니다.
for text_annotation in text_detection_response.text_annotations:
    print(text_annotation.description)
    
# 인식된 텍스트를 검색합니다.
from google.cloud import search

# 검색 인스턴스를 생성합니다.
search_client = search.SearchClient()

# 쿼리를 생성합니다.
query = "검색어"

# 검색을 실행합니다.
search_results = search_client.search(
    query,
    location="[위치]",
    language="ko",
)

# 검색 결과를 출력합니다.
for search_result in search_results.results:
    print(search_result.doc_id, search_result.snippet)