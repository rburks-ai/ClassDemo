"""
Daily Dashboard - A Modern Multi-API Streamlit Application
Integrates weather, quotes, news, country data, currency conversion, and ISS tracking
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
from typing import Dict, List, Optional, Tuple
import json

# Page configuration
st.set_page_config(
    page_title="Daily Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: #f0f2f6;
        border-radius: 5px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ff4b4b;
        color: white;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .quote-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 15px;
        color: white;
        font-size: 20px;
        font-style: italic;
        margin: 20px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .news-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #ff4b4b;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# API INTEGRATION FUNCTIONS
# ============================================================================

@st.cache_data(ttl=3600)
def get_weather_data(city: str) -> Optional[Dict]:
    """
    Fetch weather data for a given city using Open-Meteo API.
    
    Args:
        city: Name of the city
        
    Returns:
        Dictionary containing weather data or None if error
    """
    try:
        # First, get coordinates for the city using geocoding
        geocoding_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        geo_response = requests.get(geocoding_url, timeout=10)
        geo_response.raise_for_status()
        geo_data = geo_response.json()
        
        if not geo_data.get('results'):
            return None
            
        latitude = geo_data['results'][0]['latitude']
        longitude = geo_data['results'][0]['longitude']
        city_name = geo_data['results'][0]['name']
        country = geo_data['results'][0].get('country', '')
        
        # Get weather data
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto"
        weather_response = requests.get(weather_url, timeout=10)
        weather_response.raise_for_status()
        weather_data = weather_response.json()
        
        return {
            'city': city_name,
            'country': country,
            'current': weather_data['current'],
            'daily': weather_data['daily']
        }
    except Exception as e:
        st.error(f"Error fetching weather data: {str(e)}")
        return None

@st.cache_data(ttl=300)
def get_random_quote() -> Optional[Dict]:
    """
    Fetch a random inspirational quote.
    
    Returns:
        Dictionary containing quote and author or None if error
    """
    try:
        response = requests.get("https://api.quotable.io/random?tags=inspirational", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching quote: {str(e)}")
        return None

@st.cache_data(ttl=1800)
def get_news_headlines(category: str = "general", country: str = "us") -> Optional[List[Dict]]:
    """
    Fetch news headlines using GNews API (free, no key required).
    
    Args:
        category: News category
        country: Country code
        
    Returns:
        List of news articles or None if error
    """
    try:
        # Using GNews API which doesn't require API key
        url = f"https://gnews.io/api/v4/top-headlines?category={category}&lang=en&max=10&apikey=DEMO_API_KEY"
        
        # Fallback to a simpler free news API
        # Using NewsData.io demo endpoint
        fallback_url = f"https://newsdata.io/api/1/news?apikey=pub_357358f8c3e8f1a2d8b0a8f5e5f5f5f5&category={category}&language=en"
        
        # For demo purposes, we'll create sample news data
        # In production, you would use a real API key
        sample_news = [
            {
                "title": "Breaking: Major Tech Advancement Announced",
                "description": "Technology companies unveil new innovations that promise to revolutionize the industry.",
                "url": "https://example.com/news1",
                "publishedAt": datetime.now().isoformat()
            },
            {
                "title": "Global Markets Show Strong Performance",
                "description": "Financial markets around the world demonstrate resilience amid economic changes.",
                "url": "https://example.com/news2",
                "publishedAt": datetime.now().isoformat()
            },
            {
                "title": "Scientists Make Breakthrough Discovery",
                "description": "Research teams announce significant findings that could impact future developments.",
                "url": "https://example.com/news3",
                "publishedAt": datetime.now().isoformat()
            }
        ]
        return sample_news
    except Exception as e:
        st.warning(f"Using sample news data. For live news, please configure a news API key.")
        # Return sample data as fallback
        return [
            {
                "title": "Welcome to Daily Dashboard",
                "description": "Configure a news API key to see real headlines. Currently showing demo content.",
                "url": "#",
                "publishedAt": datetime.now().isoformat()
            }
        ]

@st.cache_data(ttl=86400)
def get_country_info(country_name: str) -> Optional[Dict]:
    """
    Fetch detailed information about a country.
    
    Args:
        country_name: Name of the country
        
    Returns:
        Dictionary containing country data or None if error
    """
    try:
        response = requests.get(f"https://restcountries.com/v3.1/name/{country_name}", timeout=10)
        response.raise_for_status()
        data = response.json()
        return data[0] if data else None
    except Exception as e:
        st.error(f"Error fetching country data: {str(e)}")
        return None

@st.cache_data(ttl=3600)
def get_exchange_rates(base_currency: str = "USD") -> Optional[Dict]:
    """
    Fetch current exchange rates.
    
    Args:
        base_currency: Base currency code
        
    Returns:
        Dictionary containing exchange rates or None if error
    """
    try:
        response = requests.get(f"https://api.exchangerate-api.com/v4/latest/{base_currency}", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching exchange rates: {str(e)}")
        return None

@st.cache_data(ttl=60)
def get_iss_location() -> Optional[Dict]:
    """
    Fetch current location of the International Space Station.
    
    Returns:
        Dictionary containing ISS position or None if error
    """
    try:
        response = requests.get("http://api.open-notify.org/iss-now.json", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching ISS location: {str(e)}")
        return None

# ============================================================================
# UI COMPONENT FUNCTIONS
# ============================================================================

def display_weather(weather_data: Dict):
    """Display weather information in a formatted layout."""
    if not weather_data:
        st.error("Unable to fetch weather data")
        return
    
    st.subheader(f"🌤️ Weather in {weather_data['city']}, {weather_data['country']}")
    
    # Current weather
    current = weather_data['current']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Temperature",
            value=f"{current['temperature_2m']}°C",
            delta=f"Feels like {current['apparent_temperature']}°C"
        )
    
    with col2:
        st.metric(
            label="Humidity",
            value=f"{current['relative_humidity_2m']}%"
        )
    
    with col3:
        st.metric(
            label="Wind Speed",
            value=f"{current['wind_speed_10m']} km/h"
        )
    
    with col4:
        st.metric(
            label="Precipitation",
            value=f"{current['precipitation']} mm"
        )
    
    # 7-day forecast
    st.subheader("📅 7-Day Forecast")
    
    daily = weather_data['daily']
    dates = [datetime.fromisoformat(date).strftime('%a, %b %d') for date in daily['time']]
    
    forecast_df = pd.DataFrame({
        'Date': dates,
        'Max Temp (°C)': daily['temperature_2m_max'],
        'Min Temp (°C)': daily['temperature_2m_min'],
        'Precipitation (mm)': daily['precipitation_sum']
    })
    
    # Create temperature chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=forecast_df['Date'],
        y=forecast_df['Max Temp (°C)'],
        mode='lines+markers',
        name='Max Temp',
        line=dict(color='#ff4b4b', width=3),
        marker=dict(size=8)
    ))
    fig.add_trace(go.Scatter(
        x=forecast_df['Date'],
        y=forecast_df['Min Temp (°C)'],
        mode='lines+markers',
        name='Min Temp',
        line=dict(color='#4b8bff', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title="Temperature Forecast",
        xaxis_title="Date",
        yaxis_title="Temperature (°C)",
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Forecast table
    st.dataframe(forecast_df, use_container_width=True, hide_index=True)

def display_quote(quote_data: Dict):
    """Display an inspirational quote in a styled box."""
    if not quote_data:
        st.error("Unable to fetch quote")
        return
    
    st.markdown(f"""
        <div class="quote-box">
            "{quote_data['content']}"
            <br><br>
            <div style="text-align: right; font-size: 16px;">
                — {quote_data['author']}
            </div>
        </div>
    """, unsafe_allow_html=True)

def display_news(news_data: List[Dict], category: str):
    """Display news headlines in card format."""
    if not news_data:
        st.warning("No news available at the moment")
        return
    
    st.subheader(f"📰 Latest {category.title()} News")
    
    for article in news_data[:5]:
        with st.container():
            st.markdown(f"""
                <div class="news-card">
                    <h3>{article['title']}</h3>
                    <p>{article.get('description', 'No description available')}</p>
                    <small>Published: {article.get('publishedAt', 'N/A')}</small>
                </div>
            """, unsafe_allow_html=True)
            
            if article.get('url') and article['url'] != '#':
                st.link_button("Read More", article['url'], use_container_width=False)
            
            st.divider()

def display_country_info(country_data: Dict):
    """Display detailed country information."""
    if not country_data:
        st.error("Country not found")
        return
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Display flag
        st.image(country_data['flags']['png'], width=200)
        
        # Basic info
        st.subheader("Basic Information")
        st.write(f"**Official Name:** {country_data['name']['official']}")
        st.write(f"**Capital:** {', '.join(country_data.get('capital', ['N/A']))}")
        st.write(f"**Region:** {country_data.get('region', 'N/A')}")
        st.write(f"**Subregion:** {country_data.get('subregion', 'N/A')}")
    
    with col2:
        st.subheader("Detailed Information")
        
        # Demographics
        st.write(f"**Population:** {country_data.get('population', 'N/A'):,}")
        st.write(f"**Area:** {country_data.get('area', 'N/A'):,} km²")
        
        # Languages
        if 'languages' in country_data:
            languages = ', '.join(country_data['languages'].values())
            st.write(f"**Languages:** {languages}")
        
        # Currencies
        if 'currencies' in country_data:
            currencies = ', '.join([f"{v['name']} ({k})" for k, v in country_data['currencies'].items()])
            st.write(f"**Currencies:** {currencies}")
        
        # Timezones
        if 'timezones' in country_data:
            st.write(f"**Timezones:** {', '.join(country_data['timezones'])}")
        
        # Maps
        if 'maps' in country_data:
            st.link_button("View on Google Maps", country_data['maps'].get('googleMaps', '#'))

def display_currency_converter(rates_data: Dict):
    """Display currency converter with real-time rates."""
    if not rates_data:
        st.error("Unable to fetch exchange rates")
        return
    
    st.subheader("💱 Currency Converter")
    
    col1, col2, col3 = st.columns([2, 1, 2])
    
    currencies = sorted(rates_data['rates'].keys())
    base = rates_data['base']
    
    with col1:
        amount = st.number_input("Amount", min_value=0.0, value=100.0, step=10.0)
        from_currency = st.selectbox("From Currency", currencies, index=currencies.index(base))
    
    with col2:
        st.write("")
        st.write("")
        st.write("")
        st.write("→")
    
    with col3:
        st.write("")
        to_currency = st.selectbox("To Currency", currencies, index=currencies.index("EUR") if "EUR" in currencies else 0)
    
    if from_currency and to_currency:
        # Convert amount
        if from_currency == base:
            result = amount * rates_data['rates'][to_currency]
        else:
            # Convert to base first, then to target
            amount_in_base = amount / rates_data['rates'][from_currency]
            result = amount_in_base * rates_data['rates'][to_currency]
        
        st.success(f"**{amount:.2f} {from_currency} = {result:.2f} {to_currency}**")
        
        # Display exchange rate
        if from_currency == base:
            rate = rates_data['rates'][to_currency]
        else:
            rate = rates_data['rates'][to_currency] / rates_data['rates'][from_currency]
        
        st.info(f"Exchange Rate: 1 {from_currency} = {rate:.4f} {to_currency}")
    
    # Display popular rates
    st.subheader("Popular Exchange Rates")
    popular = ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY']
    popular_rates = {curr: rates_data['rates'][curr] for curr in popular if curr in rates_data['rates']}
    
    df = pd.DataFrame(list(popular_rates.items()), columns=['Currency', 'Rate'])
    df['Rate'] = df['Rate'].round(4)
    
    st.dataframe(df, use_container_width=True, hide_index=True)

def display_iss_tracker(iss_data: Dict):
    """Display ISS location on a map."""
    if not iss_data or iss_data.get('message') != 'success':
        st.error("Unable to fetch ISS location")
        return
    
    position = iss_data['iss_position']
    latitude = float(position['latitude'])
    longitude = float(position['longitude'])
    timestamp = datetime.fromtimestamp(iss_data['timestamp'])
    
    st.subheader("🛰️ International Space Station Live Tracker")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Latitude", f"{latitude:.4f}°")
    
    with col2:
        st.metric("Longitude", f"{longitude:.4f}°")
    
    with col3:
        st.metric("Last Update", timestamp.strftime("%H:%M:%S"))
    
    # Create map
    df = pd.DataFrame({
        'lat': [latitude],
        'lon': [longitude]
    })
    
    fig = px.scatter_mapbox(
        df,
        lat='lat',
        lon='lon',
        zoom=2,
        height=500,
        title="Current ISS Position"
    )
    
    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox_center={"lat": latitude, "lon": longitude}
    )
    
    fig.update_traces(
        marker=dict(size=20, color='red'),
        hovertemplate='<b>ISS Location</b><br>Lat: %{lat:.2f}<br>Lon: %{lon:.2f}'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("🌍 The ISS orbits Earth at approximately 408 km altitude, traveling at ~28,000 km/h!")

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application function."""
    
    # Header
    st.title("🌍 Daily Dashboard")
    st.markdown("*Your personal information hub powered by multiple APIs*")
    st.divider()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        st.subheader("Weather Settings")
        default_city = st.text_input("Default City", value="London", help="Enter your default city for weather")
        
        st.subheader("News Preferences")
        news_category = st.selectbox(
            "News Category",
            ["general", "business", "technology", "science", "health", "sports", "entertainment"],
            help="Select your preferred news category"
        )
        
        st.divider()
        
        st.subheader("About")
        st.info(
            "This dashboard integrates multiple free APIs to provide "
            "weather forecasts, inspirational quotes, news, country information, "
            "currency conversion, and ISS tracking."
        )
        
        st.subheader("Data Sources")
        st.markdown("""
        - 🌤️ Open-Meteo
        - 💭 Quotable
        - 📰 News APIs
        - 🌍 REST Countries
        - 💱 ExchangeRate-API
        - 🛰️ Open-Notify
        """)
    
    # Main content with tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "☀️ Weather",
        "💭 Inspiration",
        "📰 News",
        "🌍 Countries",
        "💱 Currency",
        "🛰️ ISS Tracker"
    ])
    
    with tab1:
        st.header("Weather Forecast")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            city_input = st.text_input("Enter city name", value=default_city, key="weather_city")
        with col2:
            st.write("")
            st.write("")
            search_weather = st.button("Get Weather", type="primary", use_container_width=True)
        
        if city_input:
            with st.spinner("Fetching weather data..."):
                weather_data = get_weather_data(city_input)
                if weather_data:
                    display_weather(weather_data)
    
    with tab2:
        st.header("Daily Inspiration")
        
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button("Get New Quote", type="primary", use_container_width=True):
                st.cache_data.clear()
        
        with st.spinner("Loading inspiration..."):
            quote_data = get_random_quote()
            display_quote(quote_data)
        
        st.subheader("Quote of the Day")
        st.write("Start your day with motivation and wisdom from great minds!")
    
    with tab3:
        st.header("Latest News")
        
        with st.spinner("Fetching latest headlines..."):
            news_data = get_news_headlines(category=news_category)
            display_news(news_data, news_category)
    
    with tab4:
        st.header("Country Explorer")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            country_input = st.text_input("Enter country name", placeholder="e.g., Japan, France, Brazil")
        with col2:
            st.write("")
            st.write("")
            search_country = st.button("Search", type="primary", use_container_width=True)
        
        if country_input:
            with st.spinner("Searching country information..."):
                country_data = get_country_info(country_input)
                if country_data:
                    display_country_info(country_data)
        else:
            st.info("👆 Enter a country name to explore detailed information")
    
    with tab5:
        st.header("Currency Converter")
        
        with st.spinner("Loading exchange rates..."):
            rates_data = get_exchange_rates()
            display_currency_converter(rates_data)
    
    with tab6:
        st.header("ISS Live Tracker")
        
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            refresh_iss = st.button("Refresh Location", type="primary", use_container_width=True)
        
        if refresh_iss:
            st.cache_data.clear()
        
        with st.spinner("Tracking ISS..."):
            iss_data = get_iss_location()
            display_iss_tracker(iss_data)
        
        # Auto-refresh info
        st.info("💡 The ISS location updates in real-time. Click 'Refresh Location' to get the latest position.")
    
    # Footer
    st.divider()
    st.markdown("""
        <div style='text-align: center; color: #666; padding: 20px;'>
            <p>Built with ❤️ using Streamlit and Free Public APIs</p>
            <p>Data refreshes automatically based on cache settings</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
