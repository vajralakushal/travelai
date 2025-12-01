import requests
from src.utils.config import TAVILY_API_KEY

class SearchTool:
    def __init__(self):
        self.api_key = TAVILY_API_KEY
        self.base_url = "https://api.tavily.com/search"
    
    def search(self, query: str, max_results: int = 5):
        """
        Search the web using Tavily API
        Args:
            query: Search query string
            max_results: Maximum number of results to return
        Returns:
            List of search results with title, content, and URL
        """
        payload = {
            "api_key": self.api_key,
            "query": query,
            "max_results": max_results,
            "include_answer": True,
            "search_depth": "basic"
        }
        
        try:
            response = requests.post(self.base_url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = {
                "answer": data.get("answer", ""),
                "results": [
                    {
                        "title": r.get("title"),
                        "content": r.get("content"),
                        "url": r.get("url")
                    }
                    for r in data.get("results", [])
                ]
            }
            return results
        except Exception as e:
            return {"error": str(e), "results": []}