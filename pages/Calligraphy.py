import streamlit as st
import easyocr
import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image
import docx



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


col_box, col_btn_commit = st.columns([9,1])
with col_box:
    text_area_input = st.text_area("글씨쓰기 연습할 문구를 입력하세요.")
                 
        
char_box_id = {}
cols = st.columns(13)

for j,col in enumerate(cols):
    for i in range(5):
        char_box_id[f"{i}{j}"] = col.text_input(f"char{i}{j}",label_visibility="collapsed")

if col_btn_commit.button("입력"):
    # 2차원 리스트를 생성합니다.
    text_array_2D = []
    # 3개의 세로 행을 만듭니다.
    for i in range(3):
        row = ["", "", "", "", "", "", "", "", "", "", "", "", ""]
        text_array_2D.append(row)
            
    for row_num in range(3):
        for col_num in range(13):
            if text_area_input!="":
                first_char = text_area_input[0]
                if first_char == '\n':
                    break
                text_array_2D.append(first_char)
                st.session_state[f"char{i}{j}"] = first_char
                text_area_input = text_area_input[1:]
                
                



# 딕셔너리

languages_selected = ["한국어", "영어"]

radio_cam_option = st.radio("카메라 촬영 vs 파일 업로드", ["파일 업로드", "카메라 촬영"])

font_color = hex_to_rgb(st.color_picker('폰트 색상을 지정하세요.','#FF0000'))

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
