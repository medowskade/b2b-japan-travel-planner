import streamlit as st
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import itertools

# Set page title and layout for a professional SaaS feel
st.set_page_config(page_title="Executive Travel Logistics Optimizer", layout="centered")

# Custom CSS for high-end minimalist corporate styling
st.markdown("""
<style>
    .reportview-container { background: #fafafa; }
    .stButton>button { width: 100%; border-radius: 4px; font-weight: 600; }
    .metric-box { background-color: #ffffff; padding: 15px; border-radius: 6px; border: 1px solid #e0e0e0; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- DATABASE OF POPULAR TOKYO SPOTS (For accurate exploration time estimation) ---
SPOT_TIMES = {
    "sensoji temple": 1.5, "asakusa": 1.5, "tokyo skytree": 2.5,
    "shibuya": 2.0, "shibuya crossing": 1.0, "harajuku": 2.0,
    "meiji shrine": 1.5, "ueno park": 2.0, "shinjuku gyoen": 1.5,
    "tokyo tower": 1.5, "akihabara": 2.5
}

def get_exploration_time(spot_name):
    name_clean = spot_name.lower().strip()
    for key, hours in SPOT_TIMES.items():
        if key in name_clean:
            return hours
    return 2.0  # Default allocated exploration time

st.title("Executive Route & Itinerary Logistics Optimizer")
st.subheader("Enterprise-grade daily waypoint sequencing and operational feasibility engine.")
st.write("---")

# --- GLOBAL GEOGRAPHIC CONTEXT ---
st.markdown("### Regional Search Optimization Context")
search_context = st.selectbox(
    "Select Destination Hub (Ensures precise matching for hotels, cafes, and local venues)",
    ["Tokyo, Japan", "Kyoto, Japan", "Osaka, Japan", "Hiroshima, Japan"]
)

# --- SECTION 1: POINT OF ORIGIN ---
st.markdown("### 1. Point of Origin (Lodging / Base Location)")
hotel_input = st.text_input("Specify accommodation node or primary starting point (e.g., Keio Plaza Hotel)", "Keio Plaza Hotel")

# --- SECTION 2: DYNAMIC WAYPOINT CONFIGURATION ---
st.markdown("### 2. Daily Waypoint Configuration")

# Initialize session state to dynamically track number of destinations
if "num_destinations" not in st.session_state:
    st.session_state.num_destinations = 3

# UI Buttons to dynamically add or remove rows cleanly
col_btn1, col_btn2 = st.columns([1, 4])
if col_btn1.button("➕ Add Waypoint"):
    st.session_state.num_destinations += 1
if col_btn2.button("➖ Remove Waypoint") and st.session_state.num_destinations > 2:
    st.session_state.num_destinations -= 1

# Generate input fields dynamically based on session state
waypoints = []
for i in range(st.session_state.num_destinations):
    default_val = ""
    if i == 0: default_val = "Ueno Park"
    if i == 1: default_val = "Asakusa"
    if i == 2: default_val = "Shibuya"
    
    val = st.text_input(f"Destination Waypoint {i+1}", value=default_val, key=f"waypoint_{i}")
    waypoints.append(val)

# Average urban transit speed parameter
AVG_SPEED_KMH = 30 

st.write("---")

if st.button("Analyze Transit Logistics & Evaluate Feasibility", type="primary"):
    # Filter out empty inputs
    filtered_spots = [w.strip() for w in waypoints if w.strip()]
    
    if len(filtered_spots) < 2:
        st.error("Logistical Requirement: Please specify a minimum of 2 destinations to perform sequence optimization.")
    else:
        with st.spinner("Executing sequence permutations and analyzing spatial constraints..."):
            try:
                geolocator = Nominatim(user_agent="b2b_premium_logistics_optimizer_v2")
                
                # Smart Query Appending: Attaching the city/country context to local venues automatically
                refined_hotel_query = f"{hotel_input}, {search_context}"
                hotel_loc = geolocator.geocode(refined_hotel_query)
                
                if not hotel_loc:
                    st.error(f"Geocoding Failure: Unable to resolve unique coordinates for Base Location: '{hotel_input}'. Please specify the exact name or adding vicinity details.")
                    st.stop()
                
                # Resolve coordinates for all custom waypoints safely
                spot_locations = {}
                invalid_spots = []
                for s in filtered_spots:
                    refined_spot_query = f"{s}, {search_context}"
                    loc = geolocator.geocode(refined_spot_query)
                    if loc:
                        spot_locations[s] = loc
                    else:
                        invalid_spots.append(s)
                
                if invalid_spots:
                    st.error(f"Geocoding Failure: Unable to locate coordinates for the following nodes within {search_context}: {', '.join(invalid_spots)}")
                    st.stop()
                
                # --- TSP ROUTE OPTIMIZATION ALGORITHM ---
                best_sequence = None
                min_total_distance = float('inf')
                spot_names = list(spot_locations.keys())
                
                for perm in itertools.permutations(spot_names):
                    current_distance = 0
                    first_spot = spot_locations[perm[0]]
                    current_distance += geodesic((hotel_loc.latitude, hotel_loc.longitude), (first_spot.latitude, first_spot.longitude)).kilometers
                    
                    for i in range(len(perm) - 1):
                        loc_a = spot_locations[perm[i]]
                        loc_b = spot_locations[perm[i+1]]
                        current_distance += geodesic((loc_a.latitude, loc_a.longitude), (loc_b.latitude, loc_b.longitude)).kilometers
                    
                    last_spot = spot_locations[perm[-1]]
                    current_distance += geodesic((last_spot.latitude, last_spot.longitude), (hotel_loc.latitude, hotel_loc.longitude)).kilometers
                    
                    if current_distance < min_total_distance:
                        min_total_distance = current_distance
                        best_sequence = perm
                
                # --- METRIC COMPUTATIONS ---
                allocated_exploration_hours = sum(get_exploration_time(s) for s in filtered_spots)
                projected_transit_hours = (min_total_distance / AVG_SPEED_KMH) + (len(filtered_spots) * 0.25) 
                aggregate_operational_hours = round(allocated_exploration_hours + projected_transit_hours, 1)
                
                # --- DISPLAY PREMIUM OUTPUTS ---
                st.markdown("### Optimal Route Sequence")
                
                path_str = f"Base Location: **{hotel_input}**"
                for s in best_sequence:
                    path_str += f" ➔ Node: {s}"
                path_str += f" ➔ Return Node: **{hotel_input}**"
                
                st.info(path_str)
                
                # Render Clean Corporate Metric Columns
                st.markdown("<br>", unsafe_allow_html=True)
                m_col1, m_col2, m_col3 = st.columns(3)
                m_col1.markdown(f"<div class='metric-box'><p style='color:#666;margin:0;'>Cumulative Distance</p><h3>{round(min_total_distance, 2)} KM</h3></div>", unsafe_allow_html=True)
                m_col2.markdown(f"<div class='metric-box'><p style='color:#666;margin:0;'>Projected Transit Duration</p><h3>{round(projected_transit_hours, 1)} Hrs</h3></div>", unsafe_allow_html=True)
                m_col3.markdown(f"<div class='metric-box'><p style='color:#666;margin:0;'>Allocated Exploration Time</p><h3>{round(allocated_exploration_hours, 1)} Hrs</h3></div>", unsafe_allow_html=True)
                
                st.markdown(f"<p style='font-size:18px; font-weight:600; margin-top:20px;'>Aggregate Daily Operational Hours: {aggregate_operational_hours} Hours</p>", unsafe_allow_html=True)
                
                # Premium Clean Custom Advisories
                if aggregate_operational_hours > 11:
                    st.markdown(f"""
                    <div style="background-color:#fff5f5; padding:20px; border-radius:6px; border-left: 5px solid #e53e3e; color:#2d3748;">
                        <h4 style="color:#c53030; margin-top:0; font-weight:600;">⚠️ Operational Advisory: Schedule Overload Detected</h4>
                        <p style="margin:0;">The projected daily itinerary spans approximately {aggregate_operational_hours} hours. This duration significantly exceeds standard client comfort thresholds and may lead to logistical fatigue. To optimize traveler satisfaction and ensure a sustainable pace, we recommend omitting at least one destination from this specific day.</p>
                    </div>
                    """, unsafe_allow_html=True)
                elif aggregate_operational_hours > 8.5:
                    st.markdown(f"""
                    <div style="background-color:#fffaf0; padding:20px; border-radius:6px; border-left: 5px solid #dd6b20; color:#2d3748;">
                        <h4 style="color:#dd6b20; margin-top:0; font-weight:600;">ℹ️ Operational Notice: High-Density Schedule</h4>
                        <p style="margin:0;">The projected itinerary demands {aggregate_operational_hours} hours of active operations. While execution is highly feasible, this schedule offers a tighter pacing structure. It may feel slightly accelerated for family demographics or senior citizens.</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background-color:#f0fff4; padding:20px; border-radius:6px; border-left: 5px solid #38a169; color:#2d3748;">
                        <h4 style="color:#2f855a; margin-top:0; font-weight:600;">✅ Logistics Verification: Schedule Optimized</h4>
                        <p style="margin:0;">The projected daily itinerary is highly feasible, spanning an estimated {aggregate_operational_hours} hours. This schedule offers an optimal balance of transit efficiency and generous exploration time, ensuring an exceptional and comfortable client experience.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
            except Exception as e:
                st.error(f"System Exception during optimization sequence: {str(e)}")
