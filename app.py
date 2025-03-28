import streamlit as st
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import google.generativeai as genai

# Configure Google Gemini API
genai.configure(api_key="your_api_key")

# Function to extract text & formulas from PDF
def extract_text_and_formulas_from_pdf(uploaded_file):
    text = ""
    formulas = []

    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page in doc:
            # Extract standard text
            text += page.get_text("text") + "\n"

            # Extract formulas using image processing
            for img_index, img in enumerate(page.get_images(full=True)):
                xref = img[0]
                base_image = doc.extract_image(xref)
                img_data = base_image["image"]
                img_pil = Image.open(io.BytesIO(img_data))

                # Apply OCR to extract equation text
                extracted_formula = pytesseract.image_to_string(img_pil, config="--psm 6")
                formulas.append(extracted_formula.strip())

    return text, formulas

# Function to extract insights using AI
def extract_insights_with_gemini(text, formulas):
    model = genai.GenerativeModel("gemini-1.5-pro-latest")

    prompt = f"""
    Extract the following key details from this research paper:
    - Title of Paper
    - Year of Publication
    - Journal Name
    - Objective
    - Dataset Used
    - Preprocessing Techniques Used
    - Algorithm Used
    - Performance Metrics Used
    - Advantages
    - Limitations
    - Future Work

    Here is the research paper content:
    {text}

    Additionally, format the extracted mathematical formulas:
    {formulas}
    """

    response = model.generate_content(prompt)
    return response.text

# Streamlit UI Configuration
st.set_page_config(page_title="AI Research Paper Reviewer", page_icon="📄", layout="wide")

# Sidebar - Project Information
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/2/2d/Artificial_Intelligence_%26_AI_%26_Machine_Learning_-_30212411048.jpg", use_container_width=True)

    st.markdown("### 🔍 About This Project")
    st.info("This app extracts key insights from research papers and includes **mathematical formulas**.")

    st.markdown("### 🔹 Why This Project Matters?")
    st.write("📌 **Researchers often spend hours reading papers** to extract key details. This app automates that process, making research faster and more efficient.")
    st.markdown("### 💡 How It Works?")
    
    st.write("""
    1️⃣ **Upload a research paper (PDF).**  
    2️⃣ **AI processes the document & extracts insights** (Title, Objective, Methods, Results, etc.).  
    3️⃣ **Instantly review & download key details.**  
    """)

    st.markdown("### 🚀 Key Features")
    st.write("""
    - 📄 **AI-powered research paper reviewer**  
    - ⏳ **Saves time** by extracting key insights instantly  
    - 🔬 **Summarizes methodology, algorithms & findings**  
    - 🔢 **Extracts Mathematical Formulas** for research papers with equations  
    - 📂 **Supports multiple research domains**  
    - 💾 **Download extracted insights for easy reference**  
    """)

# Main Page Title
st.markdown('<h1 style="text-align:center;">📄 AI-Powered Research Paper Reviewer</h1>', unsafe_allow_html=True)
st.write("🚀 **Upload a research paper (PDF) and extract key insights, including formulas.**")

# File Upload Section
uploaded_file = st.file_uploader("📤 Upload a Research Paper (PDF)", type="pdf")

if uploaded_file is not None:
    st.success(f"✅ File uploaded: {uploaded_file.name}")

    # Extract text & formulas from PDF
    with st.spinner("📃 Extracting text and formulas from PDF... Please wait."):
        pdf_text, extracted_formulas = extract_text_and_formulas_from_pdf(uploaded_file)

    # Extract insights using AI
    with st.spinner("🤖 AI is analyzing the document..."):
        insights = extract_insights_with_gemini(pdf_text, extracted_formulas)

    # Display extracted insights
    st.markdown("### 📌 Extracted Paper Insights")

    # Display structured insights
    for section in insights.split("\n"):
        if section.strip():
            st.markdown(f'<div style="background-color:white;padding:15px;border-radius:10px;box-shadow:2px 2px 10px rgba(0,0,0,0.1);margin-bottom:10px;">{section}</div>', unsafe_allow_html=True)

    # Display extracted mathematical formulas
    if extracted_formulas:
        st.markdown("### 📐 Extracted Mathematical Formulas")
        for formula in extracted_formulas:
            st.code(formula, language="latex")

    # Download extracted insights as a text file
    st.download_button(label="📥 Download Extracted Insights", data=insights, file_name="paper_insights.txt", mime="text/plain")
