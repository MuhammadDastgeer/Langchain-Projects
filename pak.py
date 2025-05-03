import streamlit as st
from langchain_community.tools import DuckDuckGoSearchRun
import pandas as pd
from datetime import datetime

# Initialize search tool
search = DuckDuckGoSearchRun()

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

# Sidebar with search filters
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/3/32/Flag_of_Pakistan.svg", width=80)
    st.title(" News Explorer")
    
    with st.expander("🔍 Search Filters", expanded=True):
        st.selectbox(
            "Category",
            ["General", "Politics", "Business", "Sports", "Technology", "Entertainment", "Health"],
            key="category"
        )
        
        st.selectbox(
            "Time Range",
            ["Today", "Last 24h", "This Week", "This Month", "Any Time"],
            key="time_range"
        )
        
        st.selectbox(
            "Region",
            ["All Pakistan", "Islamabad", "Karachi", "Lahore", "Peshawar", "Other"],
            key="region"
        )
        
        st.selectbox(
            "Language",
            ["English", "Urdu", "Both"],
            key="language"
        )
        
        st.slider("Number of Results", 5, 25, 10, key="num_results")

# Main content area
st.header(" News Explorer", divider="green")

# Search box container
with st.container():
    st.subheader("Search News", anchor=False)
    
    # Tabbed interface for search types
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

# Function to execute searches and display results
def perform_search(query, num_results):
    with st.spinner(f"Searching for: {query}"):
        try:
            results = search.run(query)
            
            if not results:
                st.warning("No results found. Try different search terms.")
                return
            
            # Process and display results
            result_list = [r.strip() for r in results.split('\n') if r.strip()]
            
            st.success(f"Found {len(result_list)} results")
            st.divider()
            
            for i, result in enumerate(result_list[:num_results], 1):
                with st.container():
                    st.markdown(f"""
                    <div class="result-card">
                        <h4>Result #{i}</h4>
                        <p>{result}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Extract and show URL if available
                    if "http" in result:
                        url = result[result.find("http"):].split()[0]
                        st.markdown(f"[📖 Read full article]({url})")
            
            # Option to view as data table
            if st.checkbox("View as table"):
                df = pd.DataFrame({
                    "Result": [f"Result {i}" for i in range(1, len(result_list[:num_results])+1)],
                    "Content": result_list[:num_results]
                })
                st.dataframe(df, use_container_width=True)
                
        except Exception as e:
            st.error(f"Search error: {str(e)}")

# Handle basic search
if search_btn and query:
    # Build query from filters
    search_query = query
    
    # Add language filter
    if st.session_state.language == "Urdu":
        search_query += " Urdu"
    elif st.session_state.language == "Both":
        search_query += " (Urdu OR English)"
    
    # Add region filter
    if st.session_state.region != "All Pakistan":
        search_query += f" {st.session_state.region}"
    
    # Add category filter
    if st.session_state.category != "General":
        search_query += f" {st.session_state.category.lower()}"
    
    # Add time filter
    if st.session_state.time_range != "Any Time":
        search_query += f" {st.session_state.time_range.lower().replace(' ', '')}"
    
    perform_search(search_query, st.session_state.num_results)

# Handle advanced search
if custom_search_btn and (custom_query or must_include or exact_phrase):
    if custom_query:
        # Use raw custom query if provided
        perform_search(custom_query, st.session_state.num_results)
    else:
        # Build advanced query from components
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
st.caption(f"© {datetime.now().year} Pakistan News Explorer | Powered by DuckDuckGo Search")