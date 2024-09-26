import streamlit as st
import easyocr
import pandas as pd
import fitz  # PyMuPDF
from io import BytesIO
import re

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

# Function to clean and structure extracted text
def structure_extracted_data(extracted_data):
    structured_data = {
        "Invoice Number": "",
        "Date": "",
        "Customer Name": "",
        "Customer Address": "",
        "Item Descriptions": [],
        "Quantity": [],
        "Unit Price": [],
        "Total Price": [],
        "Tax": "",
        "Grand Total": ""
    }
    
    for line in extracted_data:
        # Example regex patterns for capturing common fields (modify based on specific invoice layout)
        if re.search(r"Invoice Number", line, re.IGNORECASE):
            structured_data["Invoice Number"] = re.findall(r"Invoice Number[:\s]*([A-Za-z0-9\-]+)", line)[0]
        elif re.search(r"Date", line, re.IGNORECASE):
            structured_data["Date"] = re.findall(r"Date[:\s]*([\d\-\/]+)", line)[0]
        elif re.search(r"Customer Name", line, re.IGNORECASE):
            structured_data["Customer Name"] = line.split(":")[-1].strip()
        elif re.search(r"Customer Address", line, re.IGNORECASE):
            structured_data["Customer Address"] = line.split(":")[-1].strip()
        elif re.search(r"Grand Total", line, re.IGNORECASE):
            structured_data["Grand Total"] = re.findall(r"Grand Total[:\s]*([0-9\.,]+)", line)[0]
        elif re.search(r"Tax", line, re.IGNORECASE):
            structured_data["Tax"] = re.findall(r"Tax[:\s]*([0-9\.,]+)", line)[0]
        elif re.search(r"Total", line, re.IGNORECASE):
            structured_data["Total Price"].append(re.findall(r"Total[:\s]*([0-9\.,]+)", line)[0])
        elif re.search(r"\bItem\b", line, re.IGNORECASE):  # Example for item description (adjust based on format)
            structured_data["Item Descriptions"].append(line.strip())
        elif re.search(r"\bQuantity\b", line, re.IGNORECASE):  # Example for quantity (adjust based on format)
            structured_data["Quantity"].append(re.findall(r"Quantity[:\s]*([0-9]+)", line)[0])
        elif re.search(r"\bUnit Price\b", line, re.IGNORECASE):  # Example for unit price (adjust based on format)
            structured_data["Unit Price"].append(re.findall(r"Unit Price[:\s]*([0-9\.,]+)", line)[0])

    return structured_data

# Function to convert structured data into a CSV-friendly format
def convert_to_csv(structured_data):
    # Create a list of dictionaries for each line item
    rows = []
    for i in range(len(structured_data["Item Descriptions"])):
        rows.append({
            "Invoice Number": structured_data["Invoice Number"],
            "Date": structured_data["Date"],
            "Customer Name": structured_data["Customer Name"],
            "Customer Address": structured_data["Customer Address"],
            "Item Description": structured_data["Item Descriptions"][i],
            "Quantity": structured_data["Quantity"][i] if i < len(structured_data["Quantity"]) else "",
            "Unit Price": structured_data["Unit Price"][i] if i < len(structured_data["Unit Price"]) else "",
            "Total Price": structured_data["Total Price"][i] if i < len(structured_data["Total Price"]) else ""
        })

    # Add summary information at the end (tax and grand total)
    rows.append({
        "Invoice Number": structured_data["Invoice Number"],
        "Date": structured_data["Date"],
        "Customer Name": structured_data["Customer Name"],
        "Customer Address": structured_data["Customer Address"],
        "Item Description": "Tax",
        "Quantity": "",
        "Unit Price": "",
        "Total Price": structured_data["Tax"]
    })
    rows.append({
        "Invoice Number": structured_data["Invoice Number"],
        "Date": structured_data["Date"],
        "Customer Name": structured_data["Customer Name"],
        "Customer Address": structured_data["Customer Address"],
        "Item Description": "Grand Total",
        "Quantity": "",
        "Unit Price": "",
        "Total Price": structured_data["Grand Total"]
    })
    
    df = pd.DataFrame(rows)
    return df

# Streamlit app
st.title("Multi-File Invoice PDF to Structured CSV Extractor")
st.write("Upload invoice PDF files containing images to extract text and download as a structured CSV file.")

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
                structured_data = structure_extracted_data(extracted_data)
                all_extracted_data.append(structured_data)
            st.success(f"OCR completed for {uploaded_file.name}.")
        else:
            st.warning(f"No images found in {uploaded_file.name}.")
    
    # Combine and convert the extracted data to CSV format
    if all_extracted_data:
        with st.spinner("Converting extracted data to structured CSV..."):
            structured_csv_data = pd.concat([convert_to_csv(data) for data in all_extracted_data], ignore_index=True)
        
        # Provide a download button for the CSV file
        st.write("Download CSV:")
        csv = structured_csv_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name='structured_invoice_data.csv',
            mime='text/csv',
        )
    else:
        st.warning("No text extracted from the uploaded files.")
