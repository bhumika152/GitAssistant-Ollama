# 🤖 GitHub RAG Assistant

A local-first GitHub Repository Q&A system built using Retrieval-Augmented Generation (RAG).
It allows you to ask questions about any GitHub repository and get accurate answers grounded in the repository’s source code.

🔒 Privacy-friendly — Code embeddings are generated locally using Ollama.
⚡ Fast & Accurate — Uses ChromaDB vector search + Gemini 2.5 Flash for reasoning.

# 🚀 Features

🔍 Ask natural-language questions about any GitHub repository

🧠 RAG-based architecture (no hallucinations)

🧩 Intelligent code chunking & parsing

🧠 Local embeddings via Ollama (nomic-embed-text)

💾 Persistent vector storage using ChromaDB

💬 High-quality answers using Google Gemini 2.5 Flash

🖥️ Interactive UI built with Streamlit

# ⚙️ Prerequisites
1️⃣ Python
Python 3.9 – 3.12

2️⃣ Ollama (Required for Local Embeddings)

Install Ollama:
👉 https://ollama.com/download

How It Works

User enters a GitHub repository URL

Repository is cloned locally

Source code is parsed & chunked

Embeddings are generated locally via Ollama

Vectors are stored in ChromaDB

User asks a question

Relevant code chunks are retrieved

Gemini 2.5 Flash generates a grounded answer

# 🔐 Privacy & Security

✅ No source code sent to embedding APIs

✅ Embeddings generated locally

✅ Vector DB stored on disk

❌ No telemetry (disabled in ChromaDB)

# 🛠️ Configuration

All settings are centralized in:

config/settings.py


You can configure:

Chunk size

Embedding batch size

Top-K retrieval

ChromaDB path

Model names

# 🙌 Acknowledgements

Ollama

ChromaDB

Sentence Transformers research

Google Gemini

