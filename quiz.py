import streamlit as st
import os
from dotenv import load_dotenv
import docx2txt
import PyPDF2

from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

# Load Google API key
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    st.error("Google API key not found in .env file.")
    st.stop()

# Function to extract text from uploaded files
def extract_text(file):
    if file.name.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file)
        return "\n".join([page.extract_text() or "" for page in reader.pages])
    elif file.name.endswith(".docx"):
        return docx2txt.process(file)
    elif file.name.endswith(".txt"):
        return file.read().decode("utf-8")
    else:
        return ""

# Prompt template: only questions, numbered format
QUESTION_PROMPT = PromptTemplate(
    input_variables=["content", "num"],
    template="""
You are a quiz question generator.

Based on the following content, generate exactly {num} multiple-choice quiz questions. 
Only generate the questions — no answer options or answers.

Strictly use the following format:
Q1. <question>
Q2. <question>
...
Q{num}. <question>

Content:
\"\"\"{content}\"\"\"
"""
)

# Streamlit UI
st.title("📘 AI Quiz Question Generator (Questions Only)")
uploaded_file = st.file_uploader("Upload a document (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])
num_questions = st.number_input("Number of Questions", min_value=1, max_value=50, value=5)

if uploaded_file and st.button("Generate Questions"):
    with st.spinner("Extracting text from file..."):
        content = extract_text(uploaded_file)

    if not content.strip():
        st.error("No readable text found in the file.")
    else:
        with st.spinner("Generating questions using Gemini..."):
            llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-pro",
                temperature=0.3,
                google_api_key=GOOGLE_API_KEY
            )

            prompt = QUESTION_PROMPT.format(content=content[:8000], num=num_questions)
            response = llm.invoke(prompt)

            # Extract .content from Gemini's response safely
            result_text = getattr(response, 'content', str(response)).strip()

            if not result_text:
                st.error("No questions generated. Please try again.")
            else:
                st.markdown("### 🧠 Generated Questions:")
                for line in result_text.split("\n"):
                    if line.strip().startswith("Q"):
                        st.markdown(f"- {line.strip()}")
