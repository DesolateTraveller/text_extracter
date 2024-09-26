#---------------------------------------------------------------------------------------------------------------------------------
### Authenticator
#---------------------------------------------------------------------------------------------------------------------------------
import streamlit as st
#---------------------------------------------------------------------------------------------------------------------------------
### Import Libraries
#---------------------------------------------------------------------------------------------------------------------------------
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
#----------------------------------------
import requests
import easyocr
import fitz  # PyMuPDF
from io import BytesIO
from PIL import Image
#---------------------------------------------------------------------------------------------------------------------------------
### Title and description for your Streamlit app
#---------------------------------------------------------------------------------------------------------------------------------
#import custom_style()
st.set_page_config(page_title="Text Extracter | v0.1",
                   layout="wide",
                   page_icon="💻",             
                   initial_sidebar_state="collapsed")
#----------------------------------------
st.title(f""":rainbow[Text Extracter]""")
st.markdown(
    '''
    Created by | <a href="mailto:avijit.mba18@gmail.com">Avijit Chakraborty</a> ( 📑 [Resume](https://resume-avijitc.streamlit.app/) | :bust_in_silhouette: [LinkedIn](https://www.linkedin.com/in/avijit2403/) | :computer: [GitHub](https://github.com/DesolateTraveller) ) |
    for best view of the app, please **zoom-out** the browser to **75%**.
    ''',
    unsafe_allow_html=True)
st.info('**A lightweight text extraction streamlit app that extracts text and convert it into tabular format from uploaded file (pdf, image etc.)**', icon="ℹ️")
#----------------------------------------
# Set the background image
st.divider()
#---------------------------------------------------------------------------------------------------------------------------------
### Functions & Definitions
#---------------------------------------------------------------------------------------------------------------------------------

def extract_text_from_pdf(pdf_file):
    pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text("text")
    return text

def perform_ocr(text):
    reader = easyocr.Reader(['en'])
    result = reader.readtext(text)
    extracted_data = []
    for item in result:
        extracted_data.append(item[1]) 
    return extracted_data

def convert_to_csv(data):
    df = pd.DataFrame(data, columns=["Extracted Data"])
    return df

def extract_images_and_metadata_from_pdf(pdf_file):
    document = fitz.open(stream=pdf_file.read(), filetype="pdf")
    images_and_metadata = []
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = document.extract_image(xref)
            image_bytes = base_image["image"]
            image = Image.open(BytesIO(image_bytes))
            metadata = {
                "Page Number": page_num + 1,
                "Image Number": img_index + 1,
                "Image Width": image.width,
                "Image Height": image.height,
                "Image Format": image.format,
                "Image Mode": image.mode
                }
            images_and_metadata.append((image, metadata))
    return images_and_metadata

#---------------------------------------------------------------------------------------------------------------------------------
### Main app
#---------------------------------------------------------------------------------------------------------------------------------



# File uploader
uploaded_file = st.file_uploader("Upload your PDF", type="pdf")

if uploaded_file is not None:
    with st.spinner("Extracting text from PDF..."):
        extracted_text = extract_images_and_metadata_from_pdf(uploaded_file)
        st.success("Text extraction completed.")

        st.subheader(f"Preview : {uploaded_file.name}",divider='blue')
        if extracted_text:
            st.markdown(f"Found {len(extracted_text)} image(s) in the PDF {uploaded_file.name}.",unsafe_allow_html=True)
            for img_index, (image, metadata) in enumerate(extracted_text):
                st.image(image, caption=f"Image {img_index + 1} from Page {metadata['Page Number']}", use_column_width=True)
    


    
