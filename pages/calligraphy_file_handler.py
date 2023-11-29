import streamlit as st
from docx import Document
from docx.shared import Pt
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.shared import Cm
from io import BytesIO

# Calculate the table width to fit A4 paper
table_width = Cm(21.0 - 2.0)  # A4 width minus 20mm left and right margins

# Create a new Word document
def create_word_document(text_to_insert):
    doc = Document()

    # Calculate the number of rows and columns needed
    num_rows = len(text_to_insert) // 7
    num_cols = 13

    # Create a table with square cells
    table = doc.add_table(rows=num_rows, cols=num_cols, width=table_width)

    # Set the alignment of the cells to center both horizontally and vertically
    for row in table.rows:
        for cell in row.cells:
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            cell.width = Cm(1.0)  # Make cells square

    # Iterate over each cell in the table and insert characters from the input text
    char_index = 0
    for row in table.rows:
        for cell in row.cells:
            if char_index < len(text_to_insert):
                cell.text = text_to_insert[char_index]
                char_index += 1

    # Save the Word document to a BytesIO object
    doc_bytes = BytesIO()
    doc.save(doc_bytes)
    doc_bytes.seek(0)

    return doc_bytes

# Streamlit app
st.title("Word Document Generator")

# Input text to be inserted into the table
text_to_insert = st.text_area("Enter text (13x7 characters):", height=100)

if st.button("Generate Word Document"):
    if len(text_to_insert) != 91:
        st.error("Please enter exactly 13x7=91 characters.")
    else:
        # Create the Word document
        doc_bytes = create_word_document(text_to_insert)

        # Offer the document for download
        st.download_button(
            label="Download Word Document",
            data=doc_bytes,
            key="word_doc",
            file_name="table_with_text.docx",
            mime="application/octet-stream",
        )

# Display the table with characters
if text_to_insert:
    st.write("Table with Characters:")
    for i in range(7):
        for j in range(13):
            st.write(text_to_insert[i * 13 + j], end=" ")
        st.write("")  # New line