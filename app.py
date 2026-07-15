import streamlit as st
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import requests

# Set page title and layout
st.set_page_config(page_title="B2B Japan & Global Route Planner", layout="centered")

# --- DATABASE OF POPULAR JAPAN TRANSIT ROUTES ---
JAPAN_ROUTES = {
    ("tokyo", "kyoto"): {
        "mode": "🚄 Shinkansen (Bullet Train - Nozomi)",
        "duration": "2h 15m",
        "price_yen": 14170,
        "frequency": "Every 10-15 minutes"
    },
    ("kyoto", "tokyo"): {
        "mode": "🚄 Shinkansen (Bullet Train - Nozomi)",
        "duration": "2h 15m",
        "price_yen": 14170,
        "frequency": "Every 10-15 minutes"
    },
    ("tokyo", "osaka"): {
        "mode": "🚄 Shinkansen (Bullet Train - Nozomi)",
        "duration": "2h 30m",
        "price_yen": 14720,
        "frequency": "Every 10-15 minutes"
    },
    ("osaka", "tokyo"): {
        "mode": "🚄 Shinkansen (Bullet Train - Nozomi)",
        "duration": "2h 30m",
        "price_yen": 14720,
        "frequency": "Every 10-15 minutes"
    },
    ("kyoto", "osaka"): {
        "mode": "🚆 JR Special Rapid Service",
        "duration": "30 mins",
        "price_yen": 580,
        "frequency": "Every 8 minutes"
    },
    ("osaka", "kyoto"): {
        "mode": "🚆 JR Special Rapid Service",
        "duration": "30 mins",
        "price_yen": 580,
        "frequency": "Every 8 minutes"
    },
    ("tokyo", "hiroshima"): {
        "mode": "🚄 Shinkansen (Bullet Train)",
        "duration": "4h 0m",
        "price_yen": 19440,
        "frequency": "Every 30 minutes"
    },
    ("tokyo", "hakone"): {
        "mode": "🚆 Odakyu Romancecar",
        "duration": "1h 15m",
        "price_yen": 2470,
        "frequency": "Every 30 minutes"
    }
}

# --- UI Header ---
st.title("🗺️ B2B Global Route & Japan Transit Planner")
st.subheader("Instantly fetch driving distances, air paths, and Japan Shinkansen details.")
st.write("---")

# Input Fields
origin_city = st.text_input("Enter Starting City", "Tokyo, Japan")
dest_city = st.text_input("Enter Destination City", "Kyoto, Japan")

# Your RapidAPI Key
API_KEY = "3f140aa7b0mshd4b67b160e55987p15eb64jsnc0654f962765"

if st.button("Calculate Route & Transit", type="primary"):
    with st.spinner("Analyzing routes..."):
        try:
            # Step 1: Geocode names
            geolocator = Nominatim(user_agent="b2b_travel_planner_app_v4")
            loc1 = geolocator.geocode(origin_city)
            loc2 = geolocator.geocode(dest_city)
            
            if loc1 and loc2:
                # Check if it's a known Japan route
                city1_clean = origin_city.lower().split(",")[0].strip()
                city2_clean = dest_city.lower().split(",")[0].strip()
                route_key = (city1_clean, city2_clean)
                
                # --- SPECIAL JAPAN TRANSIT SECTION ---
                if route_key in JAPAN_ROUTES:
                    transit = JAPAN_ROUTES[route_key]
                    usd_price = round(transit["price_yen"] / 150, 2) # Est. conversion rate
                    
                    st.success("🇯🇵 Japan Transit Option Found!")
                    
                    # Corrected Parameter here (unsafe_allow_html=True)
                    st.markdown(f"""
                    <div style="background-color:#f0f8ff; padding:20px; border-radius:10px; border-left: 5px solid #1e90ff; color:#333;">
                        <h4 style="color:#1e90ff; margin-top:0;">🚄 Recommended Route for Clients:</h4>
                        <p><strong>Mode:</strong> {transit['mode']}</p>
                        <p><strong>Travel Time:</strong> {transit['duration']}</p>
                        <p><strong>Frequency:</strong> {transit['frequency']}</p>
                        <p><strong>Est. Ticket Price:</strong> ¥{transit['price_yen']:,} (~${usd_price} USD) per person</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.write("")
                
                # --- GLOBAL ROUTING FALLBACKS ---
                origin_coords = f"{loc1.latitude},{loc1.longitude}"
                dest_coords = f"{loc2.latitude},{loc2.longitude}"
                
                # Try Driving Route API
                url = "https://trueway-directions2.p.rapidapi.com/FindDrivingRoute"
                querystring = {"stops": f"{origin_coords};{dest_coords}"}
                headers = {
                    "x-rapidapi-key": API_KEY,
                    "x-rapidapi-host": "trueway-directions2.p.rapidapi.com"
                }
                
                response = requests.get(url, headers=headers, params=querystring)
                data = response.json()
                
                if 'route' in data:
                    route_info = data['route']
                    distance_km = round(route_info['distance'] / 1000, 2)
                    duration_mins = int(route_info['duration'] / 60)
                    hours = duration_mins // 60
                    mins = duration_mins % 60
                    
                    st.success("🚗 Driving Route Details:")
                    col1, col2 = st.columns(2)
                    col1.metric(label="📍 Driving Distance", value=f"{distance_km} KM")
                    col2.metric(label="⏱️ Driving Time", value=f"{hours}h {mins}m" if hours > 0 else f"{mins} mins")
                else:
                    # Straight Line distance calculation
                    coord1 = (loc1.latitude, loc1.longitude)
                    coord2 = (loc2.latitude, loc2.longitude)
                    aerial_distance = round(geodesic(coord1, coord2).kilometers, 2)
                    
                    st.warning("ℹ️ Driving route unavailable, showing Straight Line distance:")
                    col1, col2 = st.columns(2)
                    col1.metric(label="✈️ Air / Straight Distance", value=f"{aerial_distance} KM")
                    col2.metric(label="⏱️ Est. Direct Flight / Transit", value=f"~{round(aerial_distance/800, 1)} hrs" if aerial_distance > 500 else "Short Transit")
                    
            else:
                st.error("Could not find one or both of the locations.")
                
        except Exception as e:
            st.error(f"Error: {str(e)}")