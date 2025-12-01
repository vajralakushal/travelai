from anthropic import Anthropic
from src.tools import SearchTool, ImageTool, GeocodingTool
from src.utils.config import ANTHROPIC_API_KEY

class DestinationAgent:
    def __init__(self, api_key=None):
        self.client = Anthropic(api_key=api_key or ANTHROPIC_API_KEY)
        self.search_tool = SearchTool()
        self.image_tool = ImageTool()
        self.geo_tool = GeocodingTool()
    
    def research(self, destination: str, interests: list):
        """
        Research destination and find relevant information
        """
        # Get coordinates for location context
        coordinates = self.geo_tool.get_coordinates(destination)
        
        # Search for general destination info
        search_query = f"{destination} travel guide attractions things to do"
        search_results = self.search_tool.search(search_query, max_results=3)
        
        # Get destination image
        image_data = self.image_tool.get_destination_image(destination)
        
        # Use Claude to synthesize information
        prompt = f"""You are a destination research agent for a travel planner.

Destination: {destination}
Traveler interests: {', '.join(interests)}

Search results summary:
{self._format_search_results(search_results)}

Provide:
1. Brief destination overview (2-3 sentences)
2. Top 5 must-see attractions matching interests
3. Cultural tips or local customs
4. Best neighborhoods to explore

Keep response under 200 words."""

        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {
            "research": message.content[0].text,
            "image": image_data,
            "coordinates": coordinates,
            "sources": [r["url"] for r in search_results.get("results", [])]
        }
    
    def _format_search_results(self, results):
        """Format search results for Claude"""
        if "error" in results:
            return "No search results available"
        
        formatted = []
        for r in results.get("results", []):
            formatted.append(f"- {r['title']}: {r['content'][:200]}...")
        return "\n".join(formatted)