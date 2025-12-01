from src.agents import DestinationAgent, ActivityAgent

# Test Destination Agent
print("=" * 50)
print("Testing Destination Agent...")
print("=" * 50)
dest_agent = DestinationAgent()
dest_result = dest_agent.research("Tokyo", ["food", "culture", "temples"])
print(dest_result.get("research", "Error"))
print(f"\nCoordinates: {dest_result.get('coordinates', {})}")
print()

# Test Activity Agent with destination coordinates
print("=" * 50)
print("Testing Activity Agent...")
print("=" * 50)
activity_agent = ActivityAgent()
activity_result = activity_agent.find_activities(
    "Tokyo", 
    ["food", "culture", "temples"], 
    "2025-06-15",  # Rainy season in Tokyo!
    "2025-06-20",
    dest_result.get('coordinates', {"lat": 35.6762, "lon": 139.6503})
)
print(f"Season Context:\n{activity_result.get('season_context', 'N/A')}\n")
print(f"Activities:\n{activity_result.get('activities', 'Error')}")