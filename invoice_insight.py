import os
import logging
from pdf2image import convert_from_path
from io import BytesIO
from PIL import Image
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import tempfile

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Constants
SUPPORTED_FORMATS = [".pdf", ".jpg", ".jpeg", ".png"]

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Function to check if file format is supported
def is_supported_format(file_name: str) -> bool:
    _, ext = os.path.splitext(file_name.lower())
    return ext in SUPPORTED_FORMATS

# Convert PDF to a combined image
def process_pdf(uploaded_file):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(uploaded_file.getvalue())
            temp_file_path = temp_file.name
            logging.debug(f"Temporary PDF saved at: {temp_file_path}")

        images = convert_from_path(temp_file_path)
        combined_image = None

        for img in images:
            img = img.convert("RGB")
            if combined_image is None:
                combined_image = img
            else:
                new_width = max(combined_image.width, img.width)
                new_height = combined_image.height + img.height
                new_combined = Image.new("RGB", (new_width, new_height), (255, 255, 255))
                new_combined.paste(combined_image, (0, 0))
                new_combined.paste(img, (0, combined_image.height))
                combined_image = new_combined

        img_byte_arr = BytesIO()
        combined_image.save(img_byte_arr, format="JPEG")
        img_byte_arr.seek(0)
        return img_byte_arr.getvalue()

    except Exception as e:
        logging.error(f"Error processing PDF: {e}")
        return None

# Extract image bytes from uploaded file
def input_image_setup(uploaded_file):
    file_name = uploaded_file.name.lower()
    logging.debug(f"File uploaded: {file_name}")

    if not is_supported_format(file_name):
        raise ValueError("Unsupported file format.")

    if file_name.endswith(".pdf"):
        image_bytes = process_pdf(uploaded_file)
        if image_bytes:
            return [{"mime_type": "image/jpeg", "data": image_bytes}]
        else:
            raise ValueError("Failed to process PDF.")
    else:
        bytes_data = uploaded_file.getvalue()
        return [{"mime_type": uploaded_file.type, "data": bytes_data}]

# Query Gemini API
def get_gemini_response(input_text, image_data, prompt_text):
    if not image_data:
        raise ValueError("No image data found.")
#gemini-2.5-flash-lite-preview-06-17
    model = genai.GenerativeModel('gemini-1.5-flash-8b')
    try:
        response = model.generate_content([input_text, image_data[0], prompt_text])
        return response.text
    except Exception as e:
        logging.error(f"Gemini API error: {e}")
        raise

# Streamlit UI
st.set_page_config(page_title="Invoice GPT - by Prakhar Srivastava", layout="wide")
st.title("📝 GEN-AI INVOICE EXTRACTOR")
st.markdown("""
This app allows you to upload a document (PDF or image) and ask questions based on its content.  
Simply upload your file, and enter a question in the text box below.
""")

# Upload section
st.subheader("1. Upload Your File 📁")
uploaded_file = st.file_uploader("Choose a file...", type=["pdf", "jpg", "jpeg", "png"], label_visibility="collapsed")

if uploaded_file:
    if "image_data" not in st.session_state or uploaded_file.name != st.session_state.get("file_name"):
        try:
            st.session_state.image_data = input_image_setup(uploaded_file)
            st.session_state.file_name = uploaded_file.name
            logging.debug("Image data processed and cached.")
        except Exception as e:
            logging.error(f"File processing error: {e}")
            st.error("Error processing the file. Please try again with a valid image or PDF.")
            st.stop()

    image_data = st.session_state.image_data
    st.write(f"**File uploaded**: {uploaded_file.name}")
    if image_data and len(image_data) > 0:
        st.image(image_data[0]["data"], caption="Processed Image Preview", use_container_width=True)

# Prompt section
st.subheader("2. Enter Your Question 🧐")
input_prompt = st.text_input("Ask a question about the document:", key="input", help="Ask about details like invoice number, total, items, etc.")

# Submit button
submit = st.button("Ask Invoice-Gpt 🤖")

# Response section
if submit:
    if uploaded_file and input_prompt:
        with st.spinner("Processing..."):
            try:
                if "response_text" not in st.session_state or st.session_state.get("last_prompt") != input_prompt:
                    full_prompt = """
You are an expert in understanding invoices. You will receive input images of invoices, and your task is to extract key details and return them in a structured format as JSON with the following fields:

- Invoice Number
- Invoice Date
- Vendor Name
- Total Amount
- Line Items (if any), including:
    - Item Description
    - Item Quantity
    - Item Price
- Any additional relevant details (e.g., taxes, shipping, etc.)

Please ensure that:
- If the image does not contain an invoice or is not readable, return the message: "Please upload a valid invoice. The file uploaded is not an invoice."
- If any of the fields are missing or unreadable, return them as `null` or `N/A`.
- Format the response strictly as JSON:

Example:

{
    "Invoice Number": "INV123456",
    "Invoice Date": "2025-01-28",
    "Vendor Name": "ABC Corp",
    "Total Amount": 150.75,
    "Line Items": [
        {"Description": "Item A", "Quantity": 2, "Price": 50},
        {"Description": "Item B", "Quantity": 1, "Price": 100.75}
    ]
}
                    """
                    response_text = get_gemini_response(input_prompt, st.session_state.image_data, full_prompt)
                    st.session_state.response_text = response_text
                    st.session_state.last_prompt = input_prompt
                else:
                    response_text = st.session_state.response_text

                st.subheader("Gemini's Response 🤖")
                st.code(response_text, language='json')
            except Exception as e:
                if "429" in str(e):
                    st.error("⚠️ Rate limit hit: You’ve exceeded your quota. Please wait a bit or check your billing.")
                else:
                    st.error(f"❌ Error: {str(e)}")
    else:
        st.warning("Please upload a file and enter a question to proceed.")

# Footer
st.markdown("""
---
📝 **About**: GEN-AI Tool to make analysis over the invoices  
🔒 Your data is processed securely, and the file is never stored permanently.  
🤖 Model used: `gemini-2.5-flash-lite-preview-06-17`  
📧 Contact: prakharsrivastava337@gmail.com
""", unsafe_allow_html=True)
