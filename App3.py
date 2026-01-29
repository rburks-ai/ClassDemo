"""
Netflix Content Browser - Streamlit Application
A comprehensive dashboard for exploring Netflix movies and TV shows
with advanced filtering and visualization capabilities.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import requests
from typing import Dict, List, Optional
import time
from functools import lru_cache
import json

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Netflix Content Browser",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS STYLING
# ============================================================================

def load_css():
    """Apply custom CSS styling to the application"""
    st.markdown("""
    <style>
    /* Main container styling */
    .main {
        background-color: #0f0f0f;
    }
    
    /* Header styling */
    .netflix-header {
        background: linear-gradient(90deg, #E50914 0%, #B20710 100%);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 30px;
        box-shadow: 0 4px 6px rgba(229, 9, 20, 0.3);
    }
    
    .netflix-title {
        color: white;
        font-size: 48px;
        font-weight: bold;
        margin: 0;
        font-family: 'Helvetica Neue', sans-serif;
    }
    
    .netflix-subtitle {
        color: #ffffff;
        font-size: 18px;
        margin-top: 10px;
        opacity: 0.9;
    }
    
    /* Card styling */
    .content-card {
        background: #1a1a1a;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid #333;
        transition: transform 0.3s ease;
    }
    
    .content-card:hover {
        transform: translateY(-5px);
        border-color: #E50914;
    }
    
    /* Metric styling */
    .metric-container {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #E50914;
    }
    
    /* Filter section */
    .filter-section {
        background: #1a1a1a;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    
    /* Button styling */
    .stButton>button {
        background-color: #E50914;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px 24px;
        font-weight: bold;
        transition: background-color 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #B20710;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #1a1a1a;
    }
    
    /* Info box */
    .info-box {
        background: #2d2d2d;
        border-left: 4px solid #4CAF50;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    
    /* Warning box */
    .warning-box {
        background: #2d2d2d;
        border-left: 4px solid #FFC107;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# API CONFIGURATION AND DATA FETCHING
# ============================================================================

class NetflixDataFetcher:
    """Handles data fetching from TMDB API and local datasets"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"
        self.image_base_url = "https://image.tmdb.org/t/p/w500"
        
    @st.cache_data(ttl=3600)
    def fetch_trending_content(_self, media_type: str = "all", time_window: str = "week") -> List[Dict]:
        """Fetch trending movies and TV shows from TMDB"""
        if not _self.api_key:
            return []
        
        try:
            url = f"{_self.base_url}/trending/{media_type}/{time_window}"
            params = {"api_key": _self.api_key, "page": 1}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json().get('results', [])
        except Exception as e:
            st.error(f"Error fetching trending content: {str(e)}")
            return []
    
    @st.cache_data(ttl=3600)
    def search_content(_self, query: str, media_type: str = "multi") -> List[Dict]:
        """Search for content by name"""
        if not _self.api_key:
            return []
        
        try:
            url = f"{_self.base_url}/search/{media_type}"
            params = {"api_key": _self.api_key, "query": query}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json().get('results', [])
        except Exception as e:
            st.error(f"Error searching content: {str(e)}")
            return []
    
    @st.cache_data(ttl=3600)
    def discover_content(_self, media_type: str = "movie", **filters) -> List[Dict]:
        """Discover content with filters"""
        if not _self.api_key:
            return []
        
        try:
            url = f"{_self.base_url}/discover/{media_type}"
            params = {"api_key": _self.api_key, **filters}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json().get('results', [])
        except Exception as e:
            st.error(f"Error discovering content: {str(e)}")
            return []
    
    @st.cache_data(ttl=3600)
    def get_genres(_self, media_type: str = "movie") -> Dict[int, str]:
        """Fetch available genres"""
        if not _self.api_key:
            return {}
        
        try:
            url = f"{_self.base_url}/genre/{media_type}/list"
            params = {"api_key": _self.api_key}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            genres = response.json().get('genres', [])
            return {g['id']: g['name'] for g in genres}
        except Exception as e:
            st.error(f"Error fetching genres: {str(e)}")
            return {}
    
    def get_poster_url(self, poster_path: Optional[str]) -> str:
        """Get full poster URL"""
        if poster_path:
            return f"{self.image_base_url}{poster_path}"
        return "https://via.placeholder.com/500x750?text=No+Poster+Available"

# ============================================================================
# SAMPLE DATA GENERATOR (Fallback)
# ============================================================================

@st.cache_data
def generate_sample_netflix_data() -> pd.DataFrame:
    """Generate sample Netflix data for demonstration"""
    data = {
        'title': [
            'Stranger Things', 'The Crown', 'Breaking Bad', 'Money Heist',
            'The Witcher', 'Ozark', 'Dark', 'Narcos', 'Black Mirror',
            'The Queen\'s Gambit', 'Bridgerton', 'Squid Game', 'Lupin',
            'The Umbrella Academy', 'You', 'Peaky Blinders', 'Vikings',
            'The Last Kingdom', 'Better Call Saul', 'Mindhunter',
            'The Irishman', 'Marriage Story', 'Roma', 'The Trial of Chicago 7',
            'Don\'t Look Up', 'Extraction', 'Bird Box', 'The Old Guard'
        ],
        'type': [
            'TV Show', 'TV Show', 'TV Show', 'TV Show', 'TV Show', 'TV Show',
            'TV Show', 'TV Show', 'TV Show', 'TV Show', 'TV Show', 'TV Show',
            'TV Show', 'TV Show', 'TV Show', 'TV Show', 'TV Show', 'TV Show',
            'TV Show', 'TV Show', 'Movie', 'Movie', 'Movie', 'Movie',
            'Movie', 'Movie', 'Movie', 'Movie'
        ],
        'country': [
            'United States', 'United Kingdom', 'United States', 'Spain',
            'United States', 'United States', 'Germany', 'Colombia',
            'United Kingdom', 'United States', 'United States', 'South Korea',
            'France', 'United States', 'United States', 'United Kingdom',
            'Canada', 'United Kingdom', 'United States', 'United States',
            'United States', 'United States', 'Mexico', 'United States',
            'United States', 'United States', 'United States', 'United States'
        ],
        'release_year': [
            2016, 2016, 2008, 2017, 2019, 2017, 2017, 2015, 2011, 2020,
            2020, 2021, 2021, 2019, 2018, 2013, 2013, 2015, 2015, 2017,
            2019, 2019, 2018, 2020, 2021, 2020, 2018, 2020
        ],
        'rating': [
            8.7, 8.6, 9.5, 8.2, 8.2, 8.5, 8.8, 8.8, 8.7, 8.6,
            7.3, 8.0, 7.5, 7.9, 7.7, 8.8, 8.5, 8.5, 8.8, 8.6,
            7.8, 7.9, 7.7, 7.8, 7.2, 6.7, 6.6, 6.6
        ],
        'genre': [
            'Sci-Fi, Drama', 'Drama, History', 'Crime, Drama', 'Crime, Thriller',
            'Fantasy, Adventure', 'Crime, Drama', 'Sci-Fi, Mystery', 'Crime, Drama',
            'Sci-Fi, Thriller', 'Drama', 'Drama, Romance', 'Thriller, Drama',
            'Mystery, Thriller', 'Sci-Fi, Action', 'Thriller, Drama', 'Crime, Drama',
            'Action, Drama', 'Action, Drama', 'Crime, Drama', 'Crime, Drama',
            'Crime, Drama', 'Drama, Romance', 'Drama', 'Drama, History',
            'Comedy, Drama', 'Action, Thriller', 'Thriller, Horror', 'Action, Fantasy'
        ],
        'duration': [
            '50 min', '58 min', '49 min', '70 min', '60 min', '60 min',
            '60 min', '49 min', '60 min', '60 min', '60 min', '54 min',
            '45 min', '55 min', '45 min', '60 min', '44 min', '60 min',
            '46 min', '54 min', '209 min', '137 min', '135 min', '129 min',
            '138 min', '116 min', '124 min', '125 min'
        ],
        'language': [
            'English', 'English', 'English', 'Spanish', 'English', 'English',
            'German', 'Spanish', 'English', 'English', 'English', 'Korean',
            'French', 'English', 'English', 'English', 'English', 'English',
            'English', 'English', 'English', 'English', 'Spanish', 'English',
            'English', 'English', 'English', 'English'
        ]
    }
    
    return pd.DataFrame(data)

# ============================================================================
# DATA PROCESSING AND FILTERING
# ============================================================================

def filter_dataframe(df: pd.DataFrame, filters: Dict) -> pd.DataFrame:
    """Apply filters to the dataframe"""
    filtered_df = df.copy()
    
    # Filter by type
    if filters.get('type') and filters['type'] != 'All':
        filtered_df = filtered_df[filtered_df['type'] == filters['type']]
    
    # Filter by country
    if filters.get('countries') and filters['countries']:
        filtered_df = filtered_df[filtered_df['country'].isin(filters['countries'])]
    
    # Filter by year range
    if filters.get('year_range'):
        min_year, max_year = filters['year_range']
        filtered_df = filtered_df[
            (filtered_df['release_year'] >= min_year) & 
            (filtered_df['release_year'] <= max_year)
        ]
    
    # Filter by rating range
    if filters.get('rating_range'):
        min_rating, max_rating = filters['rating_range']
        filtered_df = filtered_df[
            (filtered_df['rating'] >= min_rating) & 
            (filtered_df['rating'] <= max_rating)
        ]
    
    # Filter by genre
    if filters.get('genres') and filters['genres']:
        genre_mask = filtered_df['genre'].apply(
            lambda x: any(genre in x for genre in filters['genres'])
        )
        filtered_df = filtered_df[genre_mask]
    
    # Filter by language
    if filters.get('languages') and filters['languages']:
        filtered_df = filtered_df[filtered_df['language'].isin(filters['languages'])]
    
    return filtered_df

# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================

def create_content_distribution_chart(df: pd.DataFrame) -> go.Figure:
    """Create a pie chart showing content type distribution"""
    type_counts = df['type'].value_counts()
    
    fig = go.Figure(data=[go.Pie(
        labels=type_counts.index,
        values=type_counts.values,
        hole=0.4,
        marker_colors=['#E50914', '#B20710'],
        textinfo='label+percent',
        textfont_size=14
    )])
    
    fig.update_layout(
        title="Content Type Distribution",
        title_font_size=20,
        title_font_color='white',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=True,
        height=400
    )
    
    return fig

def create_yearly_releases_chart(df: pd.DataFrame) -> go.Figure:
    """Create a bar chart showing content releases by year"""
    yearly_counts = df.groupby(['release_year', 'type']).size().reset_index(name='count')
    
    fig = px.bar(
        yearly_counts,
        x='release_year',
        y='count',
        color='type',
        title='Content Releases by Year',
        labels={'release_year': 'Year', 'count': 'Number of Releases'},
        color_discrete_map={'Movie': '#E50914', 'TV Show': '#B20710'},
        barmode='group'
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        title_font_size=20,
        xaxis=dict(gridcolor='#333'),
        yaxis=dict(gridcolor='#333'),
        height=400
    )
    
    return fig

def create_country_distribution_chart(df: pd.DataFrame, top_n: int = 10) -> go.Figure:
    """Create a horizontal bar chart showing top countries"""
    country_counts = df['country'].value_counts().head(top_n)
    
    fig = go.Figure(data=[go.Bar(
        x=country_counts.values,
        y=country_counts.index,
        orientation='h',
        marker_color='#E50914',
        text=country_counts.values,
        textposition='auto',
    )])
    
    fig.update_layout(
        title=f"Top {top_n} Countries by Content Production",
        title_font_size=20,
        title_font_color='white',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(title='Number of Titles', gridcolor='#333'),
        yaxis=dict(title=''),
        height=400
    )
    
    return fig

def create_rating_distribution_chart(df: pd.DataFrame) -> go.Figure:
    """Create a histogram showing rating distribution"""
    fig = px.histogram(
        df,
        x='rating',
        nbins=20,
        title='Rating Distribution',
        labels={'rating': 'Rating', 'count': 'Frequency'},
        color_discrete_sequence=['#E50914']
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        title_font_size=20,
        xaxis=dict(gridcolor='#333'),
        yaxis=dict(gridcolor='#333'),
        height=400
    )
    
    return fig

def create_genre_distribution_chart(df: pd.DataFrame, top_n: int = 10) -> go.Figure:
    """Create a bar chart showing top genres"""
    # Explode genres (since they're comma-separated)
    all_genres = []
    for genres in df['genre']:
        all_genres.extend([g.strip() for g in genres.split(',')])
    
    genre_counts = pd.Series(all_genres).value_counts().head(top_n)
    
    fig = go.Figure(data=[go.Bar(
        x=genre_counts.index,
        y=genre_counts.values,
        marker_color='#E50914',
        text=genre_counts.values,
        textposition='auto',
    )])
    
    fig.update_layout(
        title=f"Top {top_n} Genres",
        title_font_size=20,
        title_font_color='white',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(title='', tickangle=-45, gridcolor='#333'),
        yaxis=dict(title='Number of Titles', gridcolor='#333'),
        height=400
    )
    
    return fig

# ============================================================================
# DISPLAY FUNCTIONS
# ============================================================================

def display_header():
    """Display the application header"""
    st.markdown("""
    <div class="netflix-header">
        <h1 class="netflix-title">🎬 NETFLIX Content Browser</h1>
        <p class="netflix-subtitle">Explore thousands of movies and TV shows with advanced filtering</p>
    </div>
    """, unsafe_allow_html=True)

def display_metrics(df: pd.DataFrame):
    """Display key metrics in a row"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric(
            label="📊 Total Content",
            value=len(df),
            delta=None
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric(
            label="🎬 Movies",
            value=len(df[df['type'] == 'Movie']),
            delta=None
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric(
            label="📺 TV Shows",
            value=len(df[df['type'] == 'TV Show']),
            delta=None
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        avg_rating = df['rating'].mean()
        st.metric(
            label="⭐ Avg Rating",
            value=f"{avg_rating:.1f}",
            delta=None
        )
        st.markdown('</div>', unsafe_allow_html=True)

def display_content_grid(df: pd.DataFrame, items_per_row: int = 4):
    """Display content in a grid layout"""
    if df.empty:
        st.warning("No content matches your filters. Try adjusting your selection.")
        return
    
    # Sort by rating
    df_sorted = df.sort_values('rating', ascending=False)
    
    # Display in rows
    for i in range(0, len(df_sorted), items_per_row):
        cols = st.columns(items_per_row)
        row_items = df_sorted.iloc[i:i+items_per_row]
        
        for idx, (col, (_, item)) in enumerate(zip(cols, row_items.iterrows())):
            with col:
                with st.container():
                    st.markdown('<div class="content-card">', unsafe_allow_html=True)
                    
                    # Title
                    st.markdown(f"### {item['title']}")
                    
                    # Type badge
                    badge_color = "#E50914" if item['type'] == "Movie" else "#0080ff"
                    st.markdown(
                        f'<span style="background-color: {badge_color}; color: white; '
                        f'padding: 4px 12px; border-radius: 12px; font-size: 12px; '
                        f'font-weight: bold;">{item["type"]}</span>',
                        unsafe_allow_html=True
                    )
                    
                    st.markdown("---")
                    
                    # Details
                    st.markdown(f"**⭐ Rating:** {item['rating']}/10")
                    st.markdown(f"**📅 Year:** {item['release_year']}")
                    st.markdown(f"**🌍 Country:** {item['country']}")
                    st.markdown(f"**🎭 Genre:** {item['genre']}")
                    st.markdown(f"**⏱️ Duration:** {item['duration']}")
                    st.markdown(f"**🗣️ Language:** {item['language']}")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown("")

def display_detailed_table(df: pd.DataFrame):
    """Display content in a detailed table format"""
    if df.empty:
        st.warning("No content matches your filters.")
        return
    
    # Sort by rating
    df_display = df.sort_values('rating', ascending=False).reset_index(drop=True)
    
    # Display table
    st.dataframe(
        df_display,
        use_container_width=True,
        height=400,
        column_config={
            "title": st.column_config.TextColumn("Title", width="medium"),
            "type": st.column_config.TextColumn("Type", width="small"),
            "rating": st.column_config.NumberColumn("Rating", format="⭐ %.1f"),
            "release_year": st.column_config.NumberColumn("Year", format="%d"),
            "country": st.column_config.TextColumn("Country", width="medium"),
            "genre": st.column_config.TextColumn("Genre", width="large"),
            "duration": st.column_config.TextColumn("Duration", width="small"),
            "language": st.column_config.TextColumn("Language", width="small"),
        }
    )

# ============================================================================
# SIDEBAR FILTERS
# ============================================================================

def create_sidebar_filters(df: pd.DataFrame) -> Dict:
    """Create sidebar with all filter options"""
    st.sidebar.title("🎯 Filters")
    
    filters = {}
    
    # Search bar
    st.sidebar.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.sidebar.subheader("🔍 Search")
    search_query = st.sidebar.text_input("Search by title", "")
    if search_query:
        df = df[df['title'].str.contains(search_query, case=False, na=False)]
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # Content Type Filter
    st.sidebar.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.sidebar.subheader("📺 Content Type")
    content_type = st.sidebar.radio(
        "Select type",
        options=['All', 'Movie', 'TV Show'],
        index=0
    )
    filters['type'] = content_type
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # Year Range Filter
    st.sidebar.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.sidebar.subheader("📅 Release Year")
    min_year = int(df['release_year'].min())
    max_year = int(df['release_year'].max())
    year_range = st.sidebar.slider(
        "Select year range",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year)
    )
    filters['year_range'] = year_range
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # Rating Filter
    st.sidebar.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.sidebar.subheader("⭐ Rating")
    min_rating = float(df['rating'].min())
    max_rating = float(df['rating'].max())
    rating_range = st.sidebar.slider(
        "Select rating range",
        min_value=min_rating,
        max_value=max_rating,
        value=(min_rating, max_rating),
        step=0.1
    )
    filters['rating_range'] = rating_range
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # Country Filter
    st.sidebar.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.sidebar.subheader("🌍 Country")
    countries = sorted(df['country'].unique())
    selected_countries = st.sidebar.multiselect(
        "Select countries",
        options=countries,
        default=[]
    )
    filters['countries'] = selected_countries
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # Genre Filter
    st.sidebar.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.sidebar.subheader("🎭 Genre")
    # Extract unique genres
    all_genres = set()
    for genres in df['genre']:
        all_genres.update([g.strip() for g in genres.split(',')])
    all_genres = sorted(all_genres)
    
    selected_genres = st.sidebar.multiselect(
        "Select genres",
        options=all_genres,
        default=[]
    )
    filters['genres'] = selected_genres
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # Language Filter
    st.sidebar.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.sidebar.subheader("🗣️ Language")
    languages = sorted(df['language'].unique())
    selected_languages = st.sidebar.multiselect(
        "Select languages",
        options=languages,
        default=[]
    )
    filters['languages'] = selected_languages
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # Reset button
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Reset All Filters", use_container_width=True):
        st.rerun()
    
    # Info section
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div class="info-box">
        <h4>ℹ️ About</h4>
        <p>This app provides comprehensive Netflix content exploration with advanced filtering and visualization capabilities.</p>
    </div>
    """, unsafe_allow_html=True)
    
    return filters, df

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application function"""
    
    # Load CSS
    load_css()
    
    # Display header
    display_header()
    
    # API Configuration (optional)
    # Uncomment and add your TMDB API key for live data
    # TMDB_API_KEY = "your_api_key_here"
    # fetcher = NetflixDataFetcher(api_key=TMDB_API_KEY)
    
    # Load data (using sample data for demonstration)
    with st.spinner("Loading Netflix content..."):
        df = generate_sample_netflix_data()
    
    # Check if data is loaded
    if df.empty:
        st.error("Failed to load data. Please check your configuration.")
        return
    
    # Create sidebar filters
    filters, df = create_sidebar_filters(df)
    
    # Apply filters
    filtered_df = filter_dataframe(df, filters)
    
    # Display metrics
    st.markdown("## 📊 Overview")
    display_metrics(filtered_df)
    
    st.markdown("---")
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs([
        "📱 Grid View",
        "📋 Table View",
        "📊 Analytics",
        "📈 Insights"
    ])
    
    with tab1:
        st.markdown("## 🎬 Content Gallery")
        display_content_grid(filtered_df, items_per_row=4)
    
    with tab2:
        st.markdown("## 📋 Detailed View")
        display_detailed_table(filtered_df)
        
        # Download button
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data (CSV)",
            data=csv,
            file_name="netflix_filtered_content.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with tab3:
        st.markdown("## 📊 Visual Analytics")
        
        if not filtered_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.plotly_chart(
                    create_content_distribution_chart(filtered_df),
                    use_container_width=True
                )
                
                st.plotly_chart(
                    create_country_distribution_chart(filtered_df),
                    use_container_width=True
                )
            
            with col2:
                st.plotly_chart(
                    create_rating_distribution_chart(filtered_df),
                    use_container_width=True
                )
                
                st.plotly_chart(
                    create_genre_distribution_chart(filtered_df),
                    use_container_width=True
                )
            
            # Full-width chart
            st.plotly_chart(
                create_yearly_releases_chart(filtered_df),
                use_container_width=True
            )
        else:
            st.warning("No data available for visualization with current filters.")
    
    with tab4:
        st.markdown("## 📈 Key Insights")
        
        if not filtered_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🏆 Top Rated Content")
                top_rated = filtered_df.nlargest(5, 'rating')[['title', 'rating', 'type', 'release_year']]
                for idx, row in top_rated.iterrows():
                    st.markdown(f"""
                    <div class="content-card">
                        <h4>{row['title']}</h4>
                        <p>⭐ <strong>{row['rating']}</strong> | {row['type']} | {row['release_year']}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("### 📅 Recent Releases")
                recent = filtered_df.nlargest(5, 'release_year')[['title', 'release_year', 'type', 'rating']]
                for idx, row in recent.iterrows():
                    st.markdown(f"""
                    <div class="content-card">
                        <h4>{row['title']}</h4>
                        <p>📅 <strong>{row['release_year']}</strong> | {row['type']} | ⭐ {row['rating']}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Statistics
            st.markdown("---")
            st.markdown("### 📊 Statistical Summary")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="metric-container">
                    <h4>🌍 Countries Represented</h4>
                    <h2>{filtered_df['country'].nunique()}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-container">
                    <h4>🎭 Unique Genres</h4>
                    <h2>{len(set([g.strip() for genres in filtered_df['genre'] for g in genres.split(',')]))}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-container">
                    <h4>🗣️ Languages Available</h4>
                    <h2>{filtered_df['language'].nunique()}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            # Year range insights
            st.markdown("---")
            st.markdown("### 📅 Content Timeline")
            
            year_stats = filtered_df.groupby('release_year').size()
            peak_year = year_stats.idxmax()
            peak_count = year_stats.max()
            
            st.markdown(f"""
            <div class="info-box">
                <p><strong>Peak Production Year:</strong> {peak_year} with {peak_count} releases</p>
                <p><strong>Content Span:</strong> {filtered_df['release_year'].min()} - {filtered_df['release_year'].max()}</p>
                <p><strong>Average Release Year:</strong> {filtered_df['release_year'].mean():.0f}</p>
            </div>
            """, unsafe_allow_html=True)
            
        else:
            st.warning("No data available for insights with current filters.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888; padding: 20px;">
        <p>Made with ❤️ using Streamlit | Data updates regularly</p>
        <p style="font-size: 12px;">This is a demonstration app. For production use with real data, add a TMDB API key.</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    main()
