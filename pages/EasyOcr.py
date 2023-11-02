import streamlit as st
import easyocr
import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image

def ocr_label(image_data,lang):
    font_path = r'G:\내 드라이브\AI STUDY\simbud\streamlit_test\pages\D2Coding-Ver1.3.2-20180524.ttf'
    font = ImageFont.truetype(font_path, 24, encoding='utf-8')
    reader = easyocr.Reader(lang)

    if isinstance(image_data, np.ndarray):
        image = image_data
    else:
        try:
            buffer = image_data.read()
            nparr = np.frombuffer(buffer, np.uint8)
        except AttributeError:
            nparr = np.frombuffer(image_data, np.uint8)
        
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    result = reader.readtext(gray)

    for (bbox, text, prob) in result:
        (top_left, top_right, bottom_right, bottom_left) = bbox
        top_left = tuple(map(int, top_left))
        bottom_right = tuple(map(int, bottom_right))
        cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)

        image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(image_pil)
        draw.text((top_left[0], top_left[1] - 24), text, font=font, fill=(0, 0, 255))
        image = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)

    st.image(image, channels="BGR")
    print(result)
    return list(zip(*result))[1]
st.title("Easy OCR 카메라")
# 멀티선택

get_language_codes = lambda names, d: list(map(d.get, filter(d.__contains__, names)))

# 예제 딕셔너리
language_dict = {
    '한국어': 'ko',
    '영어': 'en',
}


# 함수 호출 및 결과 출력



options = st.multiselect("인식할 언어를 선택하세요", ['한국어','영어'])
st.write(f"당신이 선택한 언어: {', '.join(options)}")

languages_selected = get_language_codes(options, language_dict)

picture = st.camera_input("#사진을 찍으면 문자를 인식해요!")
if picture is not None:
    if options.__len__() != 0:
        st.write(ocr_label(picture, languages_selected))
