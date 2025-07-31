import requests
import time
from typing import Optional, Dict
from utils.logger import setup_logger
from utils.validators import validate_ollama_connection, validate_summary_length

class TextSummarizer:
    def __init__(self, model="mistral", base_url="http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.logger = setup_logger("TextSummarizer")
        self._validate_connection()

    def _validate_connection(self):
        """Validate Ollama connection on initialization"""
        if not validate_ollama_connection(self.base_url):
            self.logger.warning(f"⚠️ Ollama not accessible at {self.base_url}")
            self.logger.warning("Make sure Ollama is running and the model is installed")

    def _make_request(self, prompt: str, max_tokens: int = 500) -> Optional[str]:
        """Make request to Ollama with error handling"""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": 0.7
                    }
                },
                timeout=None
            )
            
            if response.status_code == 404:
                self.logger.error(f"❌ Model '{self.model}' not found")
                raise Exception(f"Model '{self.model}' not found. Please install it with: ollama pull {self.model}")
            elif response.status_code != 200:
                self.logger.error(f"❌ Ollama request failed: {response.status_code}")
                raise Exception(f"Ollama request failed with status {response.status_code}")
            
            return response.json().get("response", "").strip()
            
        except requests.Timeout:
            self.logger.error("❌ Ollama request timeout")
            raise Exception("Ollama request timeout. The model might be too slow or overloaded.")
        except requests.ConnectionError:
            self.logger.error("❌ Cannot connect to Ollama")
            raise Exception("Cannot connect to Ollama. Make sure it's running.")
        except Exception as e:
            self.logger.error(f"❌ Unexpected error: {e}")
            raise

    def summarize_text(self, text: str, max_length: int = 200) -> str:
        """Summarize text with comprehensive error handling"""
        if not validate_summary_length(text):
            return "Text too short or too long for summarization."

        self.logger.info(f"📝 Summarizing text ({len(text)} characters)")
        
        try:
            # Truncate text if too long (to avoid token limits)
            truncated_text = text[:3000] if len(text) > 3000 else text
            
            prompt = f"""Please provide a concise summary of the following article in under {max_length} words. Focus on the main points and key information:

{truncated_text}

Summary:"""
            
            summary = self._make_request(prompt, max_tokens=max_length * 2)
            
            if not summary:
                return "Failed to generate summary."
            
            # Clean up the summary
            summary = summary.strip()
            if summary.startswith("Summary:"):
                summary = summary[8:].strip()
            
            self.logger.info(f"✅ Generated summary ({len(summary)} characters)")
            return summary
            
        except Exception as e:
            self.logger.error(f"❌ Failed to summarize text: {e}")
            return f"Error generating summary: {str(e)}"

    def summarize_articles(self, articles: list, max_length: int = 200) -> list:
        """Summarize multiple articles with progress tracking"""
        self.logger.info(f"📚 Summarizing {len(articles)} articles")
        summarized_articles = []
        
        for i, article in enumerate(articles, 1):
            try:
                self.logger.info(f"📝 Processing article {i}/{len(articles)}: {article.get('title', 'Unknown')[:50]}...")
                
                summary = self.summarize_text(article['content'], max_length)
                article['summary'] = summary
                summarized_articles.append(article)
                
                # Small delay to avoid overwhelming the model
                time.sleep(0.5)
                
            except Exception as e:
                self.logger.error(f"❌ Failed to summarize article {i}: {e}")
                article['summary'] = "Failed to generate summary."
                summarized_articles.append(article)
        
        self.logger.info(f"✅ Completed summarization of {len(summarized_articles)} articles")
        return summarized_articles

    def get_model_info(self) -> Dict:
        """Get information about the current model"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get("models", [])
                for model in models:
                    if model.get("name") == self.model:
                        return {
                            "name": model.get("name"),
                            "size": model.get("size"),
                            "modified_at": model.get("modified_at")
                        }
            return {"name": self.model, "status": "unknown"}
        except Exception as e:
            self.logger.error(f"❌ Failed to get model info: {e}")
            return {"name": self.model, "status": "error"}
