# app.py
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_community.document_loaders import (
    TextLoader, CSVLoader, UnstructuredPDFLoader, UnstructuredWordDocumentLoader,
    UnstructuredMarkdownLoader, JSONLoader
)
from dotenv import load_dotenv
import os
import tempfile

load_dotenv()

# Initialize model and parser
model = ChatGoogleGenerativeAI(model='gemini-1.5-pro')
parser = StrOutputParser()

# Streamlit UI
st.set_page_config(page_title="📄 AI File Summarizer", layout="centered")
st.title("📄 AI File Summarizer with LangChain + Gemini")

uploaded_file = st.file_uploader(
    "📂 Upload a text-based file",
    type=["txt", "md", "csv", "json", "pdf", "docx"]
)

custom_prompt = st.text_area(
    "✍️ Enter your prompt",
    value="Write a summary for the following content - \n {poem}",
    height=100
)

def load_file(path, extension):
    if extension == ".txt":
        return TextLoader(path, encoding='utf-8').load()
    elif extension == ".csv":
        return CSVLoader(path).load()
    elif extension == ".pdf":
        return UnstructuredPDFLoader(path).load()
    elif extension == ".docx":
        return UnstructuredWordDocumentLoader(path).load()
    elif extension == ".md":
        return UnstructuredMarkdownLoader(path).load()
    elif extension == ".json":
        # Assumes one key per document line; adjust as needed
        return JSONLoader(path, jq_schema='.text', text_content=False).load()
    else:
        return None

if uploaded_file is not None:
    # Save the uploaded file temporarily
    suffix = os.path.splitext(uploaded_file.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_file_path = tmp_file.name

    try:
        docs = load_file(tmp_file_path, suffix.lower())
        content = "\n".join([doc.page_content for doc in docs]) if docs else ""
    except Exception as e:
        st.error(f"❌ Error loading file: {e}")
        content = ""

    if content:
        with st.expander("📖 Show extracted content"):
            st.text(content)

        prompt = PromptTemplate(template=custom_prompt, input_variables=["poem"])
        chain = prompt | model | parser

        if st.button("✨ Generate Output"):
            with st.spinner("Generating..."):
                response = chain.invoke({"poem": content})
                st.success("✅ Output:")
                st.markdown(f"### 🧠 Result\n{response}")

