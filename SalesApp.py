import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Power BI-like styling
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .css-1d391kg {
        padding-top: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Generate sample sales data
@st.cache_data
def generate_sales_data():
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='D')
    
    data = {
        'Date': dates,
        'Sales': np.random.randint(1000, 10000, len(dates)) + np.sin(np.arange(len(dates)) / 30) * 2000,
        'Orders': np.random.randint(50, 300, len(dates)),
        'Customers': np.random.randint(30, 250, len(dates)),
        'Region': np.random.choice(['North', 'South', 'East', 'West'], len(dates)),
        'Product_Category': np.random.choice(['Electronics', 'Clothing', 'Food & Beverage', 'Home & Garden', 'Sports'], len(dates)),
        'Sales_Channel': np.random.choice(['Online', 'In-Store', 'Mobile'], len(dates))
    }
    
    df = pd.DataFrame(data)
    df['Profit'] = df['Sales'] * np.random.uniform(0.15, 0.35, len(df))
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['Quarter'] = df['Date'].dt.quarter
    
    return df

# Load data
df = generate_sales_data()

# Sidebar filters
st.sidebar.header("🔍 Filters")

# Date range filter
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(df['Date'].min(), df['Date'].max()),
    min_value=df['Date'].min().date(),
    max_value=df['Date'].max().date()
)

# Region filter
regions = ['All'] + sorted(df['Region'].unique().tolist())
selected_region = st.sidebar.selectbox("Region", regions)

# Product Category filter
categories = ['All'] + sorted(df['Product_Category'].unique().tolist())
selected_category = st.sidebar.selectbox("Product Category", categories)

# Sales Channel filter
channels = ['All'] + sorted(df['Sales_Channel'].unique().tolist())
selected_channel = st.sidebar.selectbox("Sales Channel", channels)

# Apply filters
mask = (df['Date'].dt.date >= date_range[0]) & (df['Date'].dt.date <= date_range[1])
filtered_df = df.loc[mask]

if selected_region != 'All':
    filtered_df = filtered_df[filtered_df['Region'] == selected_region]
    
if selected_category != 'All':
    filtered_df = filtered_df[filtered_df['Product_Category'] == selected_category]
    
if selected_channel != 'All':
    filtered_df = filtered_df[filtered_df['Sales_Channel'] == selected_channel]

# Main dashboard
st.title("📊 Sales Analytics Dashboard")
st.markdown("---")

# KPI Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_sales = filtered_df['Sales'].sum()
    st.metric(
        label="💰 Total Sales",
        value=f"${total_sales:,.0f}",
        delta=f"{(total_sales / df['Sales'].sum() * 100):.1f}% of total"
    )

with col2:
    total_orders = filtered_df['Orders'].sum()
    st.metric(
        label="🛒 Total Orders",
        value=f"{total_orders:,.0f}",
        delta=f"{(filtered_df['Orders'].mean()):.0f} avg/day"
    )

with col3:
    total_profit = filtered_df['Profit'].sum()
    profit_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0
    st.metric(
        label="📈 Total Profit",
        value=f"${total_profit:,.0f}",
        delta=f"{profit_margin:.1f}% margin"
    )

with col4:
    unique_customers = filtered_df['Customers'].sum()
    st.metric(
        label="👥 Total Customers",
        value=f"{unique_customers:,.0f}",
        delta=f"{(filtered_df['Customers'].mean()):.0f} avg/day"
    )

st.markdown("---")

# Charts Row 1
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Sales Trend Over Time")
    daily_sales = filtered_df.groupby('Date')['Sales'].sum().reset_index()
    fig1 = px.line(
        daily_sales,
        x='Date',
        y='Sales',
        title='Daily Sales Performance',
        labels={'Sales': 'Sales ($)', 'Date': 'Date'}
    )
    fig1.update_traces(line_color='#0066CC', line_width=2)
    fig1.update_layout(hovermode='x unified', height=400)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("🥧 Sales by Product Category")
    category_sales = filtered_df.groupby('Product_Category')['Sales'].sum().reset_index()
    fig2 = px.pie(
        category_sales,
        values='Sales',
        names='Product_Category',
        title='Revenue Distribution by Category',
        hole=0.4
    )
    fig2.update_layout(height=400)
    st.plotly_chart(fig2, use_container_width=True)

# Charts Row 2
col1, col2 = st.columns(2)

with col1:
    st.subheader("🌍 Sales by Region")
    region_sales = filtered_df.groupby('Region').agg({
        'Sales': 'sum',
        'Orders': 'sum',
        'Profit': 'sum'
    }).reset_index()
    
    fig3 = go.Figure(data=[
        go.Bar(name='Sales', x=region_sales['Region'], y=region_sales['Sales'], marker_color='#0066CC'),
        go.Bar(name='Profit', x=region_sales['Region'], y=region_sales['Profit'], marker_color='#00CC66')
    ])
    fig3.update_layout(
        barmode='group',
        title='Sales and Profit by Region',
        xaxis_title='Region',
        yaxis_title='Amount ($)',
        height=400
    )
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.subheader("📱 Sales by Channel")
    channel_sales = filtered_df.groupby('Sales_Channel')['Sales'].sum().reset_index()
    fig4 = px.bar(
        channel_sales,
        x='Sales_Channel',
        y='Sales',
        title='Revenue by Sales Channel',
        color='Sales',
        color_continuous_scale='Blues',
        labels={'Sales': 'Sales ($)', 'Sales_Channel': 'Channel'}
    )
    fig4.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig4, use_container_width=True)

# Charts Row 3
st.subheader("📊 Monthly Performance Analysis")
monthly_data = filtered_df.groupby([filtered_df['Date'].dt.to_period('M')]).agg({
    'Sales': 'sum',
    'Orders': 'sum',
    'Profit': 'sum'
}).reset_index()
monthly_data['Date'] = monthly_data['Date'].dt.to_timestamp()

fig5 = go.Figure()
fig5.add_trace(go.Scatter(x=monthly_data['Date'], y=monthly_data['Sales'], name='Sales', line=dict(color='#0066CC', width=3)))
fig5.add_trace(go.Scatter(x=monthly_data['Date'], y=monthly_data['Profit'], name='Profit', line=dict(color='#00CC66', width=3)))
fig5.update_layout(
    title='Monthly Sales and Profit Trend',
    xaxis_title='Month',
    yaxis_title='Amount ($)',
    hovermode='x unified',
    height=400
)
st.plotly_chart(fig5, use_container_width=True)

# Data Table
st.markdown("---")
st.subheader("📋 Detailed Sales Data")

# Show summary statistics
col1, col2, col3 = st.columns(3)

with col1:
    st.write("**Top Performing Region:**")
    top_region = filtered_df.groupby('Region')['Sales'].sum().idxmax()
    st.success(f"{top_region}")

with col2:
    st.write("**Top Product Category:**")
    top_category = filtered_df.groupby('Product_Category')['Sales'].sum().idxmax()
    st.success(f"{top_category}")

with col3:
    st.write("**Best Sales Channel:**")
    top_channel = filtered_df.groupby('Sales_Channel')['Sales'].sum().idxmax()
    st.success(f"{top_channel}")

# Display data table
if st.checkbox("Show Raw Data"):
    st.dataframe(
        filtered_df.sort_values('Date', ascending=False).head(100),
        use_container_width=True
    )

# Footer
st.markdown("---")
st.markdown("*Dashboard updated in real-time based on selected filters*")
