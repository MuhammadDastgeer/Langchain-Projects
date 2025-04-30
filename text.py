import streamlit as st
import os
import tempfile
import json
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document

from langchain_text_splitters import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
    MarkdownHeaderTextSplitter,
    SentenceTransformersTokenTextSplitter
)

from langchain_community.document_loaders import (
    TextLoader, CSVLoader, PyPDFLoader,
    UnstructuredWordDocumentLoader, UnstructuredMarkdownLoader
)

# Load environment
load_dotenv()

# Initialize model
model = ChatGoogleGenerativeAI(model="gemini-1.5-pro")
parser = StrOutputParser()

# Streamlit UI
st.set_page_config(page_title="📄 AI Summarizer", layout="wide")
st.title("📄 AI File Summarizer with All Text Splitters")

# Sidebar config
st.sidebar.header("⚙️ Settings")
split_strategy = st.sidebar.selectbox(
    "Text splitting method",
    (
        "None",
        "Length-Based",
        "Text Structure-Based",
        "Document Structure-Based",
        "Semantic Meaning-Based"
    )
)

chunk_size = st.sidebar.number_input("Chunk size", 10, 4000, step=10)
chunk_overlap = st.sidebar.number_input("Chunk overlap", 0, 500, step=5)

custom_prompt = st.text_area(
    "✍️ Enter your prompt",
    value="Write a summary for the following content:\n\n{poem}",
    height=100
)

uploaded_file = st.file_uploader(
    "📂 Upload a file (.txt, .csv, .pdf, .docx, .md, .json)",
    type=["txt", "csv", "pdf", "docx", "md", "json"]
)

# Load file
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
                return [Document(page_content=json.dumps(data, indent=2))]
        else:
            return None
    except Exception as e:
        st.error(f"❌ Error loading file: {e}")
        return None

# Split docs
def split_docs(docs, strategy, chunk_size, chunk_overlap):
    if strategy == "Length-Based":
        splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        return splitter.split_documents(docs)

    elif strategy == "Text Structure-Based":
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        return splitter.split_documents(docs)

    elif strategy == "Document Structure-Based":
        splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[("#", "H1"), ("##", "H2"), ("###", "H3")]
        )
        split_output = []
        for doc in docs:
            split_output.extend(splitter.split_text(doc.page_content))
        return split_output

    elif strategy == "Semantic Meaning-Based":
        splitter = SentenceTransformersTokenTextSplitter(
            model_name="all-MiniLM-L6-v2",
            tokens_per_chunk=chunk_size,
            chunk_overlap=chunk_overlap
        )
        return splitter.split_documents(docs)

    else:
        return docs

# Main logic
if uploaded_file is not None:
    suffix = os.path.splitext(uploaded_file.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_file_path = tmp_file.name

    docs = load_file(tmp_file_path, suffix.lower())

    if docs:
        docs = split_docs(docs, split_strategy, chunk_size, chunk_overlap)

        # Show all extracted content
        with st.expander("📖 Show extracted content"):
            st.text("\n\n".join([doc.page_content for doc in docs[:10]]))

        # Page selector
        selected_page = st.sidebar.selectbox(
            "📄 Select page/chunk to summarize",
            options=range(len(docs)),
            format_func=lambda x: f"Page {x + 1}",
            index=0
        )

        selected_text = docs[selected_page].page_content

        with st.expander(f"📃 Selected Page {selected_page + 1}"):
            st.text(selected_text[:3000] + ("..." if len(selected_text) > 3000 else ""))

        # Summarize
        if st.button("✨ Generate Summary"):
            with st.spinner("Generating..."):
                prompt = PromptTemplate(template=custom_prompt, input_variables=["poem"])
                chain = prompt | model | parser
                response = chain.invoke({"poem": selected_text})
                st.success("✅ Summary Generated")
                st.markdown(f"### 🧠 Output\n{response}")
    else:
        st.error("❌ Could not read file.")
