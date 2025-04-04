from groq import Groq
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

def process_text_with_groq(text):
   
    # Get the API key from the environment variable
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        raise ValueError("API key not found. Please set the 'GROQ_API_KEY' in the .env file.")

    prompt = f"""Please act as a legal advisor and review the following contract or terms and conditions {text}. I need you to perform a two-step analysis:
1. Document Summary and Overall Assessment:
    Provide a concise summary of the document, highlighting key points and general themes.
    Based on this summary, assess the document's favorability. Indicate if the contract appears generally favorable, risky, or in need of specific revisions to make it less risky.

2. Identification and Explanation of Risky Clauses:
    Identify any clauses or terms that may pose a risk to the signatory.
    For each risky clause, provide a simplified explanation, clarifying why it may be risky and suggesting what to consider or amend.
    Please format the clause titles in **bold** and display them in the following format:
    
    "Clause Title (Clause Number):"
    
    Do not include asterisks around any text."""



    client = Groq(
        api_key=api_key,  # Use the API key from the environment variable
    )

    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            response_format={"type": "text"},
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error processing with Groq API: {str(e)}"
