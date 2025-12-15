"""
File utilities for handling repository files
"""
import os
from pathlib import Path
from typing import List
from config.settings import Settings
from utils.logger import logger

class FileUtils:
    """Utilities for file operations"""
    
    @staticmethod
    def is_text_file(file_path: Path) -> bool:
        """Check if file is a text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read(1024)
            return True
        except (UnicodeDecodeError, PermissionError):
            return False
    
    @staticmethod
    def should_process_file(file_path: Path) -> bool:
        """Determine if file should be processed"""
        # Check extension
        if file_path.suffix.lower() not in Settings.SUPPORTED_EXTENSIONS:
            return False
        
        # Check file size
        try:
            size_mb = file_path.stat().st_size / (1024 * 1024)
            if size_mb > Settings.MAX_FILE_SIZE_MB:
                logger.warning(f"Skipping large file: {file_path} ({size_mb:.2f}MB)")
                return False
        except OSError:
            return False
        
        # Check if text file
        if not FileUtils.is_text_file(file_path):
            return False
        
        return True
    
    @staticmethod
    def should_ignore_directory(dir_name: str) -> bool:
        """Check if directory should be ignored"""
        return dir_name in Settings.IGNORED_DIRS or dir_name.startswith('.')
    
    @staticmethod
    def scan_repository(repo_path: Path) -> List[Path]:
        """Scan repository and return list of processable files"""
        files = []
        
        for root, dirs, filenames in os.walk(repo_path):
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if not FileUtils.should_ignore_directory(d)]
            
            for filename in filenames:
                file_path = Path(root) / filename
                if FileUtils.should_process_file(file_path):
                    files.append(file_path)
        
        logger.info(f"Found {len(files)} processable files in repository")
        return files
    
    @staticmethod
    def read_file_content(file_path: Path) -> str:
        """Safely read file content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return ""
    
    @staticmethod
    def get_relative_path(file_path: Path, repo_path: Path) -> str:
        """Get relative path from repository root"""
        try:
            return str(file_path.relative_to(repo_path))
        except ValueError:
            return str(file_path)