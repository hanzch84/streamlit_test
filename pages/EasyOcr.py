import streamlit as st
import easyocr
import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image

def ocr_label(image_data,lang,font_color):
    font_path = 'pages/D2Coding-Ver1.3.2-20180524.ttf'
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
        cv2.rectangle(image, top_left, bottom_right, (0,255,0), 2)

        image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(image_pil)
        draw.text((top_left[0], top_left[1] - 24), text, font=font, fill=font_color)
        image = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)

    st.image(image, channels="BGR")
    return result
st.title("Easy OCR 카메라")
# 멀티선택


def hex_to_rgb(hex_color):
    # 앞의 '#' 기호를 제거합니다.
    hex_color = hex_color.lstrip('#')
    
    # 문자열을 세 부분으로 나누고 각각을 16진수에서 10진수로 변환합니다.
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    return (r, g, b)

get_language_codes = lambda names, d: list(map(d.get, filter(d.__contains__, names)))

# 예제 딕셔너리
language_dict = {
    "한국어": "ko",
    "영어": "en",
}

font_color = hex_to_rgb(st.color_picker('Pick a color',))
st.write(font_color)

# 함수 호출 및 결과 출력

# 라디오 버튼
radio_option = st.radio("당신의 선택은?", ["한국어", "영어", "한국어, 영어"])
st.write(f"당신은 {radio_option}을(를) 선택하셨습니다.")
if radio_option=="한국어, 영어":
    radio_option=["한국어", "영어"]
languages_selected = get_language_codes(radio_option, language_dict)

picture = st.camera_input("#사진을 찍으면 문자를 인식해요!")
if picture is not None:
    if radio_option.__len__() != 0:
        
        outputs = ocr_label(picture, languages_selected,font_color)
        if outputs.__len__() != 0:
            ocr_text = list(zip(*outputs))[1]
            st.write(ocr_text)



options = st.multiselect("인식된 단어를 고르세요.", ocr_text)
st.write(f"당신이 선택한 단어: {', '.join(options)}")
