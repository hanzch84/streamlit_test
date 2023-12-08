import streamlit as st
from docx import Document
from docx.shared import Pt
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn
from docx.shared import Cm, RGBColor
from io import BytesIO
import pandas as pd
import qrcode
from pyzbar.pyzbar import decode
import easyocr
import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image
st.set_page_config(layout="centered")

st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)


# Calculate the table width to fit A4 paper
table_width = Cm(21.0 - 2.0)  # A4 width minus 20mm left and right margins

def maketextgrid(text_area_input):
    single_marks = [".",",","?","!"]
    # 2차원 리스트를 생성합니다.
    text_array_2D = []
    # 3개의 세로 행을 만듭니다.
    for i in range(7):
        row = ["", "", "", "", "", "", "", "", "", "", "", "", ""]
        text_array_2D.append(row)
            
    for row_num in range(7):
        for col_num in range(13):
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
    return text_array_2D

# Create a new Word document
def create_word_document(text_grid, qr_code_data=None):
    doc = Document()
    
    # Change the page orientation to landscape (horizontal)
    section = doc.sections[0]
    new_width, new_height = section.page_height, section.page_width
    section.orientation = WD_ORIENT.LANDSCAPE
    section.page_width = new_width
    section.page_height = new_height

    # Calculate the number of rows and columns needed
    num_rows = 7
    num_cols = 13
    style = doc.styles['Normal']
    style.font.name = '궁서체'    
    style.font.size = Pt(32)
    style.font.color.rgb = RGBColor(0x99, 0x99, 0x99)

    style._element.rPr.rFonts.set(qn('w:eastAsia'), '궁서체') # 한글 폰트를 따로 설정해 준다



    # Create a table with square cells
    table = doc.add_table(rows=num_rows, cols=num_cols)
    table.style = doc.styles['Table Grid']

    # Set the alignment of the cells to center both horizontally and vertically
    for row in table.rows:
        row.height = Cm(1.6)
        for cell in row.cells:
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            cell.width = Cm(1.6)  # Make cells square
            cell.height = Cm(2)

    # Set the font size and name for all cells
    for row in table.rows:
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(32)  # 24-point font size
                    run.font.name = '궁서체'  # Palace font

    # Iterate over each cell in the table and insert characters from the input text grid
    for row_num in range(num_rows):
        for col_num in range(num_cols):
            cell = table.cell(row_num, col_num)
            cell.text = text_grid[row_num][col_num]
    
    doc.add_page_break()



    # Create a table with square cells
    table2 = doc.add_table(rows=num_rows, cols=num_cols)
    table2.style = doc.styles['Table Grid']

    # Set the alignment of the cells to center both horizontally and vertically
    for row in table2.rows:
        row.height = Cm(1.6)
        for cell in row.cells:
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            cell.width = Cm(1.6)  # Make cells square
            cell.height = Cm(2)

    # Set the font size and name for all cells
    for row in table2.rows:
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(32)  # 24-point font size
                    run.font.name = '궁서체'  # Palace font


    # Insert QR code if QR code data is provided
    if qr_code_data:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_code_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img_bytes = BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        doc.add_picture(img_bytes, width=Cm(4), height=Cm(4))

    # Save the Word document to a BytesIO object
    doc_bytes = BytesIO()
    doc.save(doc_bytes)
    doc_bytes.seek(0)

    return doc_bytes



def ocr_label(image_data, lang, font_color):
    font_path = 'pages/D2Coding-Ver1.3.2-20180524.ttf'
    font = ImageFont.truetype(font_path, 24, encoding='utf-8')
    reader = easyocr.Reader(lang)

    # 이미지 데이터가 NumPy 배열인 경우, 해당 배열을 사용
    if isinstance(image_data, np.ndarray):
        image = image_data
    else:
        try:
            # 파일 포인터를 시작 부분으로 이동
            image_data.seek(0)
            # 파일 객체에서 데이터 읽기
            buffer = image_data.read()
        except AttributeError:
            # 이미 바이트 배열인 경우, 직접 사용
            buffer = image_data

        # 바이트 배열을 NumPy 배열로 변환
        nparr = np.frombuffer(buffer, np.uint8)
        if nparr.size == 0:
            # 배열이 비어 있으면 오류 메시지 출력
            raise ValueError("이미지 데이터가 비어 있습니다.")

        # NumPy 배열을 이미지로 디코드
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if image is None:
            # 이미지 디코딩 실패 시 오류 메시지 출력
            raise ValueError("이미지 디코딩에 실패했습니다.")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    result = reader.readtext(gray)

    for (bbox, text, prob) in result:
        (top_left, top_right, bottom_right, bottom_left) = bbox
        top_left = tuple(map(int, top_left))
        bottom_right = tuple(map(int, bottom_right))
        cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)

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



# Streamlit app
st.title("도전! 예쁜 글씨 쓰기👍")
st.subheader("글씨쓰기 학습지 만들기 + 자동 채점하기")
st.write("학습지의 앞면은 따라쓰기, 뒷면은 빈 칸입니다. 뒷면에 있는 qr코드로 손글씨의 정답을 인식합니다.")
         

# Input text to be inserted into the table
text_to_insert = st.text_area("Enter text (13x7 characters):", height=100)
result_matrix = maketextgrid(text_to_insert)
df =pd.DataFrame(result_matrix)          
st.dataframe(df,hide_index=True,use_container_width=True)

st.write(len(text_to_insert),len(text_to_insert)//13)

if st.button("Generate Word Document"):
    
    # Create the Word document
    result_qr = ''.join([''.join(row) for row in result_matrix])
    doc_bytes = create_word_document(result_matrix, result_qr)

    # Offer the document for download
    st.download_button(
        label="Download Word Document",
        data=doc_bytes,
        key="word_doc",
        file_name="table_with_text.docx",
        mime="application/octet-stream",
    )
languages_selected = ["ko", "en"]
font_color = hex_to_rgb(st.color_picker('폰트 색상을 지정하세요.','#00FF00'))
radio_cam_option = st.radio("카메라 촬영 vs 파일 업로드", ["카메라 촬영", "파일 업로드"],label_visibility='collapsed')

if radio_cam_option == "카메라 촬영":
    picture = st.camera_input("#사진을 찍으면 문자를 인식해요!")
else:
    picture = st.file_uploader('이미지를 업로드 하세요.', type=['png', 'jpg', 'jpeg'])

if picture is not None:
    d = decode(Image.open(picture))
    for data in d:
        st.code(f"{data.type} = {data.data.decode('utf-8')}",language="ada")
    outputs = ocr_label(picture, languages_selected,font_color)
    if outputs.__len__() != 0:
        ocr_text = list(zip(*outputs))[1]
        st.write(ocr_text)
    options = st.multiselect("인식된 단어를 고르세요.", ocr_text)
    st.write(f"당신이 선택한 단어: {', '.join(options)}")
