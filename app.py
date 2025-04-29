# app.py

import streamlit as st
from dotenv import load_dotenv
import os
import tempfile
import json

# LangChain modules
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    TextLoader, CSVLoader, PyPDFLoader, UnstructuredWordDocumentLoader,
    UnstructuredMarkdownLoader
)

# Load environment variables (e.g., API keys)
load_dotenv()

# Initialize model and parser
model = ChatGoogleGenerativeAI(model="gemini-1.5-pro")
parser = StrOutputParser()

# Streamlit page config
st.set_page_config(page_title="📄 AI File Summarizer", layout="centered")
st.title("📄 AI File Summarizer with Gemini")

# File upload
uploaded_file = st.file_uploader(
    "📂 Upload a file (txt, csv, md, json, pdf, docx)",
    type=["txt", "csv", "md", "json", "pdf", "docx"]
)

# Prompt input
custom_prompt = st.text_area(
    "✍️ Enter your prompt",
    value="Write a summary for the following content:\n\n{poem}",
    height=100
)

# Function to load and parse file content
def load_file(path, extension):
    try:
        if extension == ".txt":
            return TextLoader(path, encoding="utf-8").load()
        elif extension == ".csv":
            return CSVLoader(path).load()
        elif extension == ".pdf":
            return PyPDFLoader(path).load()
        elif extension == ".docx":
            return UnstructuredWordDocumentLoader(path).load()
        elif extension == ".md":
            return UnstructuredMarkdownLoader(path).load()
        elif extension == ".json":
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                content = json.dumps(data, indent=2)
                return [Document(page_content=content)]
        else:
            return None
    except Exception as e:
        st.error(f"❌ Error loading file: {e}")
        return None

# Main logic
if uploaded_file is not None:
    suffix = os.path.splitext(uploaded_file.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_file_path = tmp_file.name

    docs = load_file(tmp_file_path, suffix.lower())

    if docs:
        content = "\n".join([doc.page_content for doc in docs])

        with st.expander("📖 Show file content"):
            st.text(content)

        prompt = PromptTemplate(template=custom_prompt, input_variables=["poem"])
        chain = prompt | model | parser

        if st.button("✨ Generate Output"):
            with st.spinner("Generating..."):
                response = chain.invoke({"poem": content})
                st.success("✅ Summary Generated:")
                st.markdown(f"### 🧠 Output\n{response}")
    else:
        st.error("❌ Failed to read the file. Try another format or fix content.")
