from flask import Flask, render_template, request
from dotenv import load_dotenv

load_dotenv()
import base64
import os
import io
from PIL import Image 
import pdf2image
import google.generativeai as genai
import streamlit as st

app = Flask(__name__)

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input, pdf_content, prompt):
    model = genai.GenerativeModel('gemini-pro-vision')
    response = model.generate_content([input, pdf_content[0], prompt])
    return response.text

def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        images = pdf2image.convert_from_bytes(uploaded_file.read())
        first_page = images[0]
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
        raise FileNotFoundError("No file uploaded")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process_resume', methods=['POST'])
def process_resume():
    input_text = request.form.get('input_text')
    uploaded_file = request.files['resume']

    if 'submit1' in request.form:
        prompt = """
            You are an experienced Technical Human Resource Manager, your task is to review the provided resume against the job description.
            Please share your professional evaluation on whether the candidate's profile aligns with the role.
            Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
        """
    elif 'submit3' in request.form:
        prompt = """
            You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality,
            your task is to evaluate the resume against the provided job description. Give me the percentage match if the resume matches
            the job description. First, the output should come as a percentage, then keywords missing, and last final thoughts.
        """
    else:
        return "Invalid form submission"

    if uploaded_file:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(prompt, pdf_content, input_text)
        return response
    else:
        return "Please upload the resume"

if __name__ == '__main__':
    app.run(debug=True)
