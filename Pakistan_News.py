import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

# Configure app
st.set_page_config(
    page_title=" News Explorer",
    page_icon="🇵🇰",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .sidebar {
        background-color: #046a38;
        color: white;
    }
    .search-header {
        color: #046a38;
        border-bottom: 2px solid #046a38;
        padding-bottom: 10px;
    }
    .search-box {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .result-card {
        border-left: 4px solid #046a38;
        padding: 15px;
        margin-bottom: 15px;
        background-color: white;
        border-radius: 5px;
    }
    .quick-search-btn {
        width: 100%;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/3/32/Flag_of_Pakistan.svg", width=80)
    st.title(" News Explorer")
    
    with st.expander("🔍 Search Filters", expanded=True):
        st.selectbox("Category", ["General", "Politics", "Business", "Sports", "Technology", "Entertainment", "Health"], key="category")
        st.selectbox("Time Range", ["Today", "Last 24h", "This Week", "This Month", "Any Time"], key="time_range")
        st.selectbox("Region", ["All Pakistan", "Islamabad", "Karachi", "Lahore", "Peshawar", "Other"], key="region")
        st.selectbox("Language", ["English", "Urdu", "Both"], key="language")
        st.slider("Number of Results", 5, 25, 10, key="num_results")

# Main
st.header(" News Explorer", divider="green")

with st.container():
    st.subheader("Search News", anchor=False)
    search_tab, custom_tab = st.tabs(["Basic Search", "Advanced Search"])
    
    with search_tab:
        with st.form("basic_search"):
            query = st.text_input("Enter your search terms", placeholder="e.g. Pakistan election news")
            search_btn = st.form_submit_button("Search News", type="primary")
    
    with custom_tab:
        with st.form("advanced_search"):
            col1, col2 = st.columns(2)
            with col1:
                must_include = st.text_input("Must contain")
                exact_phrase = st.text_input("Exact phrase")
            with col2:
                exclude = st.text_input("Exclude words")
                site_filter = st.text_input("Specific website")
            
            custom_query = st.text_area("OR enter complete search query")
            custom_search_btn = st.form_submit_button("Advanced Search", type="primary")

# New: DuckDuckGo HTML-based search function
def duckduckgo_search(query, max_results=10):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    url = "https://html.duckduckgo.com/html"
    data = {"q": query}
    response = requests.post(url, headers=headers, data=data)

    if response.status_code != 200:
        raise Exception("DuckDuckGo search failed.")

    soup = BeautifulSoup(response.text, "html.parser")
    results = []
    for link in soup.find_all("a", class_="result__a", limit=max_results):
        title = link.get_text()
        href = link.get("href")
        results.append(f"{title}\n{href}")
    return results

# Function to perform search and display
def perform_search(query, num_results):
    with st.spinner(f"Searching for: {query}"):
        try:
            result_list = duckduckgo_search(query, num_results)
            if not result_list:
                st.warning("No results found.")
                return
            
            st.success(f"Found {len(result_list)} results")
            st.divider()
            
            for i, result in enumerate(result_list, 1):
                title, link = result.split("\n", 1)
                st.markdown(f"""
                <div class="result-card">
                    <h4>Result #{i}</h4>
                    <p>{title}</p>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"[📖 Read full article]({link})")
            
            if st.checkbox("View as table"):
                df = pd.DataFrame({
                    "Result": [f"Result {i}" for i in range(1, len(result_list)+1)],
                    "Title": [r.split("\n", 1)[0] for r in result_list],
                    "URL": [r.split("\n", 1)[1] for r in result_list],
                })
                st.dataframe(df, use_container_width=True)
        
        except Exception as e:
            st.error(f"Search error: {str(e)}")

# Basic search handling
if search_btn and query:
    search_query = query
    if st.session_state.language == "Urdu":
        search_query += " Urdu"
    elif st.session_state.language == "Both":
        search_query += " (Urdu OR English)"
    if st.session_state.region != "All Pakistan":
        search_query += f" {st.session_state.region}"
    if st.session_state.category != "General":
        search_query += f" {st.session_state.category.lower()}"
    if st.session_state.time_range != "Any Time":
        search_query += f" {st.session_state.time_range.lower().replace(' ', '')}"
    
    perform_search(search_query, st.session_state.num_results)

# Advanced search
if custom_search_btn and (custom_query or must_include or exact_phrase):
    if custom_query:
        perform_search(custom_query, st.session_state.num_results)
    else:
        query_parts = []
        if exact_phrase:
            query_parts.append(f'"{exact_phrase}"')
        if must_include:
            query_parts.append(must_include)
        if exclude:
            query_parts.append(f"-{exclude.replace(' ', ' -')}")
        if site_filter:
            query_parts.append(f"site:{site_filter}")
        if query_parts:
            perform_search(" ".join(query_parts), st.session_state.num_results)
        else:
            st.warning("Please enter search terms")

# Quick search buttons
st.divider()
st.subheader("Quick Searches")

quick_topics = {
    "Politics": "🏛️",
    "Economy": "💵", 
    "Sports": "⚽",
    "Technology": "📱",
    "Weather": "🌤️",
    "Health": "🏥"
}

cols = st.columns(len(quick_topics))
for i, (topic, icon) in enumerate(quick_topics.items()):
    with cols[i]:
        if st.button(f"{icon} {topic}", use_container_width=True):
            st.session_state.quick_search = f"Pakistan {topic.lower()} news"

# Handle quick search
if hasattr(st.session_state, "quick_search"):
    perform_search(st.session_state.quick_search, st.session_state.num_results)

# Footer
st.divider()
st.caption(f"© {datetime.now().year} Pakistan News Explorer | Powered by DuckDuckGo HTML Search")
