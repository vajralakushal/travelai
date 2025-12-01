import requests
from src.utils.config import UNSPLASH_ACCESS_KEY

class ImageTool:
    def __init__(self):
        self.access_key = UNSPLASH_ACCESS_KEY
        self.base_url = "https://api.unsplash.com/search/photos"
    
    def get_destination_image(self, location: str):
        """
        Get representative image for a destination
        Args:
            location: Location name
        Returns:
            Dict with image URL and photographer attribution
        """
        params = {
            "query": f"{location} travel landmark",
            "per_page": 1,
            "orientation": "landscape"
        }
        headers = {
            "Authorization": f"Client-ID {self.access_key}"
        }
        
        try:
            response = requests.get(self.base_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data["results"]:
                result = data["results"][0]
                return {
                    "url": result["urls"]["regular"],
                    "photographer": result["user"]["name"],
                    "photographer_url": result["user"]["links"]["html"]
                }
            return {"error": "No image found"}
        except Exception as e:
            return {"error": str(e)}