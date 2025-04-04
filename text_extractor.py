import pdfplumber

def extract_text_from_pdf(file_path):
    try:
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        return f"Error extracting text: {str(e)}"

# # Extract text from the PDF
# file_path = r"D:\Legal_Lens\Sample(T&c)\Health Companion-Health Insurance Plan_GEN617.pdf"
# extracted_text = extract_text_from_pdf(file_path)

# # Save the extracted text to a text file
# if extracted_text:
#     output_file_path = "extracted_text.txt"
#     with open(output_file_path, "w", encoding="utf-8") as file:
#         file.write(extracted_text)
#     print(f"Text has been saved to {output_file_path}")
# else:
#     print("No text was extracted.")
