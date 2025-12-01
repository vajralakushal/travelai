from anthropic import Anthropic
from src.utils.config import ANTHROPIC_API_KEY

class ItineraryAgent:
    def __init__(self, api_key=None, cost_tracker=None):
        self.client = Anthropic(api_key=api_key or ANTHROPIC_API_KEY)
        self.cost_tracker = cost_tracker
    def build_itinerary(self, destination: str, start_date: str, end_date: str, 
                   destination_info: str, activities: str, budget_info: str, 
                   season_context: str):
        """
        Synthesize all research into a day-by-day itinerary
        """
        from datetime import datetime, timedelta
        
        # Generate list of dates
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        num_days = (end - start).days + 1
        
        dates = []
        for i in range(num_days):
            date = start + timedelta(days=i)
            dates.append(date.strftime("%Y-%m-%d"))
        
        # Dynamic token allocation: ~400 tokens per day + 500 base
        max_tokens = min(500 + (num_days * 400), 4000)
        
        prompt = f"""You are an itinerary building agent. Create a detailed day-by-day travel plan.

    Destination: {destination}
    Dates: {start_date} to {end_date} ({num_days} days)

    Destination Overview:
    {destination_info[:300]}

    Season & Weather Context:
    {season_context}

    Available Activities:
    {activities}

    Budget Considerations:
    {budget_info[:200]}

    TASK: Create a day-by-day itinerary with the following structure for EACH day:

    **Day [X] - [Date] - [Day of Week]**

    **Morning (9am-12pm):**
    - [Activity name and location]
    - [Brief description and why it's scheduled in morning]
    - Estimated cost: $[amount]

    **Midday (12pm-5pm):**
    - [Activity name and location]
    - [Include lunch suggestion]
    - Estimated cost: $[amount]

    **Evening (5pm-10pm):**
    - [Activity name and location]
    - [Include dinner suggestion]
    - Estimated cost: $[amount]

    **Night (Optional, 10pm+):**
    - [Optional nightlife/relaxation activity]
    - Estimated cost: $[amount]

    **Day [X] Total Estimated Cost: $[sum]**

    IMPORTANT:
    - Balance indoor/outdoor activities based on season
    - Group activities by geographic proximity to minimize travel time
    - Include meal suggestions that match the area you're in
    - Vary the pace - don't overschedule
    - Consider typical opening hours
    - End each day with realistic daily cost estimate
    - Make it feel natural and enjoyable, not rushed
    - Be concise but specific

    Create the full {num_days}-day itinerary now. Keep each day's description focused and actionable."""

        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Log token usage (optional - for debugging)
        print(f"  ⚡ Tokens used - Input: {message.usage.input_tokens}, Output: {message.usage.output_tokens}")
        # Track usage
        if self.cost_tracker:
            self.cost_tracker.add_usage(message.usage.input_tokens, message.usage.output_tokens)
        return {
            "itinerary": message.content[0].text,
            "num_days": num_days,
            "dates": dates,
            "tokens_used": message.usage.output_tokens
        }