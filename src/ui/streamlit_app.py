import streamlit as st
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.agents import TravelCoordinator
from src.database import DatabaseManager
from src.utils.config import validate_config

# Page config
st.set_page_config(
    page_title="TravelAI - AI Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1E88E5;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1E88E5;
        color: white;
        font-size: 1.1rem;
        padding: 0.75rem;
        border-radius: 8px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #1565C0;
    }
    .trip-card {
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #ddd;
        margin-bottom: 1rem;
        background-color: #f9f9f9;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'trip_plan' not in st.session_state:
    st.session_state.trip_plan = None
if 'generating' not in st.session_state:
    st.session_state.generating = False
if 'db' not in st.session_state:
    st.session_state.db = DatabaseManager()

# Header
st.markdown('<div class="main-header">✈️ WanderAI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Your AI-Powered Travel Planner with Multi-Agent Intelligence</div>', unsafe_allow_html=True)

# Sidebar - API Key Configuration
with st.sidebar:
    st.header("⚙️ Settings")
    
    api_key_option = st.radio(
        "API Key",
        ["Use demo key", "Use my own key"],
        help="Demo key has daily limits. Use your own key for unlimited access."
    )
    
    user_api_key = None
    if api_key_option == "Use my own key":
        user_api_key = st.text_input(
            "Anthropic API Key",
            type="password",
            help="Your API key is only used for this session and never stored."
        )
        st.caption("🔒 Your key is never stored or logged")
    
    st.divider()
    
    # Past trips
    st.header("📚 Past Trips")
    past_trips = st.session_state.db.get_all_trips()
    
    if past_trips:
        for trip in past_trips[:5]:  # Show last 5 trips
            with st.expander(f"🌍 {trip['destination']} - {trip['start_date']}"):
                st.write(f"**Dates:** {trip['start_date']} to {trip['end_date']}")
                st.write(f"**Budget:** ${trip['budget']}")
                if st.button(f"Load Trip", key=f"load_{trip['id']}"):
                    import json
                    st.session_state.trip_plan = json.loads(trip['itinerary_json'])
                    st.rerun()
    else:
        st.info("No past trips yet. Create your first itinerary!")

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.header("🗺️ Plan Your Trip")
    
    # Input form
    with st.form("trip_form"):
        destination = st.text_input(
            "Destination City",
            placeholder="e.g., Tokyo, Paris, New York",
            help="Enter a single city name"
        )
        
        col_date1, col_date2 = st.columns(2)
        with col_date1:
            start_date = st.date_input(
                "Start Date",
                value=datetime.now() + timedelta(days=30),
                min_value=datetime.now()
            )
        with col_date2:
            end_date = st.date_input(
                "End Date",
                value=datetime.now() + timedelta(days=34),
                min_value=datetime.now()
            )
        
        budget = st.number_input(
            "Budget (USD)",
            min_value=100,
            max_value=50000,
            value=2000,
            step=100,
            help="Total budget for accommodation, food, activities, and transportation"
        )
        
        interests = st.multiselect(
            "Your Interests",
            ["Food & Dining", "Culture & History", "Nature & Outdoors", "Shopping", 
             "Nightlife", "Art & Museums", "Adventure", "Photography", "Relaxation", "Architecture"],
            default=["Food & Dining", "Culture & History"],
            help="Select up to 5 interests (recommended)"
        )
        
        submitted = st.form_submit_button("🚀 Generate Itinerary", use_container_width=True)
        
        if submitted:
            # Validation
            if not destination:
                st.error("❌ Please enter a destination")
            elif len(interests) == 0:
                st.error("❌ Please select at least one interest")
            elif len(interests) > 5:
                st.error("❌ Please select no more than 5 interests")
            elif end_date <= start_date:
                st.error("❌ End date must be after start date")
            else:
                st.session_state.generating = True
                st.rerun()

with col2:
    st.header("ℹ️ How It Works")
    st.markdown("""
    **WanderAI uses multiple AI agents:**
    
    1. 🔍 **Destination Agent**
       - Researches your destination
       - Finds top attractions
    
    2. 🎯 **Activity Agent**
       - Matches activities to your interests
       - Considers seasonal weather
    
    3. 💰 **Budget Agent**
       - Estimates realistic costs
       - Provides money-saving tips
    
    4. 📅 **Itinerary Agent**
       - Builds day-by-day plan
       - Optimizes routes and timing
    
    **Limits:**
    - Max 7 days per city
    - Single-city trips only
    """)

# Generate itinerary
if st.session_state.generating:
    st.session_state.generating = False
    
    with st.spinner("🤖 AI agents are working on your itinerary..."):
        # Progress indicator
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("🔍 Researching destination...")
        progress_bar.progress(25)
        
        # Create coordinator
        coordinator = TravelCoordinator(api_key=user_api_key)
        
        status_text.text("🎯 Finding activities...")
        progress_bar.progress(50)
        
        # Generate trip
        trip_plan = coordinator.plan_trip(
            destination=destination,
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            budget=float(budget),
            interests=interests
        )
        
        status_text.text("💰 Analyzing budget...")
        progress_bar.progress(75)
        
        if "error" in trip_plan:
            st.error(f"❌ Error: {trip_plan['error']}")
        else:
            st.session_state.trip_plan = trip_plan
            
            # Save to database
            import json
            st.session_state.db.save_trip(
                destination=destination,
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
                budget=float(budget),
                interests=interests,
                itinerary=trip_plan
            )
            
            status_text.text("✅ Complete!")
            progress_bar.progress(100)
        
        st.rerun()

# Display results
if st.session_state.trip_plan and "error" not in st.session_state.trip_plan:
    st.divider()
    
    plan = st.session_state.trip_plan
    
    # Hero section with image
    if plan.get("destination_image", {}).get("url"):
        st.image(
            plan["destination_image"]["url"],
            caption=f"Photo by {plan['destination_image'].get('photographer', 'Unknown')}",
            use_column_width=True
        )
    
    st.header(f"🌍 {plan['destination']}")
    st.subheader(f"📅 {plan['dates']} • 💰 ${plan['budget']} budget")
    
    # Overview section
    with st.expander("📖 Destination Overview", expanded=True):
        st.write(plan['destination_overview'])
    
    # Season context
    with st.expander("🌤️ Season & Weather Context"):
        st.info(plan['season_context'])
    
    # Budget analysis
    with st.expander("💵 Budget Analysis"):
        st.write(plan['budget_analysis'])
    
    # Main itinerary
    st.header("📋 Your Itinerary")
    st.markdown(plan['itinerary'])
    
    # Usage stats
    if 'usage_stats' in plan:
        with st.expander("⚡ API Usage Stats"):
            stats = plan['usage_stats']
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Input Tokens", f"{stats['input_tokens']:,}")
            with col2:
                st.metric("Output Tokens", f"{stats['output_tokens']:,}")
            with col3:
                st.metric("Estimated Cost", f"${stats['estimated_cost_usd']:.4f}")
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Generate New Trip", use_container_width=True):
            st.session_state.trip_plan = None
            st.rerun()
    with col2:
        st.download_button(
            label="📥 Download Itinerary (Text)",
            data=plan['itinerary'],
            file_name=f"{plan['destination']}_itinerary.txt",
            mime="text/plain",
            use_container_width=True
        )

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    Built with ❤️ using Claude, LangGraph, and Streamlit | 
    <a href='https://github.com/vajralakushal/travelai' target='_blank'>View on GitHub</a>
</div>
""", unsafe_allow_html=True)