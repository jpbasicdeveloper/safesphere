import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import re
import overpy
from geopy.distance import geodesic
import geocoder
from geopy.geocoders import Nominatim
import requests
from streamlit_option_menu import option_menu
import seaborn as sns
import matplotlib.pyplot as plt






st.set_page_config(page_title="SafeSphere", layout="wide")

st.title("🚨 SafeSphere")
st.title("Stay informed. Stay prepared. Stay safe.")
st.write("**Stay informed and prepared for emergencies in your area!**")

# Create two rows with two columns each
#col1, col2 = st.columns(2)

def realTimeAlerts():


    # List of 50 U.S. states
        # Dictionary mapping full state names to their 2-letter abbreviations
    state_to_code = {
        "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
        "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
        "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
        "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
        "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
        "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN",
        "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE",
        "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ",
        "New Mexico": "NM", "New York": "NY", "North Carolina": "NC",
        "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR",
        "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
        "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
        "Vermont": "VT", "Virginia": "VA", "Washington": "WA",
        "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"
    }
    
    # Add a placeholder option at the top
    options = ["-- Select a State --"] +  list(state_to_code.keys())
    
    
    state = st.selectbox("Select your state:", options)

    # Convert to 2-letter code
    if state != "-- Select a State --":
        state_code = state_to_code[state]
        st.write(f"You selected **{state}** ({state_code})")
    else:
        st.write("Please select a state to continue.")  

    if st.button("Get Alerts"):
        url = f"https://api.weather.gov/alerts/active?area={state_code.upper()}"
        response = requests.get(url)
        data = response.json()
        alerts = data.get("features", [])
        if alerts:
            for alert in alerts[:5]:
                st.subheader(alert["properties"]["headline"])
                st.write(alert["properties"]["description"])
        else:
            st.write("No active alerts for this area.")


def emergencyChecklist():
    st.header("Emergency Preparedness Checklist")
    checklist = [
       "Water (one gallon per person per day for at least three days)",
       "Non-perishable food (three-day supply)",
       "Battery-powered or hand crank radio",
       "Flashlight and extra batteries",
       "First aid kit",
       "Whistle (to signal for help)",
       "Dust mask (to help filter contaminated air)",
       "Plastic sheeting and duct tape (for shelter)",
       "Moist towelettes, garbage bags, and plastic ties (for personal sanitation)",
       "Wrench or pliers (to turn off utilities)",
       "Manual can opener (for food)",
       "Local maps",
       "Cell phone with chargers and backup battery"
    ]
    for item in checklist:
       st.checkbox(item)


#col3, col4 = st.columns(2)

def helpCenters():
    
    def find_help_centers(lat, lon, radius_km=5):
        api = overpy.Overpass()
        query = f"""
        [out:json];
        (
          node["amenity"="hospital"](around:{radius_km * 1000},{lat},{lon});
          node["amenity"="police"](around:{radius_km * 1000},{lat},{lon});
          node["amenity"="fire_station"](around:{radius_km * 1000},{lat},{lon});
          node["amenity"="pharmacy"](around:{radius_km * 1000},{lat},{lon});
          node["amenity"="shelter"](around:{radius_km * 1000},{lat},{lon});
        );
        out body;
        """

        result = api.query(query)
        #st.write(result.nodes)
        centers = []
        for node in result.nodes:
            st.write(node.tags)
            tags = node.tags
            
            distance = geodesic((lat, lon), (node.lat, node.lon)).km
            centers.append({
                "name": node.tags.get("name", "Unknown"),
                "type": node.tags.get("amenity", "Unknown"),
                "lat": node.lat,
                "lon": node.lon,
                "distance_km": round(distance, 2)
            })

        return sorted(centers, key=lambda x: x["distance_km"])


    def find_help_centers_updated(lat, lon, radius_km=5):
        api = overpy.Overpass()
        query = f"""
        [out:json];
        (
          node["amenity"="hospital"](around:{radius_km * 1000},{lat},{lon});
          node["amenity"="police"](around:{radius_km * 1000},{lat},{lon});
          node["amenity"="fire_station"](around:{radius_km * 1000},{lat},{lon});
          node["amenity"="pharmacy"](around:{radius_km * 1000},{lat},{lon});
          node["amenity"="shelter"](around:{radius_km * 1000},{lat},{lon});
        );
        out body;
        """

        result = api.query(query)
        
        centers = []
        for node in result.nodes:
            #st.write(node.tags)
            tags = node.tags

            # Construct address from available tags
            address_parts = [
                tags.get('addr:housenumber'),
                tags.get('addr:street'),
                tags.get('addr:postcode'),
                tags.get('addr:city')
            ]
            address = ', '.join([part for part in address_parts if part])
            if not address:
                address = "Address not available"
            
            
            distance = geodesic((lat, lon), (node.lat, node.lon)).km
            centers.append({
                "name": node.tags.get("name", "Unknown"),
                "type": node.tags.get("amenity", "Unknown"),
                "lat": node.lat,
                "lon": node.lon,
                "address": address,
                "distance_km": round(distance, 2)
            })

        return sorted(centers, key=lambda x: x["distance_km"])

    def get_city_from_coords(lat, lon):
        geolocator = Nominatim(user_agent="city_lookup")
        try:
            location = geolocator.reverse((lat, lon), language="en")
        
            if location and "address" in location.raw:
                address = location.raw["address"]
                city = address.get("city") or address.get("town") or address.get("village") or address.get("county")
                return city
            return "City not found"
        except (GeocoderUnavailable, GeocoderTimedOut) as e:
            return "City not found"
            


    if "user_location" not in st.session_state:
        g = geocoder.ip('me')
        #if g.ok:
            #st.session_state["user_location"] = tuple(g.latlng)
        #else:
            #st.session_state["user_location"] = (40.7128, -74.0060) 

    st.session_state["user_location"] = (37.3382, -121.8863)
    st.header(f"🆘 Nearby Help Centers in city")
    #st.session_state["user_location"]
    user_lat, user_lon = st.session_state["user_location"]
    help_centers = find_help_centers_updated(user_lat, user_lon)

    city = get_city_from_coords(user_lat, user_lon)
    st.write(f"**User City:** {city}")
    # Dictionary to hold one example per amenity
    examples = {}
                
    for c in help_centers[:50]:
        #st.write(f"**{c['type'].title()}**: {c['name']} ({c['distance_km']} km away)")
        amenity_type = c['type']
        if amenity_type not in examples:
            examples[amenity_type] = c

    # Print one of each
    for amenity_type, service in examples.items():
        if(amenity_type != "shelter"):
            st.subheader(f"{amenity_type.title()}:")
            st.write(f"  Name: {service['name']}")
            st.write(f"  Address: {service['address']}")
            st.write(f"  Location: ({service['lat']}, {service['lon']})\n")

    



def crimeAlerts():
    CITY_URLS = {
        "Oakland": "https://data.oaklandca.gov/resource/ppgh-7dqv.csv",
        "Los Angeles": "https://data.lacity.org/resource/2nrs-mtv8.csv",
        "San Francisco": "https://data.sfgov.org/resource/wg3w-h783.csv"
    }

    st.header("🚓 California Crime Dashboard")
    st.write("**Explore live crime data from major California cities.**")

    city = st.selectbox("🏙 Select a California City", list(CITY_URLS.keys()), index=0)
    st.write(f"You selected **{city}**")

    def extract_coordinates(df):
        """Find and clean latitude/longitude fields from different formats."""
        df.columns = [c.lower() for c in df.columns]

        # Case 1: direct coordinate columns
        if {"latitude", "longitude"}.issubset(df.columns):
            df = df.dropna(subset=["latitude", "longitude"])
            return df

        # Case 2: direct coordinate columns
        if {"lat", "lon"}.issubset(df.columns):
            df = df.rename(columns={"lon": "longitude", "lat": "latitude"})
            df = df.dropna(subset=["latitude", "longitude"])
            return df

        # Case 3: 'x' and 'y' columns (Oakland uses this)
        elif {"x", "y"}.issubset(df.columns):
            df = df.rename(columns={"x": "longitude", "y": "latitude"})
            df = df.dropna(subset=["latitude", "longitude"])
            return df

        # Case 4: combined geometry or point string column
        elif "location" in df.columns or "point" in df.columns:
            col = "location" if "location" in df.columns else "point"

            def parse_point(val):
                if isinstance(val, str):
                    match = re.findall(r"-?\d+\.\d+", val)
                    if len(match) == 2:
                        lon, lat = map(float, match)
                        return pd.Series({"longitude": lon, "latitude": lat})
                return pd.Series({"longitude": None, "latitude": None})

            coords = df[col].apply(parse_point)
            df = pd.concat([df, coords], axis=1)
            df = df.dropna(subset=["latitude", "longitude"])
            return df

        else:
            st.error("⚠️ Could not find coordinate columns. Available columns:")
            st.write(df.columns.tolist())
            return pd.DataFrame()


    def fetch_data(city):
        # Socrata API endpoint for Oakland’s CrimeWatch Data (past 90 days)
        #url = f"https://data.oaklandca.gov/resource/ppgh-7dqv.csv?$limit=5000"

        url = CITY_URLS.get(city)
        
        # Load CSV directly over HTTPS
        df = pd.read_csv(url)

        df = extract_coordinates(df)
        
        return df



    # ---------- LOAD DATA ----------
    with st.spinner("Fetching latest crime data for {city}..."):
        df = fetch_data(city)

    if df.empty:
        st.warning("No data could be loaded. Please check your internet connection or dataset URL.")
        st.stop()

    st.success(f"✅ Loaded {len(df):,} crime records for {city}.")


    # ---------- FILTERS ----------
    if "crime_type" in df.columns:
        crime_types = sorted(df["crime_type"].dropna().unique())
        selected_types = st.multiselect("Filter by crime type:", crime_types, default=crime_types[:3])
        df = df[df["crime_type"].isin(selected_types)]

    if "date" in df.columns:
        min_date, max_date = df["date"].min(), df["date"].max()
        date_range = st.slider("Select date range:", min_value=min_date, max_value=max_date, value=(min_date, max_date))
        df = df[(df["date"] >= date_range[0]) & (df["date"] <= date_range[1])]


    # ---------- MAP ----------
    st.subheader(f"🗺️ {city} Crime Map")
    if not df.empty:
        avg_lat = df["latitude"].astype(float).mean()
        avg_lon = df["longitude"].astype(float).mean()
        m = folium.Map(location=[avg_lat, avg_lon], zoom_start=12)

        for _, row in df.head(500).iterrows():  # show up to 500 points for speed
            popup_text = f"{row.get('crime_type', 'Unknown')}<br>{row.get('date', '')}"
            folium.CircleMarker(
                location=[float(row["latitude"]), float(row["longitude"])],
                radius=3,
                color="red",
                fill=True,
                fill_opacity=0.6,
                popup=popup_text
            ).add_to(m)

        st_folium(m, width=800, height=500)
    else:
        st.warning("No crimes found for the selected filters.")

    # Set seaborn style
    sns.set(style="whitegrid", palette="muted")

    st.subheader(f"{city} Crime Alerts — Top 10 Crime Categories")
    #st.write("Raw data sample:")
    #st.dataframe(df.head())
    #st.write("Columns:", list(df.columns))

    # Suppose the column we want is called 'category' (adjust if different)
    
    if(city=="Oakland"):
        category_col = "crimetype"  # change this if the column name differs
    elif(city=="Los Angeles"):
        category_col = "crm_cd_desc"  # change this if the column name differs
    else:
        category_col = "incident_category"  # change this if the column name differs
    

    colors = sns.color_palette("viridis", 10)

    if category_col not in df.columns:
        st.error(f"Column '{category_col}' not found in data. Please inspect and update.")
    else:
        df2 = df.dropna(subset=[category_col])
        top = df2[category_col].value_counts().nlargest(10)
        #st.write("Top 10 crime categories and their counts:")
        #st.write(top)

        fig, ax = plt.subplots(figsize=(10,6))
        sns.barplot(
            x=top.values,
            y=top.index,
            palette=colors,
            ax=ax
        )
        ax.set_xlabel("Number of Incidents")
        ax.set_ylabel("Crime Category")
        ax.set_title(f"Top 10 Crime Categories in {city} (CrimeWatch data)")
        st.pyplot(fig)




# --- Sidebar Navigation Menu ---
with st.sidebar:
    selected = option_menu(
        "Menu",
        ["Real- time Emergency Alerts", "Help Center Information", "California Crime Dashboard", "Emergency Preparedness Checklist"],
        icons=["bell", "info-circle", "exclamation-triangle", "clipboard-check"],
        menu_icon="cast",
        default_index=0
    )

# --- Page routing ---
if selected == "Real- time Emergency Alerts":
    realTimeAlerts()
elif selected == "Help Center Information":
    helpCenters()
elif selected == "California Crime Dashboard":
    crimeAlerts()
elif selected == "Emergency Preparedness Checklist":
    emergencyChecklist()
