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
# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    # Open the uploaded PDF file
    pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
    
    text = ""
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text("text")
    
    return text

# Function to perform OCR on extracted text
def perform_ocr(text):
    reader = easyocr.Reader(['en'])
    result = reader.readtext(text)
    extracted_data = []
    for item in result:
        extracted_data.append(item[1])  # Extract the text component
    return extracted_data

# Function to convert extracted text to CSV format
def convert_to_csv(data):
    # Assuming the data is a simple list for now; you can structure it into columns as needed.
    df = pd.DataFrame(data, columns=["Extracted Data"])
    return df

#---------------------------------------------------------------------------------------------------------------------------------
### Main app
#---------------------------------------------------------------------------------------------------------------------------------


# Streamlit app
st.title("Invoice PDF to CSV Extractor")
st.write("Upload an invoice PDF file and extract it into a CSV format.")

# File uploader
uploaded_file = st.file_uploader("Upload your PDF", type="pdf")

if uploaded_file is not None:
    # Extract text from the PDF
    with st.spinner("Extracting text from PDF..."):
        extracted_text = extract_text_from_pdf(uploaded_file)
        st.success("Text extraction completed.")
    
    # Display extracted text (optional)
    st.write("Extracted Text:")
    st.text_area("Extracted Text", value=extracted_text, height=300)

    # Perform OCR on the extracted text
    with st.spinner("Performing OCR..."):
        extracted_data = perform_ocr(extracted_text)
        st.success("OCR completed.")
    
    # Convert the extracted data to CSV format
    with st.spinner("Converting to CSV..."):
        csv_data = convert_to_csv(extracted_data)
    
    # Provide a download button for the CSV file
    st.write("Download CSV:")
    csv = csv_data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name='invoice_data.csv',
        mime='text/csv',
    )
