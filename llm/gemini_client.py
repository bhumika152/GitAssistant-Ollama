"""
Google Gemini 2.0 Flash API client for generating answers
"""
import google.generativeai as genai
from config.settings import Settings
from utils.logger import logger

class GeminiClient:
    """Client for interacting with Google Gemini 2.0 Flash API"""
    
    def __init__(self):
        genai.configure(api_key=Settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(Settings.GEMINI_MODEL)
        logger.info(f"Initialized Gemini model: {Settings.GEMINI_MODEL}")
    
    def generate_answer(self, query: str, context: str) -> str:
        """Generate answer using retrieved context"""
        
        prompt = f"""You are an expert code assistant analyzing a GitHub repository. 
Based on the provided code context, answer the user's question accurately and concisely.

**Instructions:**
- Use ONLY the information from the provided context
- If the context doesn't contain relevant information, say so clearly
- Reference specific files when mentioning code
- Provide code snippets when relevant (use proper markdown formatting)
- Be precise and technical
- If multiple files are relevant, mention all of them
- Format your response in markdown for better readability

**Code Context:**
{context}

**User Question:**
{query}

**Answer:**"""
        
        try:
            logger.info("Generating answer with Gemini 2.0 Flash...")
            response = self.model.generate_content(prompt)
            answer = response.text
            logger.info("Answer generated successfully")
            return answer
        
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            raise Exception(f"Failed to generate answer: {str(e)}")
    
    def generate_summary(self, repo_name: str, file_count: int, languages: list) -> str:
        """Generate repository summary"""
        
        prompt = f"""Provide a brief summary of this GitHub repository:

**Repository Name:** {repo_name}
**Number of Files:** {file_count}
**Languages Detected:** {', '.join(languages)}

**Provide a 2-3 sentence summary about:**
1. What type of project this appears to be
2. Main technologies used
3. Likely purpose

Keep it concise and informative."""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return "Unable to generate repository summary."