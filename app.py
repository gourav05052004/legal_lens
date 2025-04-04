import streamlit as st
from text_extractor import extract_text_from_pdf  # Import the text extraction function
from AI import process_text_with_groq  # Import the AI function for analysis
from io import BytesIO

# Streamlit app layout
st.title("Legal Lens 🔍")

# Upload PDF file
uploaded_file = st.file_uploader("Upload a PDF file to highlight the concering points", type=["pdf"])

if uploaded_file:
    # Display the uploaded PDF file using Streamlit's built-in PDF viewer
    st.subheader("Uploaded PDF:")
    st.download_button(label="Download PDF", data=uploaded_file, file_name="uploaded_document.pdf", mime="application/pdf")
    
    # Extract text from the uploaded PDF using BytesIO (in-memory)
    extracted_text = extract_text_from_pdf(BytesIO(uploaded_file.read()))

    # Check if text extraction was successful
    if extracted_text:
        with st.spinner("Processing document..."):
            analysis_result = process_text_with_groq(extracted_text)

        # Display the result from the Groq API analysis
        if "Error" in analysis_result:
            st.error(analysis_result)  # Show error message if there was an issue
        else:
            st.subheader("Analysis Result:")
            # Display the result using markdown for better formatting
            st.markdown(analysis_result)
    else:
        st.error("Failed to extract text from the PDF. Please try another file.")
