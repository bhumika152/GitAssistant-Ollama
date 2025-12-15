"""
Code parser for extracting and chunking code content
"""
import tiktoken
from pathlib import Path
from typing import List
from config.settings import Settings
from utils.file_utils import FileUtils
from utils.logger import logger

class CodeDocument:
    """Represents a code document with metadata"""
    
    def __init__(self, content: str, file_path: str, language: str, chunk_id: int = 0):
        self.content = content
        self.file_path = file_path
        self.language = language
        self.chunk_id = chunk_id
    
    def __repr__(self):
        return f"CodeDocument(file={self.file_path}, chunk={self.chunk_id}, len={len(self.content)})"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'content': self.content,
            'file_path': self.file_path,
            'language': self.language,
            'chunk_id': self.chunk_id
        }

class CodeParser:
    """Parse and chunk code files from repository"""
    
    def __init__(self):
        self.chunk_size = Settings.CHUNK_SIZE
        self.chunk_overlap = Settings.CHUNK_OVERLAP
        self.encoder = tiktoken.get_encoding("cl100k_base")
    
    def get_language_from_extension(self, file_path: Path) -> str:
        """Determine programming language from file extension"""
        ext_map = {
            '.py': 'python', '.js': 'javascript', '.jsx': 'javascript',
            '.ts': 'typescript', '.tsx': 'typescript', '.java': 'java',
            '.cpp': 'cpp', '.c': 'c', '.h': 'c', '.cs': 'csharp',
            '.go': 'go', '.rs': 'rust', '.php': 'php', '.rb': 'ruby',
            '.swift': 'swift', '.kt': 'kotlin', '.scala': 'scala',
            '.md': 'markdown', '.txt': 'text', '.json': 'json',
            '.yaml': 'yaml', '.yml': 'yaml', '.xml': 'xml',
            '.html': 'html', '.css': 'css', '.sh': 'bash',
            '.sql': 'sql', '.r': 'r', '.dart': 'dart',
            '.vue': 'vue', '.svelte': 'svelte'
        }
        return ext_map.get(file_path.suffix.lower(), 'text')
    
    def chunk_text(self, text: str, file_path: str, language: str) -> List[CodeDocument]:
        """Split text into overlapping chunks"""
        tokens = self.encoder.encode(text)
        chunks = []
        
        if len(tokens) <= self.chunk_size:
            return [CodeDocument(text, file_path, language, 0)]
        
        # Create overlapping chunks
        start = 0
        chunk_id = 0
        
        while start < len(tokens):
            end = start + self.chunk_size
            chunk_tokens = tokens[start:end]
            chunk_text = self.encoder.decode(chunk_tokens)
            
            chunks.append(CodeDocument(chunk_text, file_path, language, chunk_id))
            
            start = end - self.chunk_overlap
            chunk_id += 1
            
            if start >= len(tokens) - self.chunk_overlap:
                break
        
        return chunks
    
    def parse_repository(self, repo_path: Path) -> List[CodeDocument]:
        """Parse all files in repository and create document chunks"""
        documents = []
        files = FileUtils.scan_repository(repo_path)
        
        logger.info(f"Parsing {len(files)} files...")
        
        for file_path in files:
            try:
                content = FileUtils.read_file_content(file_path)
                if not content:
                    continue
                
                relative_path = FileUtils.get_relative_path(file_path, repo_path)
                language = self.get_language_from_extension(file_path)
                
                chunks = self.chunk_text(content, relative_path, language)
                documents.extend(chunks)
                
            except Exception as e:
                logger.error(f"Error parsing file {file_path}: {e}")
                continue
        
        logger.info(f"Created {len(documents)} document chunks from {len(files)} files")
        return documents