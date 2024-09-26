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

# Function to extract images from PDF pages
def extract_images_from_pdf(pdf_file):
    pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
    images = []
    
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        for image_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            images.append(image_bytes)
    
    return images

# Function to perform OCR on images and extract text
def perform_ocr_on_images(images):
    reader = easyocr.Reader(['en'])
    extracted_data = []
    
    for img_bytes in images:
        # Convert byte data to image format and perform OCR
        text_result = reader.readtext(img_bytes, detail=0, paragraph=True)
        extracted_data.extend(text_result)
    
    return extracted_data

# Function to convert extracted text to CSV format
def convert_to_csv(data):
    df = pd.DataFrame(data, columns=["Extracted Data"])
    return df

#---------------------------------------------------------------------------------------------------------------------------------
### Main app
#---------------------------------------------------------------------------------------------------------------------------------

# File uploader for multiple files
uploaded_files = st.file_uploader("Upload your PDFs", type="pdf", accept_multiple_files=True)

if uploaded_files is not None and len(uploaded_files) > 0:
    all_extracted_data = []

    # Loop through each uploaded PDF file
    for uploaded_file in uploaded_files:
        st.write(f"Processing file: {uploaded_file.name}")
        
        # Extract images from the PDF
        with st.spinner(f"Extracting images from {uploaded_file.name}..."):
            images = extract_images_from_pdf(uploaded_file)
        
        if images:
            # Perform OCR on the extracted images
            with st.spinner(f"Performing OCR on images from {uploaded_file.name}..."):
                extracted_data = perform_ocr_on_images(images)
                all_extracted_data.extend(extracted_data)
            st.success(f"OCR completed for {uploaded_file.name}.")
        else:
            st.warning(f"No images found in {uploaded_file.name}.")
    
    # Combine and convert the extracted data to CSV format
    if all_extracted_data:
        with st.spinner("Converting extracted data to CSV..."):
            csv_data = convert_to_csv(all_extracted_data)
        
        # Provide a download button for the CSV file
        st.write("Download CSV:")
        csv = csv_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name='invoice_data.csv',
            mime='text/csv',
        )
    else:
        st.warning("No text extracted from the uploaded files.")

    


    
