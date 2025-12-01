from src.agents import TravelCoordinator

print("=" * 60)
print("TESTING FULL TRAVEL PLANNER SYSTEM")
print("=" * 60)

coordinator = TravelCoordinator()

trip_plan = coordinator.plan_trip(
    destination="Lisbon",
    start_date="2025-06-15",
    end_date="2025-06-18",  # 4 days - well under the 7-day limit
    budget=2000,
    interests=["food", "culture", "nightlife", "photography"]
)

print("\n" + "=" * 60)
print("FINAL TRAVEL PLAN")
print("=" * 60)

if "error" in trip_plan:
    print(f"❌ Error: {trip_plan['error']}")
else:
    print(f"\n📍 Destination: {trip_plan['destination']}")
    print(f"📅 Dates: {trip_plan['dates']}")
    print(f"💰 Budget: ${trip_plan['budget']}")
    print(f"\n🌍 Overview:\n{trip_plan['destination_overview'][:200]}...")
    print(f"\n🌤️ Season Context:\n{trip_plan['season_context'][:150]}...")
    print(f"\n💵 Budget Analysis:\n{trip_plan['budget_analysis'][:200]}...")
    print(f"\n📋 ITINERARY:\n{trip_plan['itinerary']}")
    
    # Show usage stats
    if "usage_stats" in trip_plan:
        stats = trip_plan["usage_stats"]
        print(f"\n" + "=" * 60)
        print("API USAGE STATS")
        print("=" * 60)
        print(f"Input tokens: {stats['input_tokens']:,}")
        print(f"Output tokens: {stats['output_tokens']:,}")
        print(f"Estimated cost: ${stats['estimated_cost_usd']:.4f}")
        print(f"Trips remaining in $20 budget: ~{stats['trips_remaining_in_20_budget']}")