import streamlit as st
from text_extractor import extract_text_from_pdf
from AI import process_text_with_groq
from io import BytesIO
import pdfplumber

def display_pdf(file_bytes):
    try:
        with pdfplumber.open(BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                im = page.to_image(resolution=100)
                st.image(im.original, use_container_width=True)
    except Exception as e:
        st.error(f"Error displaying PDF: {e}")

@st.cache_data(ttl=3600, show_spinner=False)
def get_extracted_text(file_bytes):
    text, method = extract_text_from_pdf(BytesIO(file_bytes))
    return text, method

@st.cache_data(ttl=3600, show_spinner=False)
def get_ai_analysis(text):
    return process_text_with_groq(text)

# 1. Page Configuration
st.set_page_config(page_title="Legal Lens", page_icon="🔍", layout="wide")

# 2. Sidebar Layout
with st.sidebar:
    st.title("Legal Lens 🔍")
    st.info("Your AI-powered legal assistant.")
    st.info("Your documents are not stored. They are processed entirely in memory.")
    
    st.markdown("### How it works")
    st.markdown(
        "1. **Upload** a legal document or contract (PDF).\n"
        "2. **Extract** the text content.\n"
        "3. **Analyze** with AI to find risky clauses and get a plain-English summary."
    )
    
    import os
    if os.path.exists("offerletter.pdf"):
        with open("offerletter.pdf", "rb") as f:
            st.download_button(
                label="Try with a sample contract",
                data=f,
                file_name="sample_offerletter.pdf",
                mime="application/pdf"
            )
            
    st.markdown("---")

# 3. Main Content Organization
st.title("Legal Document Analysis 📄")
st.markdown("Upload your contract below. Our AI will simplify the legal jargon and highlight potential risks.")
st.warning("⚠️ **Disclaimer:** This analysis is for educational and informational purposes only. It does not constitute legal advice. Please consult a qualified legal professional before making any decisions based on this report.")

uploaded_file = st.file_uploader("Upload a PDF document to begin", type=["pdf"], help="Only PDF files are supported.")

if uploaded_file:
    # Reset stream position in case Streamlit has re-run and the stream was already consumed
    uploaded_file.seek(0)
    # Read file bytes once for both extraction and display
    file_bytes = uploaded_file.read()
    
    if not file_bytes:
        st.error("The uploaded file appears to be empty. Please upload a valid PDF document.")
        st.stop()
        
    # Use session_state to prevent re-running analysis on widget interactions (like download button)
    file_key = f"{uploaded_file.name}_{uploaded_file.size}"
    if "current_file" not in st.session_state or st.session_state.current_file != file_key:
        st.session_state.current_file = file_key
        st.session_state.extracted_text = None
        st.session_state.extraction_method = None
        st.session_state.analysis_result = None
    
    # 4. Results Layout with Tabs
    tab1, tab2 = st.tabs(["AI Analysis", "Document Preview"])
    
    with tab1:
        st.subheader("AI Analysis")
        
        # Extract text
        progress_bar = st.progress(10, text="Extracting text from PDF...")
        
        if st.session_state.extracted_text is None:
            extracted_text, extraction_method = get_extracted_text(file_bytes)
            st.session_state.extracted_text = extracted_text
            st.session_state.extraction_method = extraction_method
        else:
            extracted_text = st.session_state.extracted_text
            extraction_method = st.session_state.extraction_method
        
        if extracted_text and extraction_method != "error" and extraction_method != "none":
            if extraction_method == "ocr":
                st.info("📷 This appears to be a scanned document. Text was extracted using OCR (Optical Character Recognition).")
            elif extraction_method == "fitz":
                st.info("📄 Text was extracted using PyMuPDF.")
            
            with st.expander("View Extracted Text"):
                st.text(extracted_text)
                
            # Check if text extraction was somewhat successful
            if st.session_state.analysis_result is None:
                progress_bar.progress(50, text="AI is reviewing the document...")
                analysis_result = get_ai_analysis(extracted_text)
                st.session_state.analysis_result = analysis_result
                progress_bar.progress(100, text="Analysis Complete!")
            else:
                progress_bar.progress(100, text="Analysis Complete!")
                analysis_result = st.session_state.analysis_result
            
            # 5. Enhanced Status States
            if "Error processing" in analysis_result:
                st.error("There was an error communicating with the AI service.")
                st.error(analysis_result)
            else:
                st.success("Analysis Complete!")
                
                # Check for RISK_LEVEL badge
                lines = analysis_result.split('\n')
                first_line = lines[0]
                if "RISK_LEVEL:" in first_line:
                    risk_level = first_line.replace("RISK_LEVEL:", "").strip()
                    # Remove the first line from the result
                    analysis_result = '\n'.join(lines[1:])
                    
                    if "High" in risk_level:
                        st.error(f"**Overall Risk Level:** {risk_level}")
                    elif "Medium" in risk_level:
                        st.warning(f"**Overall Risk Level:** {risk_level}")
                    else:
                        st.success(f"**Overall Risk Level:** {risk_level}")
                        
                # Download report
                def create_pdf(text):
                    from fpdf import FPDF
                    
                    class PDFReport(FPDF):
                        def header(self):
                            self.set_font("helvetica", "B", 24)
                            self.cell(0, 10, "Legal Lens", align="L")
                            self.ln(12)
                            self.set_x(self.l_margin)
                            
                            # Draw the two horizontal lines
                            y = self.get_y()
                            self.set_line_width(0.5)
                            self.line(10, y, 200, y)
                            self.set_line_width(0.2)
                            self.line(10, y + 1.5, 200, y + 1.5)
                            self.ln(5)
                            self.set_x(self.l_margin)
                            
                            # Disclaimer warning in red
                            self.set_text_color(220, 0, 0)
                            self.set_font("helvetica", "BI", 8)
                            self.set_x(self.l_margin)
                            self.multi_cell(w=self.epw, h=4, text="Disclaimer: This analysis is for educational and informational purposes only. It does not constitute legal advice. Please consult a qualified legal professional before making any decisions based on this report.")
                            self.set_text_color(0, 0, 0)
                            self.ln(4)
                            self.set_x(self.l_margin)
                            
                        def footer(self):
                            self.set_y(-15)
                            self.set_font("helvetica", "I", 8)
                            self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

                    pdf = PDFReport()
                    pdf.add_page()
                    pdf.set_font("helvetica", size=11)
                    
                    # Replace common smart quotes to standard quotes to avoid encoding issues
                    replacements = {
                        "“": '"', "”": '"', "’": "'", "‘": "'", "—": "-", "–": "-", "…": "..."
                    }
                    for k, v in replacements.items():
                        text = text.replace(k, v)
                    sanitized_text = text.encode('latin-1', 'replace').decode('latin-1')
                    
                    for line in sanitized_text.split('\n'):
                        pdf.set_x(pdf.l_margin) # Always reset X before writing
                        if "Document Summary and Overall Assessment:" in line:
                            pdf.set_text_color(0, 128, 0) # Green
                            pdf.set_font("helvetica", "B", 12)
                            pdf.set_x(pdf.l_margin)
                            pdf.multi_cell(w=pdf.epw, h=7, text=line)
                            pdf.set_text_color(0, 0, 0) # Reset to black
                            pdf.set_font("helvetica", "", 11)
                        elif "Identification and Explanation of Risky Clauses:" in line:
                            pdf.set_text_color(220, 0, 0) # Red
                            pdf.set_font("helvetica", "B", 12)
                            pdf.set_x(pdf.l_margin)
                            pdf.multi_cell(w=pdf.epw, h=7, text=line)
                            pdf.set_text_color(0, 0, 0) # Reset to black
                            pdf.set_font("helvetica", "", 11)
                        else:
                            # Basic bold parsing for clause titles
                            if line.strip().startswith("**") and line.strip().endswith("**"):
                                pdf.set_font("helvetica", "B", 11)
                                pdf.set_x(pdf.l_margin)
                                pdf.multi_cell(w=pdf.epw, h=7, text=line.replace("**", ""))
                                pdf.set_font("helvetica", "", 11)
                            else:
                                pdf.set_x(pdf.l_margin)
                                pdf.multi_cell(w=pdf.epw, h=7, text=line)
                                
                    return bytes(pdf.output())
                
                pdf_bytes = create_pdf(analysis_result)
                
                st.download_button(
                    label="Download Report (.pdf)",
                    data=pdf_bytes,
                    file_name="legal_analysis_report.pdf",
                    mime="application/pdf"
                )
                
                # Display the result using markdown
                st.markdown(analysis_result)
        else:
            progress_bar.empty()
            if extraction_method == "error":
                st.error(f"An error occurred during text extraction: {extracted_text}")
            else:
                st.error("Failed to extract text from the PDF. The file may be corrupted, password-protected, or contain only images that could not be read.")
            
    with tab2:
        st.subheader("Document Preview")
        display_pdf(file_bytes)
        st.download_button(
            label="Download Original PDF", 
            data=file_bytes, 
            file_name=uploaded_file.name, 
            mime="application/pdf"
        )
