import streamlit as st
import base64
from text_extractor import extract_text_from_pdf
from AI import process_text_with_groq
from io import BytesIO

# 1. Page Configuration
st.set_page_config(page_title="Legal Lens", page_icon="🔍", layout="wide")

# Helper function to display PDF inline
def display_pdf(file_bytes):
    base64_pdf = base64.b64encode(file_bytes).decode('utf-8')
    # Embedding PDF in HTML
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# 2. Sidebar Layout
with st.sidebar:
    st.title("Legal Lens 🔍")
    st.info("Your AI-powered legal assistant.")
    st.markdown("### How it works")
    st.markdown(
        "1. **Upload** a legal document or contract (PDF).\n"
        "2. **Extract** the text content.\n"
        "3. **Analyze** with AI to find risky clauses and get a plain-English summary."
    )
    st.markdown("---")
    # st.markdown("Powered by [Groq](https://groq.com) and Llama 3.1.")

# 3. Main Content Organization
st.title("Legal Document Analysis 📄")
st.markdown("Upload your contract below. Our AI will simplify the legal jargon and highlight potential risks.")

uploaded_file = st.file_uploader("Upload a PDF document to begin", type=["pdf"], help="Only PDF files are supported.")

if uploaded_file:
    # Read file bytes once for both extraction and display
    file_bytes = uploaded_file.read()
    
    # 4. Results Layout with Columns
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.subheader("Document Preview")
        # Display the PDF
        display_pdf(file_bytes)
        # Still provide a download button just in case
        st.download_button(
            label="Download Original PDF", 
            data=file_bytes, 
            file_name=uploaded_file.name, 
            mime="application/pdf"
        )
        
    with col2:
        st.subheader("AI Analysis")
        
        # Extract text
        with st.spinner("Extracting text from PDF..."):
            extracted_text = extract_text_from_pdf(BytesIO(file_bytes))
            
        if extracted_text:
            with st.expander("View Extracted Text"):
                st.text(extracted_text)
                
            # Check if text extraction was somewhat successful
            with st.spinner("AI is reviewing the document..."):
                analysis_result = process_text_with_groq(extracted_text)
                
            # 5. Enhanced Status States
            if "Error processing" in analysis_result:
                st.error("There was an error communicating with the AI service.")
                st.error(analysis_result)
            else:
                st.success("Analysis Complete!")
                # Display the result using markdown
                st.markdown(analysis_result)
        else:
            st.error("Failed to extract text from the PDF. The file might be an image-only scan or corrupted.")
