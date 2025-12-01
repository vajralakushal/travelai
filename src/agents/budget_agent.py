from anthropic import Anthropic
from src.tools import SearchTool
from src.utils.config import ANTHROPIC_API_KEY

class BudgetAgent:
    def __init__(self, api_key=None):
        self.client = Anthropic(api_key=api_key or ANTHROPIC_API_KEY)
        self.search_tool = SearchTool()
    
    def estimate_costs(self, destination: str, start_date: str, end_date: str, budget: float, activities: str):
        """
        Estimate costs and provide budget breakdown
        """
        # Calculate trip duration
        from datetime import datetime
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        num_days = (end - start).days + 1
        
        # Search for cost information
        search_query = f"{destination} travel costs budget accommodation food 2025"
        search_results = self.search_tool.search(search_query, max_results=3)
        
        prompt = f"""You are a budget planning agent for a travel planner.

Destination: {destination}
Travel Dates: {start_date} to {end_date} ({num_days} days)
Total Budget: ${budget:.2f}
Daily Budget: ${budget/num_days:.2f}

Search Results on Costs:
{self._format_search_results(search_results)}

Proposed Activities:
{activities[:500]}...

TASK: Create a realistic budget breakdown with:

1. **Daily Cost Estimates:**
   - Accommodation (per night)
   - Food (breakfast, lunch, dinner, snacks)
   - Local transportation
   - Activities/attractions
   - Miscellaneous

2. **Budget Assessment:**
   - Is the ${budget:.2f} budget realistic for {num_days} days?
   - Recommendation: comfortable / tight / insufficient
   - Suggested budget adjustments if needed

3. **Money-Saving Tips:**
   - 2-3 specific tips for this destination

Keep response under 250 words. Be realistic and honest about costs."""

        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {
            "budget_analysis": message.content[0].text,
            "num_days": num_days,
            "daily_budget": budget / num_days,
            "sources": [r["url"] for r in search_results.get("results", [])]
        }
    
    def _format_search_results(self, results):
        """Format search results for Claude"""
        if "error" in results:
            return "No cost information available"
        
        formatted = []
        for r in results.get("results", []):
            formatted.append(f"- {r['title']}: {r['content'][:150]}...")
        return "\n".join(formatted)