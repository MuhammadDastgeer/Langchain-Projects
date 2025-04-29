# app.py

import streamlit as st
from dotenv import load_dotenv
import os
import tempfile

# LangChain components
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_community.document_loaders import (
    TextLoader, CSVLoader, PyPDFLoader, UnstructuredWordDocumentLoader,
    UnstructuredMarkdownLoader, JSONLoader
)

# Load environment variables
load_dotenv()

# Initialize the model and parser
model = ChatGoogleGenerativeAI(model="gemini-1.5-pro")
parser = StrOutputParser()

# Streamlit UI setup
st.set_page_config(page_title="📄 AI File Summarizer", layout="centered")
st.title("📄 AI File Summarizer with LangChain + Gemini")

# File uploader
uploaded_file = st.file_uploader(
    "📂 Upload a file (txt, md, csv, json, pdf, docx)",
    type=["txt", "md", "csv", "json", "pdf", "docx"]
)

# Prompt input
custom_prompt = st.text_area(
    "✍️ Enter your prompt",
    value="Write a summary for the following content:\n\n{poem}",
    height=100
)

# Function to load file content
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
            return JSONLoader(path, jq_schema=".text", text_content=False).load()
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
                st.success("✅ Result:")
                st.markdown(f"### 🧠 Output\n{response}")
    else:
        st.error("Failed to read file content. Please check the format or try another file.")
