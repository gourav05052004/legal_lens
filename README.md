# Legal Lens 🔍

**Legal Lens** is an AI-powered legal assistant designed to demystify complex contracts and legal documents. By uploading a PDF file, users can quickly receive a plain-English summary of the document and an organized breakdown of potentially risky clauses.

---

## 🎯 What Problem Does It Solve?
Legal documents, terms of service, and contracts are often filled with dense jargon that is difficult for the average person to understand. Hiring a lawyer for every single contract isn't always feasible or cost-effective. 

**Legal Lens** bridges this gap by acting as your personal legal advisor. It simplifies the language, gives you an overall assessment of the document's favorability, and explicitly highlights any clauses that might pose a risk to you—explaining *why* they are risky and *what* you should consider amending.

---

## 📸 Screenshots

![Main Interface UI](assets/home.png)
*The main upload interface and side-by-side analysis view.*

**Analysis Results**
Here is a breakdown of the AI-driven analysis of risky clauses:

![Analysis Part 1](assets/result_01.png)
![Analysis Part 2](assets/result_02.png)
![Analysis Part 3](assets/result_03.png)
![Analysis Part 4](assets/result_04.png)

---

## 🛠️ Critical Decisions & Architecture

1. **Groq API & Llama 3.1**: 
   - **Decision**: We utilized the Groq API paired with the `llama-3.1-8b-instant` model.
   - **Reasoning**: Groq's LPU architecture provides ultra-fast inference speeds, meaning users don't have to wait minutes for large documents to be analyzed. Llama 3.1 was chosen for its excellent reasoning and instruction-following capabilities, making it ideal for legal review.

2. **Streamlit Frontend**:
   - **Decision**: Built the entire frontend using Streamlit.
   - **Reasoning**: Streamlit allowed for rapid UI development while keeping the codebase entirely in Python. We implemented a custom professional theme (`config.toml`) with navy and slate accents to invoke trust and reliability. 

3. **Side-by-Side UI Layout**:
   - **Decision**: Used an embedded HTML `iframe` with base64 encoding to display the PDF inline.
   - **Reasoning**: Instead of forcing the user to download the PDF or switch windows, the side-by-side layout allows users to read the original document on the left while simultaneously reviewing the AI's risk assessment on the right.

4. **pdfplumber for Text Extraction**:
   - **Decision**: Relied on `pdfplumber` instead of simpler tools like `PyPDF2`.
   - **Reasoning**: Legal contracts often have complex layouts, tables, and specific formatting. `pdfplumber` offers superior, robust extraction that ensures the AI receives clean, high-quality text for analysis.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- A [Groq API Key](https://console.groq.com/)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/legal-lens.git
   cd legal-lens/Code
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Environment Variables:**
   Create a `.env` file in the root directory and add your Groq API key:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

4. **Run the Application:**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser:**
   Navigate to `http://localhost:8501` to use Legal Lens!
