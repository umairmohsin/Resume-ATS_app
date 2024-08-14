from dotenv import load_dotenv

import base64
import streamlit as st
import os
import io
from PIL import Image 
import pdf2image
import google.generativeai as genai

# Streamlit App
st.set_page_config(page_title="ATS Resume Expert")
st.sidebar.header("Configuration")

# Add a text box in the sidebar for the API key
api_key = st.sidebar.text_input("Enter your Google API Key", type="password")

# Load the API key and configure the Generative AI model if key is provided
if api_key:
    os.environ["GOOGLE_API_KEY"] = api_key
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

st.header("ATS Tracking System")
input_text = st.text_area("Job Description", key="input")
uploaded_file = st.file_uploader("Upload your Resume(PDF)...", type=["pdf"])

def get_gemi_response(input_text, pdf_content, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input_text, pdf_content[0], prompt])
    return response.text

def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        # Convert pdf to image
        images = pdf2image.convert_from_bytes(uploaded_file.read())
        first_page = images[0]
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        pdf_parts = [
            {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode()
            }
        ]
        return pdf_parts
    else:
        raise FileNotFoundError("No File Uploaded")

if uploaded_file is not None:
    st.write("PDF Uploaded Successfully")
    
    submit1 = st.button("Tell me about the Resume")
    submit2 = st.button("Percentage Match %")

    input_prompt1 = """
    You are an experienced Technical Recruiter and Headhunter for candidates, your task is to review the provided resume against the job description. 
    Please share your professional evaluation on whether the candidate's profile aligns with the role. 
    Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
    """

    input_prompt2 = """
    You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality. 
    Your task is to evaluate the resume against the provided job description. Give me the percentage of match if the resume matches
    the job description. First the output should come as percentage and then keywords missing and last final thoughts.
    """

    if submit1:
        if uploaded_file is not None:
            pdf_content = input_pdf_setup(uploaded_file)
            response = get_gemi_response(input_prompt1, pdf_content, input_text)
            st.subheader("The Response is:")
            st.write(response)
        else:
            st.write("Please upload the Resume")

    elif submit2:
        if uploaded_file is not None:
            pdf_content = input_pdf_setup(uploaded_file)
            response = get_gemi_response(input_prompt2, pdf_content, input_text)
            st.subheader("The Response is:")
            st.write(response)
        else:
            st.write("Please upload the Resume")
