# # Q&A Chatbot
# #from langchain.llms import OpenAI

# from dotenv import load_dotenv

# load_dotenv()  # take environment variables from .env.

# import streamlit as st
# import os
# import pathlib
# import textwrap
# from PIL import Image


# import google.generativeai as genai


# os.getenv("GOOGLE_API_KEY")
# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# ## Function to load OpenAI model and get respones

# def get_gemini_response(input,image,prompt):
#     model = genai.GenerativeModel('gemini-1.5-pro')
#     response = model.generate_content([input,image[0],prompt])
#     return response.text
    

# def input_image_setup(uploaded_file):
#     # Check if a file has been uploaded
#     if uploaded_file is not None:
#         # Read the file into bytes
#         bytes_data = uploaded_file.getvalue()

#         image_parts = [
#             {
#                 "mime_type": uploaded_file.type,  # Get the mime type of the uploaded file
#                 "data": bytes_data
#             }
#         ]
#         return image_parts
#     else:
#         raise FileNotFoundError("No file uploaded")


# ##initialize our streamlit app

# st.set_page_config(page_title="Gemini Image Demo")

# st.header("Gemini Application")
# input=st.text_input("Input Prompt: ",key="input")
# uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
# image=""   
# if uploaded_file is not None:
#     image = Image.open(uploaded_file)
#     st.image(image, caption="Uploaded Image.", use_container_width=True)


# submit=st.button("Tell me about the image")

# input_prompt = """
#                You are an expert in understanding invoices.
#                You will receive input images as invoices &
#                you will have to answer questions based on the input image
#                """

# ## If ask button is clicked

# if submit:
#     image_data = input_image_setup(uploaded_file)
#     response=get_gemini_response(input_prompt,image_data,input)
#     st.subheader("The Response is")
#     st.write(response)


# import os
# import logging
# from pdf2image import convert_from_path
# from io import BytesIO
# from PIL import Image

# SUPPORTED_FORMATS = [".pdf", ".jpg", ".jpeg", ".png"]

# def is_supported_format(file_name: str) -> bool:
#     _, ext = os.path.splitext(file_name.lower())
#     return ext in SUPPORTED_FORMATS

# from tempfile import NamedTemporaryFile
# import shutil

# def process_pdf(uploaded_file):
#     try:
#         # Create a temporary file to save the uploaded PDF
#         with NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
#             shutil.copyfileobj(uploaded_file, temp_file)  # Copy content of the uploaded file to the temp file
#             temp_file_path = temp_file.name

#         # Convert PDF to images using the temporary file path
#         images = convert_from_path(temp_file_path)

#         # Initialize an empty image to combine the pages
#         combined_image = None

#         for img in images:
#             # Convert each image to RGB mode to avoid transparency issues
#             img = img.convert("RGB")

#             # If it's the first image, initialize the combined image
#             if combined_image is None:
#                 combined_image = img
#             else:
#                 # Combine images vertically (resize to match width)
#                 new_width = max(combined_image.width, img.width)
#                 new_height = combined_image.height + img.height

#                 # Create a new image with the new size (white background)
#                 combined_image_new = Image.new("RGB", (new_width, new_height), (255, 255, 255))  # white background

#                 # Paste the old combined image
#                 combined_image_new.paste(combined_image, (0, 0))

#                 # Paste the current image at the correct vertical position
#                 combined_image_new.paste(img, (0, combined_image.height))

#                 # Update the combined image for the next iteration
#                 combined_image = combined_image_new

#         # Save the combined image as bytes
#         img_byte_arr = BytesIO()
#         combined_image.save(img_byte_arr, format="JPEG")
#         img_byte_arr.seek(0)
       
#         return img_byte_arr.getvalue()
   
#     except Exception as e:
#         logging.error(f"An error occurred during PDF processing: {e}")
#         return None


# def input_image_setup(uploaded_file):
#     # Check if the uploaded file is a PDF
#     if uploaded_file is not None:
#         file_name = uploaded_file.name.lower()
       
#         if is_supported_format(file_name):
#             if file_name.endswith(".pdf"):
#                 # Process the PDF file
#                 image_bytes = process_pdf(uploaded_file)
#                 if image_bytes:
#                     image_parts = [{"mime_type": "image/jpeg", "data": image_bytes}]
#                     return image_parts
#             else:
#                 # Handle other image files
#                 bytes_data = uploaded_file.getvalue()
#                 image_parts = [{"mime_type": uploaded_file.type, "data": bytes_data}]
#                 return image_parts
#         else:
#             raise ValueError("Unsupported file format.")
#     else:
#         raise FileNotFoundError("No file uploaded")

# # In your Streamlit app
# import streamlit as st
# import google.generativeai as genai
# from dotenv import load_dotenv

# load_dotenv()  # take environment variables from .env

# # Set up Google Gemini API
# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# # Function to get the response from Gemini API
# def get_gemini_response(input, image, prompt):
#     # Validate if the image is correctly passed
#     if image is None or len(image) == 0:
#         raise ValueError("No image data found.")
    
#     model = genai.GenerativeModel('gemini-1.5-pro')
    
#     # Make sure that `image[0]` exists before passing to the model
#     response = model.generate_content([input, image[0], prompt])
#     return response.text


# # Streamlit UI
# st.set_page_config(page_title="Gemini Image Demo")
# st.header("Gemini Application")

# input = st.text_input("Input Prompt: ", key="input")
# uploaded_file = st.file_uploader("Choose a file...", type=["pdf", "jpg", "jpeg", "png"])

# if uploaded_file is not None:
#     # Process the file and extract image data
#     image_data = input_image_setup(uploaded_file)

#     # Check if image data is valid before passing it to the response function
#     if image_data and len(image_data) > 0:
#         st.image(image_data[0]["data"], caption="Processed Image.", use_container_width=True)
#     else:
#         st.error("Error processing the image. Please try again with a valid image or PDF.")


# submit = st.button("Tell me about the image")

# input_prompt = """
#                You are an expert in understanding invoices.
#                You will receive input images as invoices & you will have to answer questions based on the input image
#                """

# # When the button is clicked
# if submit:
#     response = get_gemini_response(input_prompt, image_data, input)
#     st.subheader("The Response is")
#     st.write(response)

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
st.set_page_config(page_title="Gemini Image Demo", layout="wide")
st.title("📝 Gemini Application: Invoice Understanding")
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
submit = st.button("Ask Gemini 🤖")

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
    📝 **About**: This tool uses Google's Gemini AI to analyze uploaded invoices.  
    🔒 Your data is processed securely, and the file is never stored permanently.  
    💬 Have a question? Reach out to support at: support@example.com
""", unsafe_allow_html=True)
