import streamlit as st
import folium
from streamlit_folium import st_folium, folium_static
from geopy.geocoders import Nominatim
from datetime import datetime
import service as service
import geopandas as gpd
from shapely.geometry import Point
from pyproj import Proj, transform
import requests

def get_coordinates(destination):
    base_url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": destination,
        "format": "json",
        "limit": 1,
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        if data:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            return lat, lon
        else:
            print("Location not found.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def get_pos(lat,lng):
    return lat,lng

def lon_lat_to_utm(lon, lat):
    utm_proj = Proj(init="epsg:2263")
    utm_x, utm_y = transform(Proj(init="epsg:4326"), utm_proj, lon, lat)
    return utm_x, utm_y

shapefile='./shapes/geo_export_84578745-538d-401a-9cb5-34022c705879.shp'
borough_sh='./borough/nybb.shp'

def get_precinct_and_borough(lat, lon):
    precinct_gdf = gpd.read_file(shapefile)
    borough_gdf = gpd.read_file(borough_sh)
    point = Point(lon, lat)
    point2 = Point(lon_lat_to_utm(lon, lat))
    precinct = None
    borough = None
    for _, row in precinct_gdf.iterrows():
        if row['geometry'].contains(point):
            precinct = row['precinct']
    for _, row in borough_gdf.iterrows():
        if row['geometry'].contains(point2):
            borough = row['BoroName']
            break
    return precinct, borough


def generate_base_map(default_location=[40.704467, -73.892246], default_zoom_start=11, min_zoom=11, max_zoom=15):
    base_map = folium.Map(location=default_location, control_scale=True, zoom_start=default_zoom_start,
                          min_zoom=min_zoom, max_zoom=max_zoom, max_bounds=True, min_lat=40.47739894,
                          min_lon=-74.25909008, max_lat=40.91617849, max_lon=-73.70018092)
    return base_map

def get_user_information():
    with st.container():
        st.header("Enter your information 📋")

        gender = st.radio("Gender 👤", ["Male", "Female"])
        race = st.selectbox("Race 🌍", ['WHITE', 'WHITE HISPANIC', 'BLACK', 'ASIAN / PACIFIC ISLANDER', 'BLACK HISPANIC',
                                     'AMERICAN INDIAN/ALASKAN NATIVE', 'OTHER'])
        age = st.slider("Age 🧑‍🦳:", 0, 120)
        date = st.date_input("Date 🗓️:", datetime.now())
        hour = st.slider("Hour 🕒:", min_value=0, max_value=24)
        place = st.radio("Place 📍", ("In park", "In public housing", "In station"))

    return gender, race, age, date, hour, place


def get_user_input_method():
    return st.radio("input method 📲", ["Select destination on Map 🗺️"])

st.set_page_config(
    page_title="NYC Crime Prediction 🚔",
    page_icon="🌍",
    layout="wide",  
    initial_sidebar_state="collapsed",  # Sidebar is hidden
)
st.markdown(
    """
    <style>
        /* Set background image and make it fixed */
        .stApp {
            background-size: cover;
            position: relative;
            height: 100vh;
        }

        /* Add a transparent overlay on top of the background */
        .stApp::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.4);  /* Dark transparent overlay */
            z-index: -1;
        }

        /* Styling for the main content container with some transparency */
        .stContainer {
            background: rgba(255, 255, 255, 0.9);  /* Slight transparency */
            padding: 20px;
            border-radius: 15px;
            z-index: 10;
        }

        /* Ensuring that the text is white and readable */
        .stContainer h1, .stContainer h2, .stContainer p {
            color: #FFFFFF; /* White text */
        }
       
        /* Adding specific padding for better readability */
        .stContainer .text-box {
            padding: 15px;
            border-radius: 10px;
            background-color: rgba(0, 0, 0, 0.6);  /* Dark transparent background for text */
            color: white;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Main Container for Centering
with st.container():
    st.title("New York Crime Prediction 🚔🌆")

    # Application description centered
    st.markdown("""
        This application uses machine learning models to predict the likelihood of a crime happening at a specific location in **New York City**.
        Whether you're planning to visit NYC or just curious about the safety of a certain area, this tool can help you predict the potential risks based on various inputs, such as:
   
        - **Age, Gender, Race**: Demographic information that influences crime trends.
        - **Time**: The day and hour you plan to be out in the city.
        - **Place**: Whether you are in a park, public housing, or a station.
       
        Simply enter your destination and other relevant details, and the app will predict what kind of crime you may be more likely to be a victim of.
       
        Stay safe and informed! 🌆🚔
    """)

# User Input Method
input_method = get_user_input_method()
gender, race, age, date, hour, place = get_user_information()

# Columns for Better Layout
with st.container():
    col1, col2, col3 = st.columns([1, 2, 1])  # Center the columns
    with col2:
        pred = None
        crimes = None
        if input_method == "Select destination on Map 🗺️":
            base_map = generate_base_map()
            base_map.add_child(folium.LatLngPopup())
            map = st_folium(base_map, height=350, width=700)
            if map['last_clicked'] is not None:
                data = get_pos(map['last_clicked']['lat'], map['last_clicked']['lng'])
                if data is not None:
                    st.write(data)

                lat = data[0]
                long = data[1]
                precinct, borough = get_precinct_and_borough(lat, long)
                if borough:
                    st.success(f"Coordinates are {lat}: {long} 📍")
                    st.success(f'Precinct = {precinct}, Borough = {borough} 🏙️')
                    if st.button("Predict 🔮", key="predict"):
                        if lat == '' or long == '' or precinct is None:
                            st.error("Please make sure that you selected a location on the map 📍")
                        else:
                            X = service.create_df(date, hour, lat, long, place, age, race, gender, precinct, borough)
                            pred, crimes = service.predict(X)  # Predict after inputs are given
                            st.markdown(f"You are likely to be a victim of a: **{pred}** crime ⚠️")
                            st.markdown(f"#### Some of the crimes types are the following: ")
                            st.markdown(crimes)
                else:
                    st.error("Select a destination in NYC 🏙️")
