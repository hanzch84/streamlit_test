import streamlit as st
import easyocr
import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image
import docx

st.markdown(
    """
    <style>
        /* 폰트와 텍스트 스타일 설정 */
        input,body{
            font-family: 'Noto sans Kr', sans-serif !important;}
        /* 텍스트 정렬 */
        input{ text-align: center; margin: -5px; font-size: 20px;}
        h1,h3{ text-align: center; }        
    </style>""", unsafe_allow_html=True)

st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)

ocr_text=[]
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

def hex_to_rgb(hex_color):
    # 앞의 '#' 기호를 제거합니다.
    hex_color = hex_color.lstrip('#')
    
    # 문자열을 세 부분으로 나누고 각각을 16진수에서 10진수로 변환합니다.
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    return (r, g, b)

get_language_codes = lambda names, d: list(map(d.get, filter(d.__contains__, names)))

# 페이지 랜더링
st.title("도전! 예쁜 글씨 쓰기👍")


col_box, col_btn_commit = st.columns([12,1])
with col_box:
    text_area_input = st.text_area("글씨 쓰기 연습할 문구를 입력하세요.",height=135,placeholder="글씨 쓰기 연습할 문구를 입력하세요.",label_visibility='collapsed')
                 
single_marks = [".",",","?","!"]
char_box_id = {}
cols = st.columns(13)



if col_btn_commit.button("학습지 생성"):
    # 2차원 리스트를 생성합니다.
    text_array_2D = []
    # 3개의 세로 행을 만듭니다.
    for i in range(7):
        row = ["", "", "", "", "", "", "", "", "", "", "", "", ""]
        text_array_2D.append(row)
            
    for row_num in range(7):
        for col_num, col in enumerate(cols):
            if text_area_input!="":
                first_char = text_area_input[0]
                text_area_input = text_area_input[1:]
                if first_char == '\n':
                    first_char = ""
                    text_area_input = (" " * (12-col_num)) + text_area_input
                elif first_char in single_marks:
                    first_char += " "
                    if text_area_input!="":
                        if text_area_input[0] == " ":
                            text_area_input = text_area_input[1:]
                                                        
            else: first_char = " "
            text_array_2D[row_num][col_num] = first_char
            char_box_id[f"{col_num}{row_num}"] = col.text_input(f"char{col_num}{row_num}",
                                                                label_visibility="collapsed",
                                                                value=first_char,
                                                                max_chars=1,
                                                                key=f"char{col_num}{row_num}")

languages_selected = ["ko", "en"]
font_color = hex_to_rgb(st.color_picker('폰트 색상을 지정하세요.','#00FF00'))
radio_cam_option = st.radio("카메라 촬영 vs 파일 업로드", ["카메라 촬영", "파일 업로드"],label_visibility='collapsed')

if radio_cam_option == "카메라 촬영":
    picture = st.camera_input("#사진을 찍으면 문자를 인식해요!")
else:
    picture = st.file_uploader('이미지를 업로드 하세요.', type=['png', 'jpg', 'jpeg'])

if picture is not None:
    outputs = ocr_label(picture, languages_selected,font_color)
    if outputs.__len__() != 0:
        ocr_text = list(zip(*outputs))[1]
        st.write(ocr_text)
    options = st.multiselect("인식된 단어를 고르세요.", ocr_text)
    st.write(f"당신이 선택한 단어: {', '.join(options)}")
