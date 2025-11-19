import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Weather App", page_icon="🌤️", layout="wide")

st.title("🌤️ Weather Forecast App")
st.markdown("Get current weather conditions using the Open-Meteo API")

# Create two columns for input
col1, col2 = st.columns(2)

with col1:
    latitude = st.number_input("Latitude", value=40.7128, format="%.4f", 
                                help="Enter latitude (-90 to 90)")

with col2:
    longitude = st.number_input("Longitude", value=-74.0060, format="%.4f",
                                 help="Enter longitude (-180 to 180)")

# Add some preset cities
st.markdown("**Quick Select Cities:**")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("New York"):
        latitude, longitude = 40.7128, -74.0060
        st.rerun()

with col2:
    if st.button("London"):
        latitude, longitude = 51.5074, -0.1278
        st.rerun()

with col3:
    if st.button("Tokyo"):
        latitude, longitude = 35.6762, 139.6503
        st.rerun()

with col4:
    if st.button("Sydney"):
        latitude, longitude = -33.8688, 151.2093
        st.rerun()

if st.button("Get Weather", type="primary"):
    with st.spinner("Fetching weather data..."):
        try:
            # Open-Meteo API endpoint
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m",
                "temperature_unit": "fahrenheit",
                "wind_speed_unit": "mph",
                "timezone": "auto"
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Extract current weather
            current = data["current"]
            
            # Weather code mapping (WMO Weather interpretation codes)
            weather_codes = {
                0: "☀️ Clear sky",
                1: "🌤️ Mainly clear",
                2: "⛅ Partly cloudy",
                3: "☁️ Overcast",
                45: "🌫️ Foggy",
                48: "🌫️ Depositing rime fog",
                51: "🌦️ Light drizzle",
                53: "🌦️ Moderate drizzle",
                55: "🌦️ Dense drizzle",
                61: "🌧️ Slight rain",
                63: "🌧️ Moderate rain",
                65: "🌧️ Heavy rain",
                71: "🌨️ Slight snow",
                73: "🌨️ Moderate snow",
                75: "🌨️ Heavy snow",
                77: "🌨️ Snow grains",
                80: "🌦️ Slight rain showers",
                81: "🌧️ Moderate rain showers",
                82: "🌧️ Violent rain showers",
                85: "🌨️ Slight snow showers",
                86: "🌨️ Heavy snow showers",
                95: "⛈️ Thunderstorm",
                96: "⛈️ Thunderstorm with slight hail",
                99: "⛈️ Thunderstorm with heavy hail"
            }
            
            weather_description = weather_codes.get(current["weather_code"], "Unknown")
            
            # Display results
            st.success("Weather data retrieved successfully!")
            
            st.markdown(f"### Weather for ({latitude:.4f}, {longitude:.4f})")
            st.markdown(f"**Time:** {current['time']}")
            
            # Create metrics in columns
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Condition", weather_description)
            
            with col2:
                st.metric("Temperature", f"{current['temperature_2m']:.1f}°F")
            
            with col3:
                st.metric("Feels Like", f"{current['apparent_temperature']:.1f}°F")
            
            with col4:
                st.metric("Humidity", f"{current['relative_humidity_2m']}%")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Wind Speed", f"{current['wind_speed_10m']:.1f} mph")
            
            with col2:
                st.metric("Precipitation", f"{current['precipitation']:.1f} mm")
            
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching weather data: {str(e)}")
        except KeyError as e:
            st.error(f"Error parsing weather data: {str(e)}")

st.markdown("---")
st.markdown("**Data provided by:** [Open-Meteo.com](https://open-meteo.com/) - Free Weather API")
st.caption("Enter coordinates or use quick select buttons to get weather information.")
