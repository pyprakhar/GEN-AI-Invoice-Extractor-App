
import os
import logging
from pdf2image import convert_from_path
from io import BytesIO
from PIL import Image
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
from tempfile import NamedTemporaryFile
import shutil

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Constants
SUPPORTED_FORMATS = [".pdf", ".jpg", ".jpeg", ".png"]

# Function to check if file format is supported
def is_supported_format(file_name: str) -> bool:
    _, ext = os.path.splitext(file_name.lower())
    return ext in SUPPORTED_FORMATS

# Process PDF function to convert pages to images
def process_pdf(uploaded_file):
    try:
        with NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            shutil.copyfileobj(uploaded_file, temp_file)
            temp_file_path = temp_file.name

        # Convert PDF to images
        images = convert_from_path(temp_file_path)
        combined_image = None

        # Combine images vertically
        for img in images:
            img = img.convert("RGB")
            if combined_image is None:
                combined_image = img
            else:
                new_width = max(combined_image.width, img.width)
                new_height = combined_image.height + img.height
                combined_image_new = Image.new("RGB", (new_width, new_height), (255, 255, 255))
                combined_image_new.paste(combined_image, (0, 0))
                combined_image_new.paste(img, (0, combined_image.height))
                combined_image = combined_image_new

        # Return combined image as bytes
        img_byte_arr = BytesIO()
        combined_image.save(img_byte_arr, format="JPEG")
        img_byte_arr.seek(0)
        return img_byte_arr.getvalue()

    except Exception as e:
        logging.error(f"An error occurred during PDF processing: {e}")
        return None

# Function to handle uploaded image and extract bytes
def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        file_name = uploaded_file.name.lower()
        if is_supported_format(file_name):
            if file_name.endswith(".pdf"):
                image_bytes = process_pdf(uploaded_file)
                if image_bytes:
                    return [{"mime_type": "image/jpeg", "data": image_bytes}]
            else:
                bytes_data = uploaded_file.getvalue()
                return [{"mime_type": uploaded_file.type, "data": bytes_data}]
        else:
            raise ValueError("Unsupported file format.")
    else:
        raise FileNotFoundError("No file uploaded")

# Function to get the response from Gemini API
def get_gemini_response(input, image, prompt):
    if image is None or len(image) == 0:
        raise ValueError("No image data found.")
    
    model = genai.GenerativeModel('gemini-1.5-pro')
    response = model.generate_content([input, image[0], prompt])
    return response.text

# Streamlit UI Setup
st.set_page_config(page_title="Invoice GPT- by Prakhar Srivastava", layout="wide")
st.title("📝 GEN-AI INVOICE EXTRACTOR")
st.markdown("""
    This app allows you to upload a document (PDF or image) and ask questions based on its content.
    Simply upload your file, and enter a question in the text box below.
""")

# File upload section
st.subheader("1. Upload Your File 📁")
uploaded_file = st.file_uploader("Choose a file...", type=["pdf", "jpg", "jpeg", "png"], label_visibility="collapsed")

# Display a preview of the uploaded image if available
if uploaded_file is not None:
    file_name = uploaded_file.name
    st.write(f"**File uploaded**: {file_name}")
    
    # Process image
    image_data = input_image_setup(uploaded_file)
    
    # Display processed image preview
    if image_data and len(image_data) > 0:
        st.image(image_data[0]["data"], caption="Processed Image Preview", use_container_width=True)
    else:
        st.error("Error processing the image. Please try again with a valid image or PDF.")

# User input section for prompt
st.subheader("2. Enter Your Question 🧐")
input_prompt = st.text_input("Ask a question about the document:", key="input", help="Ask about details like invoice number, total, items, etc.")

# Button to submit the question
submit = st.button("Ask Invoice-Gpt 🤖")

# Response section
if submit:
    if uploaded_file and input_prompt:
        with st.spinner("Processing..."):
            try:
                response = get_gemini_response(input_prompt, image_data, """
                    You are an expert in understanding invoices.
                    You will receive input images as invoices & you will have to answer questions based on the input image.
                """)
                st.subheader("Gemini's Response 🤖")
                st.write(response)
            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.warning("Please upload a file and enter a question to proceed.")

# Footer
st.markdown("""
    ---  
    📝 **About**: GEN-AI Tool to make analysis over the inoices 
    🔒 Your data is processed securely, and the file is never stored permanently.  
    💬 Have a question? Reach out to support at: prakharsrivastava337@gmail.com
""", unsafe_allow_html=True)
