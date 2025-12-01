from typing import TypedDict, Annotated
import operator
from langgraph.graph import StateGraph, END
from src.agents import DestinationAgent, ActivityAgent
from src.agents.budget_agent import BudgetAgent
from src.agents.itinerary_agent import ItineraryAgent
from src.utils import CostTracker

class TravelPlanState(TypedDict):
    """State passed between agents"""
    destination: str
    start_date: str
    end_date: str
    budget: float
    interests: list
    
    # Agent outputs
    destination_info: dict
    activities_info: dict
    budget_info: dict
    itinerary_info: dict
    
    # Final output
    final_plan: dict
    error: str

class TravelCoordinator:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.cost_tracker = CostTracker()
        self.dest_agent = DestinationAgent(api_key, self.cost_tracker)
        self.activity_agent = ActivityAgent(api_key, self.cost_tracker)
        self.budget_agent = BudgetAgent(api_key, self.cost_tracker)
        self.itinerary_agent = ItineraryAgent(api_key, self.cost_tracker)
        
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _build_graph(self):
        """Build LangGraph workflow"""
        workflow = StateGraph(TravelPlanState)
        
        # Add nodes
        workflow.add_node("research_destination", self._research_destination)
        workflow.add_node("find_activities", self._find_activities)
        workflow.add_node("analyze_budget", self._analyze_budget)
        workflow.add_node("build_itinerary", self._build_itinerary)
        
        # Define edges
        workflow.set_entry_point("research_destination")
        workflow.add_edge("research_destination", "find_activities")
        workflow.add_edge("find_activities", "analyze_budget")
        workflow.add_edge("analyze_budget", "build_itinerary")
        workflow.add_edge("build_itinerary", END)
        
        return workflow.compile()
    
    def _research_destination(self, state: TravelPlanState) -> TravelPlanState:
        """Node: Research destination"""
        print("🔍 Researching destination...")
        result = self.dest_agent.research(state["destination"], state["interests"])
        state["destination_info"] = result
        return state
    
    def _find_activities(self, state: TravelPlanState) -> TravelPlanState:
        """Node: Find activities"""
        print("🎯 Finding activities...")
        result = self.activity_agent.find_activities(
            state["destination"],
            state["interests"],
            state["start_date"],
            state["end_date"],
            state["destination_info"].get("coordinates", {})
        )
        state["activities_info"] = result
        return state
    
    def _analyze_budget(self, state: TravelPlanState) -> TravelPlanState:
        """Node: Analyze budget"""
        print("💰 Analyzing budget...")
        result = self.budget_agent.estimate_costs(
            state["destination"],
            state["start_date"],
            state["end_date"],
            state["budget"],
            state["activities_info"].get("activities", "")
        )
        state["budget_info"] = result
        return state
    
    def _build_itinerary(self, state: TravelPlanState) -> TravelPlanState:
        """Node: Build final itinerary"""
        print("📅 Building itinerary...")
        result = self.itinerary_agent.build_itinerary(
            state["destination"],
            state["start_date"],
            state["end_date"],
            state["destination_info"].get("research", ""),
            state["activities_info"].get("activities", ""),
            state["budget_info"].get("budget_analysis", ""),
            state["activities_info"].get("season_context", "")
        )
        
        # Compile final plan
        state["final_plan"] = {
            "destination": state["destination"],
            "dates": f"{state['start_date']} to {state['end_date']}",
            "budget": state["budget"],
            "destination_overview": state["destination_info"].get("research", ""),
            "destination_image": state["destination_info"].get("image", {}),
            "season_context": state["activities_info"].get("season_context", ""),
            "budget_analysis": state["budget_info"].get("budget_analysis", ""),
            "itinerary": result.get("itinerary", ""),
            "num_days": result.get("num_days", 0)
        }
        
        return state
    
    def plan_trip(self, destination: str, start_date: str, end_date: str, 
                  budget: float, interests: list):
        """
        Main entry point - orchestrate all agents to create travel plan
        """
        # Validate trip duration
        from datetime import datetime
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        num_days = (end - start).days + 1
        
        if num_days > 7:
            return {
                "error": "Trip duration exceeds maximum of 7 days per city. Please shorten your dates or plan multiple single-city trips."
            }
        
        if num_days < 1:
            return {
                "error": "Invalid date range. End date must be after start date."
            }
        initial_state = {
            "destination": destination,
            "start_date": start_date,
            "end_date": end_date,
            "budget": budget,
            "interests": interests,
            "destination_info": {},
            "activities_info": {},
            "budget_info": {},
            "itinerary_info": {},
            "final_plan": {},
            "error": ""
        }
        
        try:
            # Run the graph
            final_state = self.graph.invoke(initial_state)
            # Add cost tracking info
            final_state["final_plan"]["usage_stats"] = self.cost_tracker.get_summary()
            return final_state["final_plan"]
        except Exception as e:
            print(f"❌ Error in coordination: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}