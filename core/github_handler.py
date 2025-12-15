"""
GitHub repository handler for cloning and managing repositories
"""
import re
import shutil
from pathlib import Path
from git import Repo, GitCommandError
from config.settings import Settings
from utils.logger import logger

class GitHubHandler:
    """Handle GitHub repository operations"""
    
    def __init__(self):
        self.github_token = Settings.GITHUB_TOKEN
        self.clone_dir = Settings.REPOSITORIES_DIR
    
    def parse_github_url(self, url: str) -> dict:
        """Parse GitHub URL and extract owner and repository name"""
        patterns = [
            r'github\.com[:/]([^/]+)/([^/.]+)',
            r'github\.com/([^/]+)/([^/]+)\.git'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                owner, repo = match.groups()
                return {
                    'owner': owner,
                    'repo': repo.replace('.git', ''),
                    'full_name': f"{owner}/{repo.replace('.git', '')}"
                }
        
        raise ValueError(f"Invalid GitHub URL: {url}")
    
    def get_clone_url(self, repo_url: str) -> str:
        """Get authenticated clone URL if token is available"""
        if self.github_token and 'github.com' in repo_url:
            # Add token for authentication
            if repo_url.startswith('https://'):
                return repo_url.replace('https://', f'https://{self.github_token}@')
            elif not repo_url.startswith('http'):
                return f'https://{self.github_token}@github.com/{repo_url}.git'
        
        # Ensure https protocol
        if not repo_url.startswith('http'):
            return f'https://github.com/{repo_url}.git'
        
        return repo_url
    
    def clone_repository(self, repo_url: str, force_fresh: bool = False) -> Path:
        """Clone GitHub repository to local directory"""
        try:
            repo_info = self.parse_github_url(repo_url)
            repo_name = repo_info['repo']
            local_path = self.clone_dir / repo_name
            
            # Remove existing directory if force_fresh
            if force_fresh and local_path.exists():
                logger.info(f"Removing existing repository at {local_path}")
                shutil.rmtree(local_path)
            
            # Check if already cloned
            if local_path.exists() and (local_path / '.git').exists():
                logger.info(f"Repository already exists at {local_path}")
                try:
                    repo = Repo(local_path)
                    origin = repo.remotes.origin
                    origin.pull()
                    logger.info("Repository updated successfully")
                except Exception as e:
                    logger.warning(f"Could not update repository: {e}")
                
                return local_path
            
            # Clone repository
            clone_url = self.get_clone_url(repo_url)
            logger.info(f"Cloning repository from {repo_url}...")
            
            Repo.clone_from(clone_url, local_path, depth=1)
            logger.info(f"Repository cloned successfully to {local_path}")
            
            return local_path
            
        except GitCommandError as e:
            logger.error(f"Git error: {e}")
            raise Exception(f"Failed to clone repository: {e}")
        except Exception as e:
            logger.error(f"Error cloning repository: {e}")
            raise
    
    def get_repository_info(self, repo_path: Path) -> dict:
        """Get basic repository information"""
        try:
            repo = Repo(repo_path)
            return {
                'path': str(repo_path),
                'name': repo_path.name,
                'branch': repo.active_branch.name,
                'commit': repo.head.commit.hexsha[:7],
                'remote_url': repo.remotes.origin.url if repo.remotes else None
            }
        except Exception as e:
            logger.error(f"Error getting repository info: {e}")
            return {'path': str(repo_path), 'name': repo_path.name}