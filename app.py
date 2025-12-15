"""
GitHub Repository Q&A System using RAG
Ollama Embeddings + ChromaDB + Gemini 2.5 Flash
"""
import streamlit as st
from pathlib import Path
from core.github_handler import GitHubHandler
from core.code_parser import CodeParser
from core.retriever import RAGRetriever
from llm.gemini_client import GeminiClient
from utils.logger import logger
from config.settings import Settings

st.set_page_config(
    page_title="GitHub RAG Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .tech-badge {
        display: inline-block;
        background: #f0f2f6;
        padding: 0.3rem 0.8rem;
        border-radius: 1rem;
        margin: 0.2rem;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    """Initialize session state variables"""
    if 'retriever' not in st.session_state:
        st.session_state.retriever = None
    if 'repo_info' not in st.session_state:
        st.session_state.repo_info = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'indexed' not in st.session_state:
        st.session_state.indexed = False

init_session_state()

# Header
st.markdown('<div class="main-header">🤖 GitHub RAG Assistant</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Intelligent Code Repository Analysis with AI</div>',
    unsafe_allow_html=True
)

# Tech stack badges
st.markdown(
    '<div style="text-align: center;">'
    '<span class="tech-badge">🔍 Ollama Embeddings</span>'
    '<span class="tech-badge">💾 ChromaDB</span>'
    '<span class="tech-badge">✨ Gemini 2.5 Flash</span>'
    '<span class="tech-badge">🐍 Python</span>'
    '</div>',
    unsafe_allow_html=True
)

st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Key status
    if Settings.GEMINI_API_KEY:
        st.success("✅ Gemini API Key Configured")
    else:
        st.error("❌ Gemini API Key Missing")
        st.info("Add GEMINI_API_KEY to your .env file")
    
    if Settings.GITHUB_TOKEN:
        st.success("✅ GitHub Token Configured")
    else:
        st.warning("⚠️ GitHub Token Missing (Private repos won't work)")
    
    st.divider()
    
    # Repository input
    st.subheader("📂 Repository Setup")
    repo_url = st.text_input(
        "GitHub Repository URL",
        placeholder="https://github.com/owner/repo",
        help="Enter GitHub URL or owner/repo format"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        force_rebuild = st.checkbox("Force rebuild", value=False, 
                                    help="Delete and rebuild index")
    with col2:
        use_cache = st.checkbox("Use cache", value=True,
                               help="Load from existing index if available")
    
    index_button = st.button(
        "🔍 Clone & Index Repository",
        use_container_width=True,
        type="primary"
    )
    
    if index_button and repo_url:
        with st.spinner("Processing repository..."):
            try:
                # Clone repository
                progress = st.progress(0, "Cloning repository...")
                github_handler = GitHubHandler()
                repo_path = github_handler.clone_repository(repo_url, force_rebuild)
                repo_info = github_handler.get_repository_info(repo_path)
                repo_name = repo_info['name']
                
                progress.progress(20, "Repository cloned!")
                
                # Initialize retriever
                retriever = RAGRetriever()
                
                # Check cache
                if use_cache and not force_rebuild:
                    retriever._init_client(retriever._get_collection_name(repo_name))
                    existing_count = retriever.collection.count()
                    
                    if existing_count > 0:
                        progress.progress(100, "Using cached index!")
                        st.success(f"✅ Loaded {existing_count} documents from cache!")
                        st.session_state.retriever = retriever
                        st.session_state.repo_info = repo_info
                        st.session_state.indexed = True
                        st.session_state.chat_history = []
                        st.rerun()
                
                # Rebuild index
                if force_rebuild:
                    progress.progress(30, "Deleting old index...")
                    try:
                        retriever.delete_collection(repo_name)
                    except:
                        pass
                
                # Parse code
                progress.progress(40, "Parsing code files...")
                code_parser = CodeParser()
                documents = code_parser.parse_repository(repo_path)
                
                if not documents:
                    st.error("No processable files found")
                    st.stop()
                
                progress.progress(60, "Parsed files successfully!")
                
                # Build index
                progress.progress(70, "Generating embeddings (this may take a moment)...")
                retriever.build_index(documents, repo_name)
                
                progress.progress(100, "Index built successfully!")
                
                # Save to session
                st.session_state.retriever = retriever
                st.session_state.repo_info = repo_info
                st.session_state.indexed = True
                st.session_state.chat_history = []
                
                st.success(f"✅ Indexed {len(documents)} code chunks!")
                st.balloons()
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                logger.error(f"Repository indexing failed: {e}")
    
    # Repository info
    if st.session_state.indexed and st.session_state.repo_info:
        st.divider()
        st.subheader("📊 Repository Info")
        info = st.session_state.repo_info
        
        st.text(f"📁 Name: {info['name']}")
        st.text(f"🌿 Branch: {info.get('branch', 'N/A')}")
        st.text(f"📝 Commit: {info.get('commit', 'N/A')}")
        
        # Collection stats
        try:
            if st.session_state.retriever and st.session_state.retriever.collection:
                count = st.session_state.retriever.collection.count()
                st.text(f"📚 Documents: {count}")
        except:
            pass
        
        if st.button("🗑️ Clear Index", use_container_width=True):
            try:
                if st.session_state.retriever:
                    st.session_state.retriever.delete_collection(info['name'])
                
                st.session_state.retriever = None
                st.session_state.repo_info = None
                st.session_state.indexed = False
                st.session_state.chat_history = []
                st.success("Index cleared!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
    
    st.divider()
    
    # Settings
    st.subheader("🎛️ Query Settings")
    top_k = st.slider("Results to retrieve", 1, 10, Settings.TOP_K_RESULTS)
    
    st.divider()
    st.caption("💡 Powered by Ollama Embedding model, ChromaDB & Gemini 2.5 Flash")

# Main content
if not st.session_state.indexed:
    # Welcome screen
    st.info("👈 Enter a GitHub repository URL in the sidebar to get started")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🔍 Semantic Search")
        st.write("Natural language queries powered by Ollama local embedding model")
    
    with col2:
        st.markdown("### 💾 Persistent Storage")
        st.write("ChromaDB vector database with automatic caching")
    
    with col3:
        st.markdown("### ✨ AI Answers")
        st.write("Context-aware responses from Gemini 2.5 Flash")
    
    st.divider()
    
    # Example queries
    st.markdown("### 💡 Example Questions You Can Ask")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Architecture & Design:**")
        st.markdown("- How is the project structured?")
        st.markdown("- Which file handles authentication?")
        st.markdown("- What design patterns are used?")
        
        st.markdown("**Code Understanding:**")
        st.markdown("- How does the database connection work?")
        st.markdown("- What is the data flow?")
        st.markdown("- How are errors handled?")
    
    with col2:
        st.markdown("**Implementation Details:**")
        st.markdown("- Where are the API endpoints defined?")
        st.markdown("- How is user input validated?")
        st.markdown("- What libraries are used for X?")
        
        st.markdown("**Testing & Documentation:**")
        st.markdown("- What testing frameworks are used?")
        st.markdown("- Is there API documentation?")
        st.markdown("- How do I run the tests?")

else:
    # Chat interface
    st.markdown("### 💬 Ask Questions About Your Repository")
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Query input
    query = st.chat_input("Ask a question about the repository...")
    
    if query:
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": query})
        
        with st.chat_message("user"):
            st.markdown(query)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("🔍 Searching repository and generating answer..."):
                try:
                    # Retrieve context
                    retriever = st.session_state.retriever
                    results = retriever.retrieve(query, top_k=top_k)
                    
                    if not results:
                        response = "❌ I couldn't find relevant information in the repository to answer your question."
                    else:
                        # Get formatted context
                        context = retriever.get_context_for_query(query, top_k=top_k)
                        
                        # Generate answer with Gemini
                        gemini_client = GeminiClient()
                        response = gemini_client.generate_answer(query, context)
                        
                        # Add file references
                        referenced_files = set()
                        for doc, score in results:
                            referenced_files.add(doc.file_path)
                        
                        if referenced_files:
                            response += "\n\n---\n**📁 Referenced Files:**\n"
                            for file in sorted(referenced_files):
                                response += f"\n- `{file}`"
                    
                    st.markdown(response)
                    
                    # Add to chat history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": response
                    })
                    
                except Exception as e:
                    error_msg = f"❌ Error generating answer: {str(e)}"
                    st.error(error_msg)
                    logger.error(error_msg)
    
    # Additional controls
    st.divider()
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        if st.button("🔄 Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()
    
    with col2:
        if st.button("📊 Show Statistics"):
            if st.session_state.retriever:
                num_docs = len(st.session_state.retriever.documents)
                st.info(f"📚 Total indexed chunks: {num_docs}")
    
    with col3:
        if st.button("ℹ️ Help"):
            st.info("💡 Tip: Ask specific questions about code structure, implementation details, or functionality!")

# Footer
st.divider()
st.caption(
    "🤖 GitHub RAG Assistant | "
    "Built with Streamlit, Ollama Embedding, ChromaDB & Gemini 2.5 Flash"
)