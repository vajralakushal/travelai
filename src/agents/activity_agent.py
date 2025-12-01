from anthropic import Anthropic
from src.tools import SearchTool
from src.utils.config import ANTHROPIC_API_KEY
from datetime import datetime

class ActivityAgent:
    def __init__(self, api_key=None):
        self.client = Anthropic(api_key=api_key or ANTHROPIC_API_KEY)
        self.search_tool = SearchTool()
    
    def find_activities(self, destination: str, interests: list, start_date: str, end_date: str, coordinates: dict):
        """
        Find weather-appropriate activities for destination based on location and season
        """
        # Determine season and climate context
        season_context = self._get_season_context(start_date, coordinates)
        
        # Search for activities
        interests_str = " ".join(interests)
        search_query = f"{destination} {interests_str} activities things to do {start_date}"
        search_results = self.search_tool.search(search_query, max_results=5)
        
        prompt = f"""You are an activity planning agent for a travel planner.

Destination: {destination}
Dates: {start_date} to {end_date}
Traveler Interests: {', '.join(interests)}

Location & Season Context:
{season_context}

Search Results:
{self._format_search_results(search_results)}

TASK: Create a diverse list of 10-12 specific activities that:
1. Match the traveler's interests
2. Are appropriate for the destination's typical weather during this season
3. Include BOTH weather-dependent and weather-independent options (indoor/outdoor mix)
4. Account for the destination's climate (e.g., Tokyo in June = rainy season, so include indoor options)
5. Are culturally appropriate and respectful

For each activity, provide:
- Activity name and brief description (1-2 sentences)
- Estimated duration (e.g., "2-3 hours", "Half day", "Full day")
- Estimated cost ($, $$, or $$$)
- Best time of day (Morning/Midday/Evening/Night)
- Weather dependency (Indoor/Outdoor/Either)

IMPORTANT GUIDELINES:
- Include a healthy mix of indoor and outdoor activities
- For tropical/monsoon destinations during rainy season: emphasize indoor cultural activities, covered markets, museums
- For cold destinations: include indoor alternatives but also cold-weather outdoor activities if appropriate
- DO NOT mention extreme weather events (hurricanes, typhoons, blizzards) or emergency scenarios
- Focus on typical seasonal conditions, not disasters
- Be culturally sensitive and avoid stereotypes

Format as a clear numbered list."""

        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {
            "activities": message.content[0].text,
            "season_context": season_context,
            "sources": [r["url"] for r in search_results.get("results", [])]
        }
    
    def _get_season_context(self, start_date: str, coordinates: dict):
        """
        Determine season and typical weather based on location and date
        """
        try:
            date_obj = datetime.strptime(start_date, "%Y-%m-%d")
            month = date_obj.month
            lat = coordinates.get("lat", 0)
            
            # Determine hemisphere
            hemisphere = "Northern" if lat >= 0 else "Southern"
            
            # Determine season based on hemisphere and month
            if hemisphere == "Northern":
                if month in [12, 1, 2]:
                    season = "Winter"
                elif month in [3, 4, 5]:
                    season = "Spring"
                elif month in [6, 7, 8]:
                    season = "Summer"
                else:
                    season = "Fall"
            else:  # Southern hemisphere
                if month in [12, 1, 2]:
                    season = "Summer"
                elif month in [3, 4, 5]:
                    season = "Fall"
                elif month in [6, 7, 8]:
                    season = "Winter"
                else:
                    season = "Spring"
            
            # Get climate zone (simplified)
            if abs(lat) < 23.5:
                climate = "Tropical"
            elif abs(lat) < 35:
                climate = "Subtropical"
            elif abs(lat) < 50:
                climate = "Temperate"
            else:
                climate = "Cold"
            
            context = f"""Season: {season} ({hemisphere} Hemisphere)
Climate Zone: {climate}
Month: {date_obj.strftime('%B')}

Typical conditions for this location and season:
- {climate} {season.lower()} weather expected
- Plan for a mix of indoor and outdoor activities
- Include weather-flexible options"""
            
            return context
            
        except Exception as e:
            return "Season information unavailable - plan diverse indoor and outdoor activities"
    
    def _format_search_results(self, results):
        """Format search results for Claude"""
        if "error" in results:
            return "No search results available"
        
        formatted = []
        for r in results.get("results", []):
            formatted.append(f"- {r['title']}: {r['content'][:150]}...")
        return "\n".join(formatted)