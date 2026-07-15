import streamlit as st
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import itertools

# Set page title and layout
st.set_page_config(page_title="AI B2B Route & Itinerary Optimizer", layout="centered")

# --- DATABASE OF POPULAR TOKYO SPOTS (For accurate time estimation) ---
SPOT_TIMES = {
    "sensoji temple": 1.5,
    "asakusa": 1.5,
    "tokyo skytree": 2.5,
    "shibuya": 2.0,
    "shibuya crossing": 1.0,
    "harajuku": 2.0,
    "meiji shrine": 1.5,
    "ueno park": 2.0,
    "shinjuku Gyoen": 1.5,
    "tokyo tower": 1.5,
    "akihabara": 2.5
}

def get_sightseeing_time(spot_name):
    name_clean = spot_name.lower().strip()
    for key, hours in SPOT_TIMES.items():
        if key in name_clean:
            return hours
    return 2.0  # Default 2 hours agar spot list mein na ho

st.title("🧙‍♂️ AI Itinerary & Route Optimizer")
st.subheader("Smartly sequence client days, check feasibility, and save hours of planning.")
st.write("---")

# --- INPUT SECTION ---
st.markdown("### 🏨 1. Hotel / Starting Point")
hotel_input = st.text_input("Enter Hotel Name or Area (e.g., Harajuku, Tokyo)", "Harajuku, Tokyo")

st.markdown("### 📍 2. Destinations to Visit (Add up to 4 spots)")
col1, col2 = st.columns(2)
spot1 = col1.text_input("Spot 1", "Ueno Park, Tokyo")
spot2 = col2.text_input("Spot 2", "Asakusa, Tokyo")
spot3 = col1.text_input("Spot 3", "Shibuya, Tokyo")
spot4 = col2.text_input("Spot 4", "Tokyo Skytree, Tokyo")

# Avg Travel Speed assumption (30 km/h inside city traffic/train transitions)
AVG_SPEED_KMH = 30 

if st.button("🔮 Optimize Route & Check Feasibility", type="primary"):
    spots = [s.strip() for s in [spot1, spot2, spot3, spot4] if s.strip()]
    
    if len(spots) < 2:
        st.error("Please enter at least 2 spots to optimize the route!")
    else:
        with st.spinner("Calculating smartest sequence and times..."):
            try:
                geolocator = Nominatim(user_agent="b2b_japan_itinerary_optimizer_v1")
                
                # Geocode Hotel
                hotel_loc = geolocator.geocode(hotel_input)
                if not hotel_loc:
                    st.error(f"Could not find location for Hotel: {hotel_input}")
                    st.stop()
                
                # Geocode Spots
                spot_locations = {}
                invalid_spots = []
                for s in spots:
                    loc = geolocator.geocode(s)
                    if loc:
                        spot_locations[s] = loc
                    else:
                        invalid_spots.append(s)
                
                if invalid_spots:
                    st.error(f"Could not find locations for: {', '.join(invalid_spots)}")
                    st.stop()
                
                # --- TSP ROUTE OPTIMIZATION LOGIC ---
                # Find best permutation of spots starting and ending at Hotel
                best_sequence = None
                min_total_distance = float('inf')
                
                spot_names = list(spot_locations.keys())
                for perm in itertools.permutations(spot_names):
                    current_distance = 0
                    # Hotel to first spot
                    first_spot = spot_locations[perm[0]]
                    current_distance += geodesic((hotel_loc.latitude, hotel_loc.longitude), (first_spot.latitude, first_spot.longitude)).kilometers
                    
                    # Distance between spots
                    for i in range(len(perm) - 1):
                        loc_a = spot_locations[perm[i]]
                        loc_b = spot_locations[perm[i+1]]
                        current_distance += geodesic((loc_a.latitude, loc_a.longitude), (loc_b.latitude, loc_b.longitude)).kilometers
                    
                    # Last spot back to Hotel
                    last_spot = spot_locations[perm[-1]]
                    current_distance += geodesic((last_spot.latitude, last_spot.longitude), (hotel_loc.latitude, hotel_loc.longitude)).kilometers
                    
                    if current_distance < min_total_distance:
                        min_total_distance = current_distance
                        best_sequence = perm
                
                # --- TIME & FEASIBILITY CALCULATION ---
                total_sightseeing_hours = sum(get_sightseeing_time(s) for s in spots)
                # Est. travel time based on distance and average speed + buffer for train/walking transitions
                total_travel_hours = (min_total_distance / AVG_SPEED_KMH) + (len(spots) * 0.25) 
                total_day_hours = round(total_sightseeing_hours + total_travel_hours, 1)
                
                # --- DISPLAY RESULTS ---
                st.write("---")
                st.markdown("### 🗺️ Optimized Smart Sequence:")
                
                # Displaying the sequence path clearly
                path_str = f"🏨 **{hotel_input.split(',')[0]} (Hotel)**"
                for s in best_sequence:
                    path_str += f" ➔ 📍 {s.split(',')[0]}"
                path_str += f" ➔ 🏨 **{hotel_input.split(',')[0]} (Hotel)**"
                
                st.info(path_str)
                
                # Metrics
                col_m1, col_m2, col_m3 = st.columns(3)
                col_m1.metric("Total Travel Distance", f"{round(min_total_distance, 2)} KM")
                col_m2.metric("Est. Travel Time", f"{round(total_travel_hours, 1)} Hours")
                col_m3.metric("Sightseeing Time", f"{round(total_sightseeing_hours, 1)} Hours")
                
                st.markdown(f"#### Total Estimated Day Duration: **{total_day_hours} Hours**")
                
                # Feasibility Check Warning Cards
                if total_day_hours > 11:
                    st.error(f"❌ **Not Recommended (Feasibility: Overloaded):** This day takes around {total_day_hours} hours. It will be exhausting for the clients. We highly recommend dropping 1 spot.")
                elif total_day_hours > 8.5:
                    st.warning(f"⚠️ **Tight Schedule (Feasibility: Heavy Day):** This day takes around {total_day_hours} hours. It is doable but will be a bit rushing/tiring for families or senior citizens.")
                else:
                    st.success(f"✅ **Highly Doable! (Feasibility: Perfect):** This route takes around {total_day_hours} hours. Perfect pace for a great holiday experience without backtracking!")
                    
            except Exception as e:
                st.error(f"Error optimizing route: {str(e)}")
