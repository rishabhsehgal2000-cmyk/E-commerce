# -*- coding: utf-8 -*-
"""
Website Performance Analysis & Channel Portfolio Management Dashboard
Built with Python 3.11.9 and Streamlit
FINAL VERSION - Complete & Fixed
"""

import sys
import warnings

if sys.version_info < (3, 9):
    raise RuntimeError("Python 3.9+ is required")

warnings.filterwarnings('ignore')
import datetime as dt 
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

# ============================================================================
# Login System
# ============================================================================


# === USER CREDENTIALS (edit as needed) ===
USERS = {
    "user1": "pass1",
    "Rishabh": "Rishabh321"
}

# === LOGIN LOGIC ===
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if USERS.get(username) == password:
            st.session_state["authenticated"] = True
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Incorrect username or password.")

def logout():
    if st.button("Logout"):
        st.session_state["authenticated"] = False
        st.rerun()

if not st.session_state["authenticated"]:
    login()
    st.stop()  # Prevents rest of the app from running if not logged in

# === Your dashboard/app code goes below! ===
logout()

# ============================================================================
# PAGE CONFIG
# ============================================================================
st.set_page_config(
    page_title="Website Performance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main { padding: 2rem; }
    h1 { color: #1f77b4 !important; font-size: 2.5rem !important; font-weight: 700 !important; }
    h2 { color: #ff7f0e !important; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3rem; background-color: #1f77b4 !important; 
                       color: white !important; border: none !important; font-weight: 600 !important; }
    .stButton>button:hover { background-color: #ff7f0e !important; box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important; }
    [data-testid="stMetricValue"] { font-size: 2rem !important; font-weight: bold !important; }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# LOAD DATA
# ============================================================================
@st.cache_data
def load_data():
    """Load CSV files from the current directory"""
    try:
        sessions = pd.read_csv('website_sessions.csv')
        pageviews = pd.read_csv('website_pageviews.csv')
        orders = pd.read_csv('orders.csv')
        
        sessions['created_at'] = pd.to_datetime(sessions['created_at'])
        pageviews['created_at'] = pd.to_datetime(pageviews['created_at'])
        orders['created_at'] = pd.to_datetime(orders['created_at'])
        
        return sessions, pageviews, orders
    
    except FileNotFoundError as e:
        st.error(f"❌ Error: CSV file not found - {e}")
        st.info("📁 Make sure these files are in the same folder as app.py:")
        st.write("• website_sessions.csv")
        st.write("• website_pageviews.csv")
        st.write("• orders.csv")
        return None, None, None

sessions, pageviews, orders = load_data()

if sessions is None:
    st.stop()

# Set plotly template
plotly_template = "plotly_white"
# ============================================================================
# SIDEBAR FILTERS
# ============================================================================
min_date = sessions['created_at'].min().date()
max_date = sessions['created_at'].max().date()

st.sidebar.title("🔧 Filters")
st.sidebar.markdown("---")

st.sidebar.subheader("📅 Date Range")
date_preset = st.sidebar.radio("Period:", ["📆 Custom", "📊 Last 7 Days", "📊 Last 30 Days", "📊 All Time"])

if date_preset == "📆 Custom":
    start_date = st.sidebar.date_input("From:", min_date)
    end_date = st.sidebar.date_input("To:", max_date)
elif date_preset == "📊 Last 7 Days":
    end_date = max_date
    start_date = (pd.Timestamp(max_date) - pd.Timedelta(days=7)).date()
elif date_preset == "📊 Last 30 Days":
    end_date = max_date
    start_date = (pd.Timestamp(max_date) - pd.Timedelta(days=30)).date()
else:
    start_date = min_date
    end_date = max_date

st.sidebar.subheader("📊 Traffic Source")
all_sources = sorted(sessions['utm_source'].dropna().unique().astype(str).tolist())
selected_sources = st.sidebar.multiselect("Select:", all_sources, default=all_sources)

st.sidebar.subheader("📱 Device Type")
all_devices = sorted(sessions['device_type'].dropna().unique().astype(str).tolist())
selected_devices = st.sidebar.multiselect("Select:", all_devices, default=all_devices)

if st.sidebar.button("🔄 Reset"):
    st.rerun()

st.sidebar.markdown("---")

# ============================================================================
# APPLY FILTERS
# ============================================================================
@st.cache_data(ttl=3600)
def apply_filters(df_sessions, df_pageviews, df_orders, start, end, sources, devices):
    actual_start = min(start, end)
    actual_end = max(start, end)
    
    start_dt = pd.to_datetime(actual_start)
    end_dt = pd.to_datetime(actual_end) + pd.Timedelta(days=1)
    
    df_sessions = df_sessions[(df_sessions['created_at'] >= start_dt) & (df_sessions['created_at'] < end_dt)]
    
    if sources:
        df_sessions = df_sessions[df_sessions['utm_source'].isin(sources)]
    if devices:
        df_sessions = df_sessions[df_sessions['device_type'].isin(devices)]
    
    valid_sessions = df_sessions['website_session_id'].unique()
    df_pageviews = df_pageviews[df_pageviews['website_session_id'].isin(valid_sessions)]
    df_orders = df_orders[df_orders['website_session_id'].isin(valid_sessions)]
    
    return df_sessions, df_pageviews, df_orders

filtered_sessions, filtered_pageviews, filtered_orders = apply_filters(
    sessions.copy(), pageviews.copy(), orders.copy(), 
    start_date, end_date, selected_sources, selected_devices
)
# ============================================================================
# KEY METRICS
# ============================================================================
st.markdown("---")
st.markdown("## 📈 Key Metrics")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("🔵 Sessions", f"{len(filtered_sessions):,}")
with col2:
    st.metric("👁️ Pageviews", f"{len(filtered_pageviews):,}")
with col3:
    st.metric("🛒 Orders", f"{len(filtered_orders):,}")
with col4:
    conv_rate = (len(filtered_orders) / len(filtered_sessions) * 100) if len(filtered_sessions) > 0 else 0
    st.metric("💰 Conv Rate", f"{conv_rate:.2f}%")
with col5:
    revenue = filtered_orders['price_usd'].sum() if len(filtered_orders) > 0 else 0
    st.metric("💵 Revenue", f"${revenue:,.0f}")

st.markdown("---")

# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================

def plot_monthly_sales_revenue(orders):
    """
    Monthly sales and revenue trends
    Shows total items purchased and total revenue by month over time
    """
    orders_copy = orders.copy()
    orders_copy['order_date'] = pd.to_datetime(orders_copy['created_at'])
    orders_copy['order_year'] = orders_copy['order_date'].dt.year
    orders_copy['order_month'] = orders_copy['order_date'].dt.month
    
    monthly = orders_copy.groupby(['order_year', 'order_month']).agg(
        total_items=('items_purchased', 'sum'),
        total_revenue=('price_usd', 'sum')
    ).reset_index()
    
    monthly['month_year'] = monthly['order_year'].astype(str) + '-' + monthly['order_month'].astype(str).str.zfill(2)
    monthly['month_year'] = pd.to_datetime(monthly['month_year'])
    
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Total Items Purchased", "Total Revenue"))
    
    # Add items line chart
    fig.add_trace(go.Scatter(
        x=monthly['month_year'], 
        y=monthly['total_items'], 
        mode='lines+markers', 
        name='Items',
        marker=dict(color='#1f77b4', size=6),
        line=dict(color='#1f77b4', width=2)
    ), row=1, col=1)
    
    # Add revenue line chart
    fig.add_trace(go.Scatter(
        x=monthly['month_year'], 
        y=monthly['total_revenue'], 
        mode='lines+markers', 
        name='Revenue',
        marker=dict(color='#ff7f0e', size=6),
        line=dict(color='#ff7f0e', width=2)
    ), row=1, col=2)
    
    fig.update_xaxes(title_text='Month', row=1, col=1)
    fig.update_yaxes(title_text='Total Items', row=1, col=1)
    fig.update_xaxes(title_text='Month', row=1, col=2)
    fig.update_yaxes(title_text='Revenue (USD)', row=1, col=2)
    
    fig.update_layout(
        height=450, 
        template='plotly_white', 
        hovermode='x unified',
        title_text='Monthly Sales & Revenue Trends',
        showlegend=True
    )
    
    return fig


def plot_daily_sales_revenue(orders):
    """
    Daily sales and revenue trends by day of week
    Shows total items sold and revenue for each day of the week
    """
    orders_copy = orders.copy()
    orders_copy['order_date'] = pd.to_datetime(orders_copy['created_at'])
    orders_copy['order_day_of_week'] = orders_copy['order_date'].dt.dayofweek
    
    daily = orders_copy.groupby('order_day_of_week').agg(
        total_items=('items_purchased', 'sum'),
        total_revenue=('price_usd', 'sum')
    ).reset_index()
    
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily['day_name'] = daily['order_day_of_week'].map(lambda x: day_names[x] if x < 7 else 'Unknown')
    
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Items by Day of Week", "Revenue by Day of Week"))
    
    # Add items bar chart
    fig.add_trace(go.Bar(
        x=daily['day_name'], 
        y=daily['total_items'], 
        name='Items', 
        marker_color='#1f77b4',
        text=daily['total_items'], 
        textposition='outside'
    ), row=1, col=1)
    
    # Add revenue bar chart
    fig.add_trace(go.Bar(
        x=daily['day_name'], 
        y=daily['total_revenue'], 
        name='Revenue', 
        marker_color='#ff7f0e',
        text=daily['total_revenue'], 
        textposition='outside'
    ), row=1, col=2)
    
    fig.update_layout(
        height=450, 
        template='plotly_white', 
        showlegend=True,
        title_text='Daily Sales & Revenue by Day of Week',
        hovermode='x unified'
    )
    
    return fig


def plot_hourly_sessions(sessions):
    """
    Website sessions by hour of day
    Shows total website sessions for each hour of the day
    """
    sessions_copy = sessions.copy()
    sessions_copy['session_date'] = pd.to_datetime(sessions_copy['created_at'])
    sessions_copy['session_hour'] = sessions_copy['session_date'].dt.hour
    
    hourly = sessions_copy.groupby('session_hour').agg(
        total_sessions=('website_session_id', 'count')
    ).reset_index()
    
    fig = px.bar(
        hourly, 
        x='session_hour', 
        y='total_sessions', 
        title='Hourly Website Sessions Distribution',
        template='plotly_white',
        color='total_sessions', 
        color_continuous_scale='Blues',
        labels={
            'session_hour': 'Hour of Day', 
            'total_sessions': 'Total Sessions'
        },
        text='total_sessions'
    )
    
    fig.update_traces(textposition='outside')
    fig.update_layout(
        height=450,
        xaxis_title='Hour of Day (0-23)',
        yaxis_title='Total Sessions',
        hovermode='x unified'
    )
    
    return fig


def plot_product_sales(orders, products):
    """
    Product sales performance analysis
    Shows total items sold and revenue generated by each product
    """
    if products is None or len(products) == 0:
        st.warning("⚠️ Products data not available")
        return None
    
    # Merge orders with products to get product names
    order_product = orders.merge(
        products, 
        left_on='primary_product_id', 
        right_on='product_id', 
        how='left'
    )
    
    # Aggregate by product
    product_sales = order_product.groupby('product_name').agg(
        total_items=('items_purchased', 'sum'),
        total_revenue=('price_usd', 'sum')
    ).reset_index().sort_values('total_revenue', ascending=False)
    
    if len(product_sales) == 0:
        st.warning("⚠️ No product data available")
        return None
    
    fig = make_subplots(
        rows=1, 
        cols=2, 
        subplot_titles=("Total Items Sold by Product", "Total Revenue by Product")
    )
    
    # Add items bar chart
    fig.add_trace(go.Bar(
        x=product_sales['product_name'], 
        y=product_sales['total_items'], 
        name='Items', 
        marker_color='#2ca02c',
        text=product_sales['total_items'], 
        textposition='outside'
    ), row=1, col=1)
    
    # Add revenue bar chart
    fig.add_trace(go.Bar(
        x=product_sales['product_name'], 
        y=product_sales['total_revenue'], 
        name='Revenue', 
        marker_color='#d62728',
        text=product_sales['total_revenue'], 
        textposition='outside'
    ), row=1, col=2)
    
    fig.update_layout(
        height=450, 
        template='plotly_white', 
        showlegend=True,
        title_text='Product Sales Performance',
        hovermode='x unified'
    )
    
    fig.update_xaxes(tickangle=45)
    
    return fig

def plot_daily_session_trends():
    """Daily session trends"""
    if len(filtered_sessions) == 0:
        st.warning("⚠️ No data available")
        return None

    daily = filtered_sessions.groupby(filtered_sessions['created_at'].dt.date).size().reset_index()
    daily.columns = ['Date', 'Sessions']
    daily['Date'] = pd.to_datetime(daily['Date'])
    daily = daily.sort_values('Date')

    fig = px.line(
        daily,
        x='Date',
        y='Sessions',
        title='📈 Daily Session Trends',
        template=plotly_template,
        markers=True,
        line_shape='linear'
    )

    fig.update_traces(line_color='#1f77b4', marker_size=6)
    fig.update_layout(
        hovermode='x unified',
        showlegend=False,
        height=400,
        xaxis_title='Date',
        yaxis_title='Sessions'
    )

    return fig




def plot_one_time_vs_repeat_customer_distribution():
    df=orders.pivot_table(index="user_id",values="order_id",aggfunc="nunique").rename(columns={"order_id":"order_cnt"}).reset_index()
    df["Cust_Type"]=df.order_cnt.apply(lambda x :"One-time-buyer" if x==1 else "Repeat-Buyer")
    df1=orders.pivot_table(index="user_id",values=["price_usd","cogs_usd"],aggfunc="sum").rename(columns={"cogs_usd":"Total_Cost","price_usd":"Total_Spend"}).reset_index()
    df2=pd.merge(left=df,right=df1,how="left",on="user_id")
    df3=df2.pivot_table(index="Cust_Type",values=["user_id","order_cnt","Total_Spend","Total_Cost"],aggfunc={"user_id":"count","order_cnt":"sum","Total_Spend":"sum","Total_Cost":"sum"}).rename(columns={"user_id":"Total_Customers"}).reset_index()
    df3["Profit"]=df3.Total_Spend-df3.Total_Cost
    df3["Order_Distribution"]=df3.order_cnt/df3.order_cnt.sum()*100
    df3["Customer_Distribution"]=df3.Total_Customers/df3.Total_Customers.sum()*100
    df3["Revenue_Contribution"]=df3.Total_Spend/df3.Total_Spend.sum()*100
    df3["AOV"]=df3.Total_Spend/df3.order_cnt
    df3["Profit_per_Cust_type"]=df3.Profit/df3.Total_Customers
    final=df3[["Cust_Type","Order_Distribution","Customer_Distribution","Revenue_Contribution","AOV","Profit_per_Cust_type"]]
    fig = px.pie(final,
    names="Cust_Type",
    values="Customer_Distribution")
    fig.update_traces(textinfo='percent+label', hole=0.4)
    return fig


def plot_one_time_vs_repeat_order_distribution():
    df=orders.pivot_table(index="user_id",values="order_id",aggfunc="nunique").rename(columns={"order_id":"order_cnt"}).reset_index()
    df["Cust_Type"]=df.order_cnt.apply(lambda x :"One-time-buyer" if x==1 else "Repeat-Buyer")
    df1=orders.pivot_table(index="user_id",values=["price_usd","cogs_usd"],aggfunc="sum").rename(columns={"cogs_usd":"Total_Cost","price_usd":"Total_Spend"}).reset_index()
    df2=pd.merge(left=df,right=df1,how="left",on="user_id")
    df3=df2.pivot_table(index="Cust_Type",values=["user_id","order_cnt","Total_Spend","Total_Cost"],aggfunc={"user_id":"count","order_cnt":"sum","Total_Spend":"sum","Total_Cost":"sum"}).rename(columns={"user_id":"Total_Customers"}).reset_index()
    df3["Profit"]=df3.Total_Spend-df3.Total_Cost
    df3["Order_Distribution"]=df3.order_cnt/df3.order_cnt.sum()*100
    df3["Customer_Distribution"]=df3.Total_Customers/df3.Total_Customers.sum()*100
    df3["Revenue_Contribution"]=df3.Total_Spend/df3.Total_Spend.sum()*100
    df3["AOV"]=df3.Total_Spend/df3.order_cnt
    df3["Profit_per_Cust_type"]=df3.Profit/df3.Total_Customers
    final=df3[["Cust_Type","Order_Distribution","Customer_Distribution","Revenue_Contribution","AOV","Profit_per_Cust_type"]]
    fig = px.pie(final,
    names="Cust_Type",
    values="Order_Distribution")
    fig.update_traces(textinfo='percent+label', hole=0.4)
    return fig

def plot_sessions_by_source_device():
    """Sessions by traffic source and device type"""
    sessions_clean = sessions.copy()
    sessions_clean['utm_source'] = sessions_clean['utm_source'].astype(str).str.strip().str.lower()
    sessions_clean['device_type'] = sessions_clean['device_type'].astype(str).str.strip().str.lower()
    
    sessions_by_source_device = (
        sessions_clean
        .groupby(['utm_source', 'device_type'])
        .size()
        .reset_index(name='sessions_count')
        .sort_values('sessions_count', ascending=False)
    )
    
    fig = px.bar(
        sessions_by_source_device,
        x='utm_source',
        y='sessions_count',
        color='device_type',
        barmode='group',
        title='📊 Sessions by Traffic Source & Device Type',
        template=plotly_template,
        text='sessions_count',
        labels={'utm_source': 'Traffic Source', 'sessions_count': 'Sessions', 'device_type': 'Device Type'}
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(height=400)
    return fig

def plot_device_distribution():
    """Device type distribution pie chart"""
    sessions_clean = sessions.copy()
    sessions_clean['device_type'] = sessions_clean['device_type'].astype(str).str.strip().str.lower()
    
    device_counts = sessions_clean['device_type'].value_counts().reset_index()
    device_counts.columns = ['device_type', 'sessions']
    
    fig = px.pie(
        device_counts,
        names='device_type',
        values='sessions',
        hole=0.4,
        title='📱 Device Type Distribution',
        template=plotly_template
    )
    fig.update_traces(textinfo='percent+label+value')
    fig.update_layout(height=400)
    return fig

def plot_repeat_vs_new_users():
    """Repeat vs new users pie chart"""
    sessions_clean = sessions.copy()
    sessions_clean['is_repeat_session'] = sessions_clean['is_repeat_session'].fillna(0).astype(int)
    sessions_clean['user_type'] = sessions_clean['is_repeat_session'].replace({0: 'New', 1: 'Repeat'})
    
    user_counts = sessions_clean['user_type'].value_counts().reset_index()
    user_counts.columns = ['user_type', 'sessions']
    
    fig = px.pie(
        user_counts,
        names='user_type',
        values='sessions',
        hole=0.6,
        title='👥 Repeat vs New Users',
        template=plotly_template
    )
    fig.update_traces(textinfo='percent+label+value')
    fig.update_layout(height=400)
    return fig

def plot_top_pages():
    """Top pages viewed"""
    top_pages = pageviews['pageview_url'].value_counts().head(20).reset_index()
    top_pages.columns = ['pageview_url', 'pageviews']
    
    fig = px.bar(
        top_pages,
        x='pageview_url',
        y='pageviews',
        title='🔝 Top Pages Viewed',
        template=plotly_template,
        color='pageviews',
        text='pageviews',
        labels={'pageview_url': 'Page URL', 'pageviews': 'Pageviews'}
    )
    fig.update_traces(textposition='outside')
    fig.update_xaxes(tickangle=45)
    fig.update_layout(height=400)
    return fig

def plot_landing_pages():
    """Top landing pages"""
    first_views = pageviews.sort_values(['website_session_id', 'created_at']).groupby('website_session_id').first().reset_index()
    first_views = first_views[first_views['pageview_url'].astype(str).str.strip() != '']
    
    landing = first_views['pageview_url'].value_counts().head(20).reset_index()
    landing.columns = ['pageview_url', 'sessions']
    
    fig = px.bar(
        landing,
        x='sessions',
        y='pageview_url',
        orientation='h',
        title='🎯 Top Landing Pages',
        template=plotly_template,
        color='sessions',
        text='sessions',
        labels={'sessions': 'Sessions', 'pageview_url': 'Page URL'}
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(height=400)
    return fig

def plot_exit_pages():
    """Top exit pages"""
    last_views = pageviews.sort_values(['website_session_id', 'created_at']).groupby('website_session_id').last().reset_index()
    
    exit_pages = last_views['pageview_url'].value_counts().head(20).reset_index()
    exit_pages.columns = ['pageview_url', 'sessions']
    
    fig = px.bar(
        exit_pages,
        x='pageview_url',
        y='sessions',
        title='🚪 Top Exit Pages',
        template=plotly_template,
        color='sessions',
        text='sessions',
        labels={'pageview_url': 'Page URL', 'sessions': 'Sessions'}
    )
    fig.update_traces(textposition='outside')
    fig.update_xaxes(tickangle=45)
    fig.update_layout(height=400)
    return fig

def plot_bounce_rate_by_landing_page():
    """Bounce rate by landing page"""
    first_views = (
        pageviews
        .sort_values(['website_session_id', 'created_at'])
        .drop_duplicates(subset=['website_session_id'], keep='first')
        .reset_index(drop=True)
    )
    first_views = first_views[first_views['pageview_url'].astype(str).str.strip() != ""]
    
    session_counts = pageviews.groupby('website_session_id').size()
    bounced_sessions = session_counts[session_counts == 1].index
    
    bounced_landings = first_views[first_views['website_session_id'].isin(bounced_sessions)]['pageview_url']
    
    bounces = bounced_landings.value_counts()
    landings = first_views['pageview_url'].value_counts()
    
    bounce_rate = (bounces / landings * 100).reset_index()
    bounce_rate.columns = ['pageview_url', 'bounce_rate']
    bounce_rate = bounce_rate.head(20)
    
    fig = px.bar(
        bounce_rate,
        x='pageview_url',
        y='bounce_rate',
        title='📉 Bounce Rate by Landing Page',
        template=plotly_template,
        text='bounce_rate',
        labels={'pageview_url': 'Landing Page', 'bounce_rate': 'Bounce Rate (%)'}
    )
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_xaxes(tickangle=45)
    fig.update_layout(height=400)
    return fig

def plot_pageviews_boxplot():
    """Boxplot of pageviews per session"""
    pv_per_session = pageviews.groupby('website_session_id').size()
    
    fig = go.Figure()
    fig.add_trace(go.Box(y=pv_per_session, name='Pageviews'))
    fig.update_layout(
        title='📊 Boxplot of Pageviews Per Session',
        yaxis_title='Pageviews per Session',
        template=plotly_template,
        height=400
    )
    return fig

def plot_conversion_rate_by_source():
    """Conversion rate by traffic source"""
    orders_clean = orders.merge(
        sessions[['website_session_id', 'utm_source']],
        on='website_session_id',
        how='left'
    )
    
    total_sessions = sessions['utm_source'].value_counts()
    orders_by_source = orders_clean['utm_source'].value_counts()
    
    conversion_rate = (orders_by_source / total_sessions * 100).reset_index()
    conversion_rate.columns = ['utm_source', 'conversion_rate']
    
    fig = px.bar(
        conversion_rate,
        x='utm_source',
        y='conversion_rate',
        title='💰 Conversion Rate by Traffic Source',
        template=plotly_template,
        text='conversion_rate',
        labels={'utm_source': 'Traffic Source', 'conversion_rate': 'Conversion Rate (%)'}
    )
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(height=400)
    return fig

def plot_conversion_rate_by_landing_page():
    """Conversion rate by landing page"""
    first_views = (
        pageviews
        .sort_values(['website_session_id', 'created_at'])
        .drop_duplicates(subset=['website_session_id'], keep='first')
        .reset_index(drop=True)
    )
    
    first_views['converted'] = first_views['website_session_id'].isin(orders['website_session_id'])
    
    conversion_stats = first_views.groupby('pageview_url').agg(
        landings=('website_session_id', 'count'),
        conversions=('converted', 'sum')
    )
    
    conversion_stats['conversion_rate'] = (conversion_stats['conversions'] / conversion_stats['landings']) * 100
    conversion_stats = conversion_stats.reset_index().sort_values('conversion_rate', ascending=False).head(20)
    
    fig = px.bar(
        conversion_stats,
        x='pageview_url',
        y='conversion_rate',
        title='🎯 Conversion Rate by Landing Page',
        template=plotly_template,
        text='conversion_rate',
        labels={'pageview_url': 'Landing Page', 'conversion_rate': 'Conversion Rate (%)'}
    )
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_xaxes(tickangle=45)
    fig.update_layout(height=400)
    return fig

def plot_sessions_by_channel():
    """Sessions by marketing channel"""
    chan_sessions = sessions['utm_source'].value_counts().reset_index()
    chan_sessions.columns = ['channel', 'sessions']
    
    fig = px.bar(
        chan_sessions,
        x='channel',
        y='sessions',
        title='📊 Sessions by Marketing Channel',
        template=plotly_template,
        text='sessions',
        labels={'channel': 'Channel', 'sessions': 'Sessions'}
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(height=400)
    return fig

def plot_orders_by_channel():
    """Orders by marketing channel"""
    orders_clean = orders.merge(sessions[['website_session_id', 'utm_source']], on='website_session_id', how='left')
    
    chan_orders = orders_clean['utm_source'].value_counts().reset_index()
    chan_orders.columns = ['channel', 'orders']
    
    fig = px.bar(
        chan_orders,
        x='channel',
        y='orders',
        title='🛒 Orders by Marketing Channel',
        template=plotly_template,
        text='orders',
        labels={'channel': 'Channel', 'orders': 'Orders'}
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(height=400)
    return fig

def plot_conversion_rate_by_channel():
    """Conversion rate by channel"""
    orders_clean = orders.merge(sessions[['website_session_id', 'utm_source']], on='website_session_id', how='left')
    
    sess_count = sessions['utm_source'].value_counts()
    ord_count = orders_clean['utm_source'].value_counts()
    
    conv_rate = (ord_count / sess_count * 100).reset_index()
    conv_rate.columns = ['channel', 'conversion_rate']
    
    fig = px.bar(
        conv_rate,
        x='channel',
        y='conversion_rate',
        title='💰 Conversion Rate by Channel',
        template=plotly_template,
        text='conversion_rate',
        labels={'channel': 'Channel', 'conversion_rate': 'Conversion Rate (%)'}
    )
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(height=400)
    return fig

def plot_aov_by_channel():
    """Average order value by channel"""
    orders_clean = orders.merge(sessions[['website_session_id', 'utm_source']], on='website_session_id', how='left')
    
    aov = orders_clean.groupby('utm_source')['price_usd'].mean().reset_index()
    aov.columns = ['channel', 'average_order_value']
    
    fig = px.bar(
        aov,
        x='channel',
        y='average_order_value',
        title='💵 Average Order Value by Channel',
        template=plotly_template,
        text='average_order_value',
        labels={'channel': 'Channel', 'average_order_value': 'AOV (USD)'}
    )
    fig.update_traces(texttemplate='$%{text:.2f}', textposition='outside')
    fig.update_layout(height=400)
    return fig

def plot_sessions_by_channel_device():
    """Sessions by channel and device"""
    sessions_clean = sessions.copy()
    sessions_clean['device_type'] = sessions_clean['device_type'].astype(str).str.strip().str.lower()
    
    group = sessions_clean.groupby(['utm_source', 'device_type']).size().reset_index(name='sessions')
    
    fig = px.bar(
        group,
        x='utm_source',
        y='sessions',
        color='device_type',
        barmode='group',
        title='📱 Sessions by Channel & Device',
        template=plotly_template,
        text='sessions',
        labels={'utm_source': 'Channel', 'sessions': 'Sessions', 'device_type': 'Device Type'}
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(height=400)
    return fig

def plot_channel_share_trend():
    """Channel share trend over time"""
    sessions_clean = sessions.copy()
    
    agg = sessions_clean.groupby([sessions_clean['created_at'].dt.to_period('M'), 'utm_source']).size().reset_index(name='sessions')
    agg['created_at'] = agg['created_at'].astype(str)
    
    fig = px.area(
        agg,
        x='created_at',
        y='sessions',
        color='utm_source',
        title='📈 Channel Share Trend Over Time',
        template=plotly_template,
        groupnorm='percent',
        labels={'created_at': 'Month', 'sessions': 'Sessions', 'utm_source': 'Channel'}
    )
    fig.update_layout(height=400)
    return fig

def plot_new_vs_returning_by_channel():
    """New vs returning users by channel"""
    sessions_clean = sessions.copy()
    sessions_clean['is_repeat_session'] = sessions_clean['is_repeat_session'].fillna(0).astype(int)
    sessions_clean['user_type'] = sessions_clean['is_repeat_session'].replace({0: 'New', 1: 'Repeat'})
    
    group = sessions_clean.groupby(['utm_source', 'user_type']).size().reset_index(name='sessions')
    
    fig = px.bar(
        group,
        x='utm_source',
        y='sessions',
        color='user_type',
        barmode='stack',
        title='👥 New vs Returning Users by Channel',
        template=plotly_template,
        text='sessions',
        labels={'utm_source': 'Channel', 'sessions': 'Sessions', 'user_type': 'User Type'}
    )
    fig.update_traces(textposition='auto')
    fig.update_layout(height=400)
    return fig

def plot_channel_funnel():
    """Channel funnel visualization (Sankey)"""
    channels = sessions['utm_source'].unique()
    
    nodes = []
    sources = []
    targets = []
    values = []
    
    for ci, channel in enumerate(channels):
        ch_sessions = sessions[sessions['utm_source'] == channel]['website_session_id']
        ch_product = pageviews[pageviews['website_session_id'].isin(ch_sessions) & pageviews['pageview_url'].str.contains('/product', na=False)]['website_session_id'].nunique()
        ch_cart = pageviews[pageviews['website_session_id'].isin(ch_sessions) & pageviews['pageview_url'].str.contains('/cart', na=False)]['website_session_id'].nunique()
        ch_orders = orders[orders['website_session_id'].isin(ch_sessions)]['website_session_id'].nunique()
        
        nodes += [f"{channel} Session", f"{channel} Product", f"{channel} Cart", f"{channel} Order"]
        
        idx = len(nodes) - 4
        
        sources += [idx, idx+1, idx+2]
        targets += [idx+1, idx+2, idx+3]
        values += [ch_product, ch_cart, ch_orders]
    
    fig = go.Figure(
        data=[go.Sankey(
            node=dict(label=nodes, pad=15, thickness=20),
            link=dict(source=sources, target=targets, value=values)
        )]
    )
    
    fig.update_layout(title_text='🔗 Channel Funnel Visualization', font_size=12, template=plotly_template, height=400)
    return fig

def plot_top_campaigns():
    """Top campaigns within channels"""
    orders_clean = orders.merge(
        sessions[['website_session_id', 'utm_source', 'utm_campaign']],
        on='website_session_id',
        how='left'
    )
    
    group = orders_clean.groupby(['utm_source', 'utm_campaign']).size().reset_index(name='orders')
    group = group.sort_values('orders', ascending=False).head(20)
    
    fig = px.bar(
        group,
        x='utm_source',
        y='orders',
        color='utm_campaign',
        barmode='stack',
        title='🎯 Top Campaigns within Channels',
        template=plotly_template,
        text='orders',
        labels={'utm_source': 'Channel', 'orders': 'Orders', 'utm_campaign': 'Campaign'}
    )
    fig.update_traces(textposition='inside')
    fig.update_layout(height=400)
    return fig

def plot_sessions_percentage_by_source():
    """Percentage of sessions per utm_source"""
    website_sessions = pd.read_csv('website_sessions.csv')
    website_sessions['utm_source'] = website_sessions['utm_source'].astype(str).str.strip().str.lower()
    # Count sessions per source
    counts = website_sessions['utm_source'].value_counts()
    total = counts.sum()
    
    # Convert to dataframe for Plotly
    df = (counts / total * 100).reset_index()
    df.columns = ['utm_source', 'percentage']
    
    # Plot
    fig = px.bar(
        df,
        x='utm_source',
        y='percentage',
        text='percentage',
        title='🌍 Percentage of Sessions per Traffic Source',
        labels={'utm_source': 'Traffic Source', 'percentage': 'Percentage of Sessions (%)'},
        template='plotly_white'
    )
    
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(xaxis_tickangle=45)

    return fig


def plot_one_time_vs_repeat_revenue_distribution():
    df=orders.pivot_table(index="user_id",values="order_id",aggfunc="nunique").rename(columns={"order_id":"order_cnt"}).reset_index()
    df["Cust_Type"]=df.order_cnt.apply(lambda x :"One-time-buyer" if x==1 else "Repeat-Buyer")
    df1=orders.pivot_table(index="user_id",values=["price_usd","cogs_usd"],aggfunc="sum").rename(columns={"cogs_usd":"Total_Cost","price_usd":"Total_Spend"}).reset_index()
    df2=pd.merge(left=df,right=df1,how="left",on="user_id")
    df3=df2.pivot_table(index="Cust_Type",values=["user_id","order_cnt","Total_Spend","Total_Cost"],aggfunc={"user_id":"count","order_cnt":"sum","Total_Spend":"sum","Total_Cost":"sum"}).rename(columns={"user_id":"Total_Customers"}).reset_index()
    df3["Profit"]=df3.Total_Spend-df3.Total_Cost
    df3["Order_Distribution"]=df3.order_cnt/df3.order_cnt.sum()*100
    df3["Customer_Distribution"]=df3.Total_Customers/df3.Total_Customers.sum()*100
    df3["Revenue_Contribution"]=df3.Total_Spend/df3.Total_Spend.sum()*100
    df3["AOV"]=df3.Total_Spend/df3.order_cnt
    df3["Profit_per_Cust_type"]=df3.Profit/df3.Total_Customers
    final=df3[["Cust_Type","Order_Distribution","Customer_Distribution","Revenue_Contribution","AOV","Profit_per_Cust_type"]]
    fig=px.bar(final,x="Cust_Type",y="Revenue_Contribution",text_auto='.2f')
    fig.update_traces(textposition='outside')  # move labels above bars
    fig.update_layout(yaxis_title="Revenue Contribution",
    xaxis_title="Customer Type")
    return fig


def plot_rfm_cust_distribution():
    df1=orders.pivot_table(index="user_id",values="order_id",aggfunc="nunique").rename(columns={"order_id":"Frequency"}).reset_index()
    df2=orders.pivot_table(index="user_id",values="created_at",aggfunc="max").rename(columns={"created_at":"Max_Date"}).reset_index()
    df2["Recency"]=(pd.to_datetime("2015-04-01")-pd.to_datetime(df2.Max_Date.dt.date,format="%Y-%m-%d")).dt.days
    df3=orders.pivot_table(index="user_id",values="price_usd",aggfunc="sum").rename(columns={"price_usd":"Monetary"}).reset_index()
    data=pd.merge(df1,df2,how="left",on="user_id")
    data=data.drop(columns="Max_Date")
    final=pd.merge(data,df3,how="left",on="user_id")
    recency_bins=[12,172,432,1108]
    bins_labels=[3,2,1]
    final["R_Score"]=pd.cut(final.Recency,bins=recency_bins,labels=bins_labels).astype("int32")
    spend_bins=[29.768,55,120,251.94]
    spend_labels=[1,2,3]
    final["M_score"]=pd.cut(final.Monetary,bins=spend_bins,labels=spend_labels).astype("int32")
    final["RFM_Score"]=final.M_score+final.R_Score+final.Frequency
    rfm_bins=[2,4,6,9]
    rfm_labels=["Silver","Gold","Platinum"]
    final["Cust_Segment"]=pd.cut(final.RFM_Score,bins=rfm_bins,labels=rfm_labels)
    df=final.pivot_table(index="Cust_Segment",values="user_id",aggfunc="nunique").rename(columns={"user_id":"Total_Cust"}).reset_index()
    df["Cust_Distribution"]=df.Total_Cust/df.Total_Cust.sum()*100
    fig = px.pie(df,
    names="Cust_Segment",
    values="Total_Cust")
    fig.update_traces(textinfo='percent+label', hole=0.4)
    return fig


def plot_rfm_revenue_contribution() :
    df1=orders.pivot_table(index="user_id",values="order_id",aggfunc="nunique").rename(columns={"order_id":"Frequency"}).reset_index()
    df2=orders.pivot_table(index="user_id",values="created_at",aggfunc="max").rename(columns={"created_at":"Max_Date"}).reset_index()
    df2["Recency"]=(pd.to_datetime("2015-04-01")-pd.to_datetime(df2.Max_Date.dt.date,format="%Y-%m-%d")).dt.days
    df3=orders.pivot_table(index="user_id",values="price_usd",aggfunc="sum").rename(columns={"price_usd":"Monetary"}).reset_index()
    data=pd.merge(df1,df2,how="left",on="user_id")
    data=data.drop(columns="Max_Date")
    final=pd.merge(data,df3,how="left",on="user_id")
    recency_bins=[12,172,432,1108]
    bins_labels=[3,2,1]
    final["R_Score"]=pd.cut(final.Recency,bins=recency_bins,labels=bins_labels).astype("int32")
    spend_bins=[29.768,55,120,251.94]
    spend_labels=[1,2,3]
    final["M_score"]=pd.cut(final.Monetary,bins=spend_bins,labels=spend_labels).astype("int32")
    final["RFM_Score"]=final.M_score+final.R_Score+final.Frequency
    rfm_bins=[2,4,6,9]
    rfm_labels=["Silver","Gold","Platinum"]
    final["Cust_Segment"]=pd.cut(final.RFM_Score,bins=rfm_bins,labels=rfm_labels)
    df1=final.pivot_table(index="Cust_Segment",values="Monetary",aggfunc="sum").rename(columns={"Monetary":"Spend"}).reset_index()
    df1["Spend_Contribution"]=df1.Spend/df1.Spend.sum()*100
    fig=px.bar(df1,x="Cust_Segment",y="Spend_Contribution",text_auto='.2f')
    fig.update_traces(textposition='outside') 
    fig.update_layout(yaxis_title="Revenue Contribution",xaxis_title="Customer Type")
    return fig



def plot_cohort_retention_heatmap():
    """
    Enhanced Cohort Retention Heatmap - IMPROVED READABILITY
    """
    import datetime as dt
    import pandas as pd
    import plotly.graph_objects as go
    
    # Prepare data
    df = orders[['user_id', 'created_at']].copy()
    df['OrderMonth'] = df['created_at'].apply(lambda x: dt.datetime(x.year, x.month, 1))
    df['CohortMonth'] = df.groupby('user_id')['OrderMonth'].transform('min')
    
    def get_date_element(dataframe, column):
        day = dataframe[column].dt.day
        month = dataframe[column].dt.month
        year = dataframe[column].dt.year
        return day, month, year
    
    _, Ordermonth, Orderyear = get_date_element(df, 'OrderMonth')
    _, Cohortmonth, Cohortyear = get_date_element(df, 'CohortMonth')
    
    year_diff = Orderyear - Cohortyear
    month_diff = Ordermonth - Cohortmonth
    df['CohortIndex'] = year_diff * 12 + month_diff + 1
    
    # Create cohort data
    cohort_data = df.pivot_table(
        index='CohortMonth',
        columns='CohortIndex',
        values='user_id',
        aggfunc='nunique'
    )
    
    # Format index
    cohort_data.index = cohort_data.index.strftime('%b %Y')
    
    # Calculate retention rates
    new_cohort_data = cohort_data.divide(cohort_data.iloc[:, 0], axis=0)
    
    # Convert to percentage
    retention_pct = (new_cohort_data * 100).round(1)
    
    # Create custom text with percentages
    text_data = retention_pct.applymap(lambda x: f'{x:.1f}%' if pd.notna(x) else '')
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=retention_pct.values,
        x=[f'Month {i}' for i in retention_pct.columns],
        y=retention_pct.index,
        text=text_data.values,
        texttemplate='%{text}',
        textfont={"size": 10, "color": "black"},
        colorscale=[
            [0, '#f7fbff'],
            [0.2, '#deebf7'],
            [0.4, '#c6dbef'],
            [0.6, '#9ecae1'],
            [0.8, '#4292c6'],
            [1, '#08519c']
        ],
        colorbar=dict(
            title=dict(
                text="Retention %",
                side="right"
            ),
            tickmode="linear",
            tick0=0,
            dtick=20,
            ticksuffix="%",
            len=0.7,
            thickness=20
        ),
        hovertemplate='<b>Cohort:</b> %{y}<br><b>Period:</b> %{x}<br><b>Retention:</b> %{z:.1f}%<br><extra></extra>',
        zmin=0,
        zmax=100
    ))
    
    # Update layout with BETTER READABLE AXIS
    fig.update_layout(
        title={
            'text': '📊 Cohort Retention Analysis',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 22, 'color': '#1f77b4', 'family': 'Arial'}
        },
        xaxis=dict(
            title=dict(text='Months Since First Purchase', font=dict(size=13, color='#2c3e50')),
            tickfont=dict(size=12, color='#34495e'),
            side='bottom',
            tickangle=-45,
            showgrid=True,
            gridwidth=1,
            gridcolor='#ecf0f1'
        ),
        yaxis=dict(
            title=dict(text='Cohort Month', font=dict(size=13, color='#2c3e50')),
            tickfont=dict(size=12, color='#34495e'),
            autorange='reversed',
            showgrid=True,
            gridwidth=1,
            gridcolor='#ecf0f1'
        ),
        height=700,
        width=1400,
        plot_bgcolor='white',
        paper_bgcolor='#f8f9fa',
        margin=dict(l=150, r=100, t=100, b=120),
        font=dict(family='Arial, sans-serif')
    )
    
    return fig



def plot_revenue_from_new_and_existing():
    df=orders.sort_values(by=['user_id','created_at'],ascending=True).reset_index(drop=True)
    df["is_new"]=~df.duplicated(subset="user_id")
    df=df[["user_id",'created_at',"price_usd","is_new"]]
    df["cust_type"]=df.is_new.apply(lambda x :"New" if x==True else "Existing")
    df['Month']=df.created_at.dt.month_name()
    df=df.pivot_table(index="Month",columns="cust_type",values="price_usd",aggfunc="sum").reset_index()
    df.columns.name=None
    df["Total_Sale"]=df.Existing+df.New
    df["Contribution_from_Existing"]=df.Existing/df.Total_Sale*100
    df["Contribution_from_New"]=df.New/df.Total_Sale*100
    df_melted = df.melt(
    id_vars='Month',
    value_vars=['Contribution_from_Existing', 'Contribution_from_New'],
    var_name='Customer_Type',
    value_name='Contribution')
    fig = px.bar(
    df_melted,
    x='Month',
    y='Contribution',
    color='Customer_Type',
    barmode='group',
    text_auto='.2f')
    fig.update_layout(xaxis_title='Month',yaxis_title='Contribution')
    return fig

def plot_cust_journey_analysis():
    website_pageviews = pd.read_csv("website_pageviews.csv")
    df=website_pageviews.copy()
    funnel_mapping={
    '/home': 1,
    '/products': 2,
    '/cart': 3,
    '/shipping': 4,
    '/billing': 5,
    '/thank-you-for-your-order': 6
}
    df["funnel_step"]=df.pageview_url.map(funnel_mapping)
    df=df.dropna(axis=0,how="any").reset_index(drop=True)
    df=df.sort_values(["website_session_id","created_at"])
    df_unique=df.drop_duplicates(subset=["website_session_id","funnel_step"])
    df_steps=df_unique.sort_values(['website_session_id','created_at']).groupby('website_session_id')['funnel_step'].apply(list).reset_index()
    funnel_steps = [1,2,3,4,5,6]
    step_counts = {step: 0 for step in funnel_steps}
    for steps in df_steps['funnel_step']:
    # Track which steps this session reached in order
           for step in funnel_steps:
               if step in steps:
                   step_counts[step] += 1
               else:
            # Stop counting further steps for this session once a step is missing
                   break
    funnel_counts = pd.DataFrame({'funnel_step': step_counts.keys(),'sessions_reached': step_counts.values()})
    funnel_mapping = {
    1: '/home',
    2: '/products',
    3: '/cart',
    4: '/shipping',
    5: '/billing',
    6: '/thank-you-for-your-order'
}
    funnel_counts["step_name"]=funnel_counts.funnel_step.apply(lambda x:funnel_mapping[x])
    funnel_counts["conversion_from_previous"]=funnel_counts.sessions_reached/funnel_counts.sessions_reached.shift(1)*100
    funnel_counts["conversion_from_previous"]=funnel_counts.conversion_from_previous.fillna(100.00).round(2)
    fig = px.funnel(
    funnel_counts,
    x='conversion_from_previous',
    y='step_name',
    title='Website Funnel Analysis')
    fig.update_layout(title_x=0.5,
    title_font_size=22,
    font=dict(size=15),           
    yaxis=dict(
    tickfont=dict(size=15)))
    return fig


def plot_single_vs_multiple_prod_cust_distribution():
    df=orders.copy()
    df["Profit"]=df.price_usd-df.cogs_usd
    user_behav=pd.DataFrame(df.groupby("user_id")["items_purchased"].apply(list)).reset_index()
    user_behav["cust_type"]=user_behav.items_purchased.apply(lambda x: "Multiple-Product-Buyer" if any(i > 1 for i in x) else "Single-Product-Buyer")
    df1=df.pivot_table(index="user_id",values=["price_usd","Profit","order_id"],aggfunc={"order_id":"nunique","price_usd":"sum","Profit":"sum"})
    final=pd.merge(left=user_behav,right=df1,how="left",on="user_id")
    final=final.pivot_table(index="cust_type",values=["price_usd","Profit","order_id","user_id"],\
                  aggfunc={"user_id":"nunique","price_usd":"sum","Profit":"sum","order_id":"sum"})\
.rename(columns={"Profit":"Total_Profit_Earned","order_id" :"Total_Orders","price_usd":"Total_Spend","user_id":"Total_Customers"})\
.reset_index()
    final["Customer_distribution"]=final.Total_Customers/final.Total_Customers.sum()*100
    final["Order_distribution"]=final.Total_Orders/final.Total_Orders.sum()*100
    final["Spend_Contribution"]=final.Total_Spend/final.Total_Spend.sum()*100
    final["AOV"]=final.Total_Spend/final.Total_Orders
    final["Avg_Profit_Earned"]=final.Total_Profit_Earned/final.Total_Customers
    fig = px.pie(final,
    names="cust_type",
    values="Customer_distribution")
    fig.update_traces(textinfo='percent+label', hole=0.4)
    fig.update_layout(
        showlegend=True,
        legend=dict(
            font=dict(size=13),
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )
    return fig

def plot_single_vs_multiple_prod_order_distribution():
    df=orders.copy()
    df["Profit"]=df.price_usd-df.cogs_usd
    user_behav=pd.DataFrame(df.groupby("user_id")["items_purchased"].apply(list)).reset_index()
    user_behav["cust_type"]=user_behav.items_purchased.apply(lambda x: "Multiple-Product-Buyer" if any(i > 1 for i in x) else "Single-Product-Buyer")
    df1=df.pivot_table(index="user_id",values=["price_usd","Profit","order_id"],aggfunc={"order_id":"nunique","price_usd":"sum","Profit":"sum"})
    final=pd.merge(left=user_behav,right=df1,how="left",on="user_id")
    final=final.pivot_table(index="cust_type",values=["price_usd","Profit","order_id","user_id"],\
                  aggfunc={"user_id":"nunique","price_usd":"sum","Profit":"sum","order_id":"sum"})\
.rename(columns={"Profit":"Total_Profit_Earned","order_id" :"Total_Orders","price_usd":"Total_Spend","user_id":"Total_Customers"})\
.reset_index()
    final["Customer_distribution"]=final.Total_Customers/final.Total_Customers.sum()*100
    final["Order_distribution"]=final.Total_Orders/final.Total_Orders.sum()*100
    final["Spend_Contribution"]=final.Total_Spend/final.Total_Spend.sum()*100
    final["AOV"]=final.Total_Spend/final.Total_Orders
    final["Avg_Profit_Earned"]=final.Total_Profit_Earned/final.Total_Customers
    fig = px.pie(final,
    names="cust_type",
    values="Order_distribution")
    fig.update_traces(textinfo='percent+label', hole=0.4)
    fig.update_layout(
        showlegend=True,
        legend=dict(
            font=dict(size=13),
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )
    return fig

def plot_single_vs_multiple_prod_revenue_contribution():
    df=orders.copy()
    df["Profit"]=df.price_usd-df.cogs_usd
    user_behav=pd.DataFrame(df.groupby("user_id")["items_purchased"].apply(list)).reset_index()
    user_behav["cust_type"]=user_behav.items_purchased.apply(lambda x: "Multiple-Product-Buyer" if any(i > 1 for i in x) else "Single-Product-Buyer")
    df1=df.pivot_table(index="user_id",values=["price_usd","Profit","order_id"],aggfunc={"order_id":"nunique","price_usd":"sum","Profit":"sum"})
    final=pd.merge(left=user_behav,right=df1,how="left",on="user_id")
    final=final.pivot_table(index="cust_type",values=["price_usd","Profit","order_id","user_id"],\
                  aggfunc={"user_id":"nunique","price_usd":"sum","Profit":"sum","order_id":"sum"})\
.rename(columns={"Profit":"Total_Profit_Earned","order_id" :"Total_Orders","price_usd":"Total_Spend","user_id":"Total_Customers"})\
.reset_index()
    final["Customer_distribution"]=final.Total_Customers/final.Total_Customers.sum()*100
    final["Order_distribution"]=final.Total_Orders/final.Total_Orders.sum()*100
    final["Spend_Contribution"]=final.Total_Spend/final.Total_Spend.sum()*100
    final["AOV"]=final.Total_Spend/final.Total_Orders
    final["Avg_Profit_Earned"]=final.Total_Profit_Earned/final.Total_Customers
    fig=px.bar(final,x="cust_type",y="Spend_Contribution",text=["{:,.2f}".format(x) for x in final.Spend_Contribution])
    fig.update_traces(textposition='outside')  # move labels above bars
    fig.update_layout(yaxis_title="Revenue Contribution",xaxis_title="Customer Type")
    return fig

def plot_sessions_percentage_by_source(sessions):
    """Percentage of sessions per utm_source"""
    pd.read_csv('website_sessions.csv')
    # Count sessions per source
    counts = sessions['utm_source'].value_counts()
    total = counts.sum()
    
    # Convert to dataframe for Plotly
    df = (counts / total * 100).reset_index()
    df.columns = ['utm_source', 'percentage']
    
    # Plot
    fig = px.bar(
        df,
        x='utm_source',
        y='percentage',
        text='percentage',
        title='🌍 Percentage of Sessions per Traffic Source',
        labels={'utm_source': 'Traffic Source', 'percentage': 'Percentage of Sessions (%)'},
        template='plotly_white'
    )
    
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(xaxis_tickangle=45)

    return fig


def plot_customer_order_distribution():
    """Order Distribution by Customer Type (One-Time vs Repeat Buyer)"""
    
    if len(orders) == 0:
        st.warning("⚠️ No data available")
        return None
    
    try:
        # COUNT ORDERS PER USER
        df = orders.pivot_table(
            index="user_id",
            values="order_id",
            aggfunc="nunique"
        ).rename(columns={"order_id": "order_cnt"}).reset_index()
        
        # Classify as One-Time or Repeat Buyer
        df["Cust_Type"] = df.order_cnt.apply(
            lambda x: "One-Time Buyer" if x == 1 else "Repeat Buyer"
        )
        
        # SUM SPENDING AND COST PER USER
        df1 = orders.pivot_table(
            index="user_id",
            values=["price_usd", "cogs_usd"],
            aggfunc="sum"
        ).rename(columns={"cogs_usd": "Total_Cost", "price_usd": "Total_Spend"}).reset_index()
        
        # MERGE BOTH DATAFRAMES
        df2 = pd.merge(left=df, right=df1, how="left", on="user_id")
        
        # AGGREGATE BY CUSTOMER TYPE
        df3 = df2.pivot_table(
            index="Cust_Type",
            values=["user_id", "order_cnt", "Total_Spend", "Total_Cost"],
            aggfunc={
                "user_id": "count",
                "order_cnt": "sum",
                "Total_Spend": "sum",
                "Total_Cost": "sum"
            }
        ).rename(columns={"user_id": "Total_Customers"}).reset_index()
        
        # CALCULATE METRICS
        df3["Profit"] = df3.Total_Spend - df3.Total_Cost
        df3["Order_Distribution"] = df3.order_cnt / df3.order_cnt.sum() * 100
        df3["Customer_Distribution"] = df3.Total_Customers / df3.Total_Customers.sum() * 100
        df3["Revenue_Contribution"] = df3.Total_Spend / df3.Total_Spend.sum() * 100
        df3["AOV"] = df3.Total_Spend / df3.order_cnt
        df3["Profit_per_Cust_type"] = df3.Profit / df3.Total_Customers
        
        # SELECT FINAL COLUMNS
        final = df3[[
            "Cust_Type",
            "Order_Distribution",
            "Customer_Distribution",
            "Revenue_Contribution",
            "AOV",
            "Profit_per_Cust_type"
        ]]
        
        # CREATE PIE CHART
        order_dist = final.set_index('Cust_Type')['Order_Distribution']
        
        fig = px.pie(
            values=order_dist.values,
            names=order_dist.index,
            title='📊 Order Distribution by Customer Type',
            template=plotly_template,
            color_discrete_map={
                'One-Time Buyer': '#66b3ff',
                'Repeat Buyer': '#99ff99'
            }
        )
        
        fig.update_traces(
            textinfo='percent+label+value',
            textposition='auto',
            hovertemplate='<b>%{label}</b><br>Orders: %{value:.0f}<br>Percentage: %{percent}<extra></extra>'
        )
        
        fig.update_layout(height=400)
        
        return fig
    
    except Exception as e:
        st.error(f"Error generating chart: {str(e)}")
        return None

# ============================================================================
# MAIN APP
# ============================================================================

st.title("📊 Website Performance & Channel Portfolio Dashboard")

st.markdown("""
    Welcome to your comprehensive website analytics dashboard. 
    Select different analyses from the sidebar to explore your data.
""")


# ============================================================================
# NEW TRAFFIC SOURCE ANALYSIS FUNCTIONS
# ============================================================================

def plot_conversion_rate_contribution_by_source(sessions, orders):
    """Percentage contribution of conversion rate by utm_source"""

    # Merge to identify which sessions converted
    merged = sessions.merge(
        orders[['website_session_id', 'order_id']],
        on='website_session_id',
        how='left'
    )

    # Aggregate conversions by utm_source
    agg = merged.groupby('utm_source').agg(
        sessions=('website_session_id', 'nunique'),
        conversions=('order_id', lambda x: x.nunique(dropna=True))
    ).reset_index()

    # Compute conversion rate
    agg['conversion_rate'] = agg['conversions'] / agg['sessions'] * 100

    # Calculate share contribution of conversion rate
    total_rate = agg['conversion_rate'].sum()
    if total_rate == 0:
        agg['conversion_rate_share'] = 0
    else:
        agg['conversion_rate_share'] = (agg['conversion_rate'] / total_rate) * 100

    # Plotly bar chart
    fig = px.bar(
        agg,
        x='utm_source',
        y='conversion_rate_share',
        text='conversion_rate_share',
        title='🔥 Conversion Rate Contribution by Traffic Source',
        labels={'utm_source': 'Traffic Source', 'conversion_rate_share': 'Contribution (%)'},
        template='plotly_white'
    )

    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(xaxis_tickangle=45, height=500)

    return fig

def plot_device_share_by_traffic_source(sessions):
    """Device type share within each traffic source (utm_source)"""

    # Group sessions by utm_source and device_type
    grouped = sessions.groupby(['utm_source', 'device_type']).size().reset_index(name='count')

    # Calculate percentage share within each utm_source group
    grouped['pct'] = grouped.groupby('utm_source')['count'].transform(lambda x: (x / x.sum()) * 100)

    # Plot with Plotly
    fig = px.bar(
        grouped,
        x='utm_source',
        y='pct',
        color='device_type',
        barmode='group',
        text='pct',
        title='📱 Device Type Share within Each Traffic Source',
        labels={'utm_source': 'Traffic Source', 'pct': 'Percentage of Sessions (%)', 'device_type': 'Device Type'},
        template='plotly_white'
    )

    # Data label formatting
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(xaxis_tickangle=45, legend_title_text="Device Type", height=500)

    return fig

def plot_pages_per_session_box_by_source(sessions, pageviews):
    """Boxplot of pages_per_session by utm_source"""

    # pages per session
    pagecounts = pageviews.groupby('website_session_id').size().reset_index(name='pages_per_session')
    joined = sessions.merge(pagecounts, on='website_session_id', how='left').fillna({'pages_per_session': 0})
    joined['pages_per_session'] = joined['pages_per_session'].astype(float)

    fig = px.box(
        joined,
        x='utm_source',
        y='pages_per_session',
        points='outliers',
        title='📚 Pages per Session by Traffic Source',
        labels={'utm_source': 'utm_source', 'pages_per_session': 'Pages per Session'},
        template='plotly_white'
    )

    # Add median annotations
    medians = joined.groupby('utm_source')['pages_per_session'].median().reset_index()
    annotations = []
    for i, row in medians.iterrows():
        annotations.append(dict(
            x=row['utm_source'],
            y=row['pages_per_session'] + 0.2,
            text=f"med {row['pages_per_session']:.1f}",
            showarrow=False,
            yanchor='bottom'
        ))
    fig.update_layout(annotations=annotations, xaxis_tickangle=45, height=500)
    return fig

def plot_pageview_url_conversion_rate_share(sessions, orders, pageviews, top_n=None):
    """Horizontal bar chart of conversion-rate contribution per page_view_url"""

    # Link pageviews to sessions via website_session_id, then to orders
    pv_sessions = pageviews[['website_session_id', 'pageview_url']].drop_duplicates()
    merged = sessions.merge(pv_sessions, on='website_session_id', how='left')
    merged = merged.merge(orders[['website_session_id', 'order_id']], on='website_session_id', how='left')

    agg = merged.groupby('pageview_url').agg(
        sessions=('website_session_id', 'nunique'),
        conversions=('order_id', 'nunique')
    ).reset_index()

    # Drop NaN page_view_url
    agg = agg.dropna(subset=['pageview_url']).copy()
    agg['conversion_rate'] = agg['conversions'] / agg['sessions'] * 100

    # If user wants to limit, take top by conversion_rate
    if top_n is not None:
        display_df = agg.sort_values('conversion_rate', ascending=False).head(top_n)
    else:
        display_df = agg.sort_values('conversion_rate', ascending=False)

    # avoid zero-sum
    total_rate = display_df['conversion_rate'].sum()
    if total_rate == 0:
        display_df['pct_of_total_conv_rate'] = 0
    else:
        display_df['pct_of_total_conv_rate'] = display_df['conversion_rate'] / total_rate * 100

    fig = px.bar(
        display_df,
        x='pct_of_total_conv_rate',
        y='pageview_url',
        orientation='h',
        title='🌐 Pageview URL — Conversion Rate Contribution',
        labels={'pct_of_total_conv_rate': 'Conversion Rate Contribution (%)', 'pageview_url': 'Pageview URL'},
        text='pct_of_total_conv_rate',
        template='plotly_white'
    )
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(l=300), height=600)
    return fig

def plot_top_campaign_content_conversion_share(sessions, orders, top_n=10):
    """Top N campaign & content combos by conversion rate share"""

    # Merge sessions and orders
    merged = sessions.merge(
        orders[['website_session_id', 'order_id']],
        on='website_session_id',
        how='left'
    )

    # Group and compute metrics
    agg = merged.groupby(['utm_campaign', 'utm_content']).agg(
        sessions=('website_session_id', 'nunique'),
        conversions=('order_id', 'nunique')
    ).reset_index()

    agg['conversion_rate'] = (agg['conversions'] / agg['sessions']) * 100

    # Select top N by conversion rate
    top = agg.sort_values('conversion_rate', ascending=False).head(top_n)
    total_rate = top['conversion_rate'].sum()
    if total_rate == 0:
        top['pct_share'] = 0
    else:
        top['pct_share'] = (top['conversion_rate'] / total_rate) * 100

    # Create label for better display
    top['label'] = top['utm_campaign'].astype(str) + ' — ' + top['utm_content'].astype(str)

    # Plot with Plotly
    fig = px.bar(
        top,
        x='pct_share',
        y='label',
        color='utm_campaign',
        orientation='h',
        text='pct_share',
        title=f'🎯 Top {top_n} Campaign & Content Combos by Conversion Rate',
        labels={'pct_share': 'Conversion Rate Share (%)', 'label': 'Campaign — Content'},
        template='plotly_white'
    )

    fig.update_traces(texttemplate='%{text:.1f}%', textposition='auto')
    fig.update_layout(legend_title_text="UTM Campaign", height=600, yaxis={'categoryorder':'total ascending'})

    return fig

def plot_time_to_conversion_by_source(sessions, orders):
    """Time to conversion (in hours) by traffic source"""

    # Rename order timestamp to avoid confusion
    orders_copy = orders.rename(columns={"created_at": "order_created_at"})

    # Merge sessions and orders
    merged = sessions.merge(
        orders_copy[["website_session_id", "order_id", "order_created_at"]],
        on="website_session_id",
        how="inner"
    )

    # Calculate time to conversion in hours
    merged["time_to_conversion_hrs"] = (
        merged["order_created_at"] - merged["created_at"]
    ).dt.total_seconds() / 3600.0

    # Create box plot
    fig = px.box(
        merged,
        x="utm_source",
        y="time_to_conversion_hrs",
        points="outliers",
        title="⏱️ Time to Conversion (Hours) by Traffic Source",
        labels={"utm_source": "Traffic Source", "time_to_conversion_hrs": "Time to Conversion (hrs)"},
        template="plotly_white"
    )

    # Show median lines
    fig.update_traces(boxmean="sd")
    fig.update_layout(xaxis_tickangle=45, height=500)

    # Add median annotations
    medians = merged.groupby('utm_source')['time_to_conversion_hrs'].median().reset_index()
    annotations = []
    for i, row in medians.iterrows():
        annotations.append(dict(
            x=row['utm_source'],
            y=row['time_to_conversion_hrs'] + 1,
            text=f"med {row['time_to_conversion_hrs']:.1f}h",
            showarrow=False,
            yanchor='bottom'
        ))
    fig.update_layout(annotations=annotations)

    return fig

def plot_funnel_dropoff_by_source(sessions, pageviews, orders):
    """Funnel drop-off rate by utm_source"""

    # Count sessions per source
    sess_count = sessions.groupby('utm_source')['website_session_id'].nunique().reset_index(name='sessions')

    # Count pageviews per session
    pv_count = pageviews.groupby('website_session_id').size().reset_index(name='pv_count')
    joined = sessions.merge(pv_count, on='website_session_id', how='left')
    joined['pv_count'] = joined['pv_count'].fillna(0)

    # Count conversions
    conv_count = orders.groupby('website_session_id')['order_id'].nunique().reset_index(name='conversions')
    joined2 = joined.merge(conv_count, on='website_session_id', how='left').fillna({'conversions': 0})

    # Aggregate by source
    agg = joined2.groupby('utm_source').agg(
        sessions=('website_session_id', 'nunique'),
        conversions=('conversions', 'sum')
    ).reset_index()

    # Compute conversion & drop-off
    agg['conversion_rate'] = (agg['conversions'] / agg['sessions']) * 100
    agg['drop_off_rate'] = 100 - agg['conversion_rate']

    # Plot
    fig = px.bar(
        agg,
        x='utm_source',
        y='drop_off_rate',
        text='drop_off_rate',
        title='🔻 Funnel Drop-Off Rate by Traffic Source',
        labels={'utm_source': 'Traffic Source', 'drop_off_rate': 'Drop-Off Rate (%)'},
        template='plotly_white'
    )

    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(xaxis_tickangle=45, yaxis_range=[0, agg['drop_off_rate'].max() + 10], height=500)

    return fig

def plot_entrance_rate_by_page_source(sessions, pageviews):
    """Entrance Rate by Page (landing page) by Source"""

    # Get first pageview per session (landing page)
    pv = pageviews.copy()
    pv_sorted = pv.sort_values(['website_session_id', 'created_at'])
    first_pv = pv_sorted.groupby('website_session_id', sort=False).first().reset_index()[['website_session_id','pageview_url']]

    # Join with sessions to get utm_source
    joined = sessions[['website_session_id','utm_source']].merge(first_pv, on='website_session_id', how='left')
    joined['pageview_url'] = joined['pageview_url'].fillna('(none)')
    joined['utm_source'] = joined['utm_source'].fillna('(none)')

    # Aggregate
    agg = joined.groupby(['utm_source','pageview_url']).size().reset_index(name='count')
    agg['pct'] = agg.groupby('utm_source')['count'].transform(lambda x: x / x.sum() * 100)

    # Sort by percentage
    top = agg.sort_values('pct', ascending=False).head(20)

    # Use full pageview_url on y axis
    fig = px.bar(
        top, 
        x='pct', 
        y='pageview_url', 
        color='utm_source', 
        orientation='h',
        title='🚪 Entrance Rate by Landing Page & Source (Top 20)',
        labels={'pct':'Entrance Rate (%)','pageview_url':'Landing Page', 'utm_source': 'Traffic Source'}
    )
    fig.update_layout(
        yaxis={'categoryorder':'total ascending'}, 
        height=max(500, 30*len(top['pageview_url'].unique())),
        margin=dict(l=250)
    )
    fig.update_traces(text=top['pct'].round(1), textposition='outside')
    return fig

def plot_returning_sessions_share_by_source(sessions):
    """Returning Sessions Rate by Traffic Source"""

    # Ensure correct ordering before detecting returns
    sessions_sorted = sessions.sort_values(['user_id','created_at'])

    # Mark sessions after the first as returning for the same user
    sessions_sorted['is_returning'] = sessions_sorted.duplicated(subset=['user_id'], keep='first').astype(int)

    # Aggregate metrics
    agg = (
        sessions_sorted
        .groupby('utm_source')
        .agg(
            total_sessions=('website_session_id', 'nunique'),
            returning_sessions=('is_returning','sum')
        )
        .reset_index()
    )

    agg['returning_rate'] = agg['returning_sessions'] / agg['total_sessions'] * 100

    # Plot
    fig = px.bar(
        agg,
        x='utm_source',
        y='returning_rate',
        text='returning_rate',
        title='🔄 Returning Sessions Rate by Traffic Source',
        labels={'utm_source': 'Traffic Source', 'returning_rate': 'Returning Sessions (%)'},
        template='plotly_white',
        color='returning_rate',
        color_continuous_scale='Purples'
    )

    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(xaxis_tickangle=45, yaxis_range=[0, agg['returning_rate'].max() * 1.15], height=500)

    return fig


# Sidebar Navigation
st.sidebar.title("🎯 Navigation")
analysis_category = st.sidebar.radio(
    "Select Category",
    [
        "Session Analysis",
        "Page Performance",
        "Conversion Analysis",
        "Channel Portfolio",
        "User Analysis",
        "Traffic Source Analysis",
        "Business pattern and seasonality Analysis"
    ]
)

# SESSION ANALYSIS
if analysis_category == "Session Analysis":
    st.header("📈 Session Analysis")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Daily Session Trends")
        st.plotly_chart(plot_daily_session_trends(), use_container_width=True)
        
        st.subheader("New vs Repeat Users")
        st.plotly_chart(plot_repeat_vs_new_users(), use_container_width=True)

    with col2:
        st.subheader("Sessions by Source & Device")
        st.plotly_chart(plot_sessions_by_source_device(), use_container_width=True)

    with col3:
        st.subheader("Device Distribution")
        st.plotly_chart(plot_device_distribution(), use_container_width=True)
    
    


# PAGE PERFORMANCE
elif analysis_category == "Page Performance":
    st.header("📄 Page Performance Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top Pages")
        st.plotly_chart(plot_top_pages(), use_container_width=True)
        
        st.subheader("Landing Pages")
        st.plotly_chart(plot_landing_pages(), use_container_width=True)
        
        st.subheader("Bounce Rate")
        st.plotly_chart(plot_bounce_rate_by_landing_page(), use_container_width=True)

    with col2:
        st.subheader("Exit Pages")
        st.plotly_chart(plot_exit_pages(), use_container_width=True)
        
        st.subheader("Pageviews Distribution")
        st.plotly_chart(plot_pageviews_boxplot(), use_container_width=True)

# CONVERSION ANALYSIS
elif analysis_category == "Conversion Analysis":
    st.header("💰 Conversion Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Conversion by Source")
        st.plotly_chart(plot_conversion_rate_by_source(), use_container_width=True)

    with col2:
        st.subheader("Conversion by Landing Page")
        st.plotly_chart(plot_conversion_rate_by_landing_page(), use_container_width=True)
    with col1:
        st.subheader("Conversion Rate by Channel")
        st.plotly_chart(plot_conversion_rate_by_channel(), use_container_width=True)    

# CHANNEL PORTFOLIO
elif analysis_category == "Channel Portfolio":
    st.header("🎯 Channel Portfolio Management")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Sessions by Channel")
        st.plotly_chart(plot_sessions_by_channel(), use_container_width=True)

        st.subheader("Orders by Channel")
        st.plotly_chart(plot_orders_by_channel(), use_container_width=True)

        st.subheader("AOV by Channel")
        st.plotly_chart(plot_aov_by_channel(), use_container_width=True)

    with col2:
        st.subheader("Channel & Device")
        st.plotly_chart(plot_sessions_by_channel_device(), use_container_width=True)

        st.subheader("New vs Repeat by Channel")
        st.plotly_chart(plot_new_vs_returning_by_channel(), use_container_width=True)

        st.subheader("Top Campaigns")
        st.plotly_chart(plot_top_campaigns(), use_container_width=True)

    st.subheader("Channel Share Trend")
    st.plotly_chart(plot_channel_share_trend(), use_container_width=True)   

    st.subheader("Channel Funnel")
    st.plotly_chart(plot_channel_funnel(), use_container_width=True)

# USER ANALYSIS
elif analysis_category == "User Analysis":
    st.header("👥 User Analysis")

    st.subheader("📊 One-Time vs Repeat Buyer Analysis")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Customer Distribution by Customer Type")
        st.plotly_chart(plot_one_time_vs_repeat_customer_distribution(), use_container_width=True)

    with col2:
        st.subheader("Order Distribution by Customer Type")
        st.plotly_chart(plot_one_time_vs_repeat_order_distribution(), use_container_width=True)

    with col3:
        st.subheader("Revenue Contribution by Customer Type")
        st.plotly_chart(plot_one_time_vs_repeat_revenue_distribution(), use_container_width=True)

    
    st.markdown('---')
    st.subheader("📊 RFM Segmentation")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Customer Distribution Across Segments")
        st.plotly_chart(plot_rfm_cust_distribution(), use_container_width=True)

    with col2:
        st.subheader("Revenue Contribution Across Segments")
        st.plotly_chart(plot_rfm_revenue_contribution(), use_container_width=True)

    st.subheader("Cohort Retention Heatmap")
    st.plotly_chart(plot_cohort_retention_heatmap(), use_container_width=True)

    st.subheader('Monthly Contribution: Existing vs New Customers')
    st.plotly_chart(plot_revenue_from_new_and_existing(), use_container_width=True)

    st.subheader('Customer Journey Analysis')
    st.plotly_chart(plot_cust_journey_analysis(), use_container_width=True)

    st.subheader("📊 Single Product vs Multiple Product Buyer Analysis")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Customer Distribution by Customer Type")
        st.plotly_chart(plot_single_vs_multiple_prod_cust_distribution(), use_container_width=True)

    with col2:
        st.subheader("Order Distribution by Customer Type")
        st.plotly_chart(plot_single_vs_multiple_prod_order_distribution(), use_container_width=True)

    with col3:
        st.subheader("Revenue Contribution by Customer Type")
        st.plotly_chart(plot_single_vs_multiple_prod_revenue_contribution(), use_container_width=True)

# TRAFFIC SOURCE ANALYSIS
elif analysis_category == "Traffic Source Analysis":
    st.header("🌐 Advanced Traffic Source Analysis")

    st.markdown("### Session & Conversion Metrics by Source")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Sessions by Traffic Source")
        st.plotly_chart(plot_sessions_percentage_by_source(sessions), use_container_width=True)

    with col2:
        st.subheader("Conversion Rate Contribution")
        st.plotly_chart(plot_conversion_rate_contribution_by_source(sessions, orders), use_container_width=True)

    st.markdown('---')
    st.markdown("### Device & Engagement Analysis")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Device Share by Traffic Source")
        st.plotly_chart(plot_device_share_by_traffic_source(sessions), use_container_width=True)

    with col2:
        st.subheader("Pages per Session Distribution")
        st.plotly_chart(plot_pages_per_session_box_by_source(sessions, pageviews), use_container_width=True)

    st.markdown('---')
    st.markdown("### Page & Campaign Performance")

    st.subheader("Pageview URL Conversion Contribution")
    top_n_pages = st.slider("Number of pages to display", min_value=5, max_value=20, value=15, key="pageview_slider")
    st.plotly_chart(plot_pageview_url_conversion_rate_share(sessions, orders, pageviews, top_n=top_n_pages), use_container_width=True)

    st.subheader("Top Campaign & Content Combinations")
    top_n_campaigns = st.slider("Number of campaigns to display", min_value=5, max_value=20, value=10, key="campaign_slider")
    st.plotly_chart(plot_top_campaign_content_conversion_share(sessions, orders, top_n=top_n_campaigns), use_container_width=True)

    st.markdown('---')
    st.markdown("### Conversion Behavior Analysis")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Time to Conversion by Source")
        st.plotly_chart(plot_time_to_conversion_by_source(sessions, orders), use_container_width=True)

    with col2:
        st.subheader("Funnel Drop-Off Rate")
        st.plotly_chart(plot_funnel_dropoff_by_source(sessions, pageviews, orders), use_container_width=True)

    st.markdown('---')
    st.markdown("### Landing Page & User Retention")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Entrance Rate by Landing Page")
        st.plotly_chart(plot_entrance_rate_by_page_source(sessions, pageviews), use_container_width=True)

    with col2:
        st.subheader("Returning Sessions Share")
        st.plotly_chart(plot_returning_sessions_share_by_source(sessions), use_container_width=True)


if analysis_category == "Market Analysis":
    st.header("📊 Market Analysis")
    st.subheader("Customer Behavior")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(plot_one_time_vs_repeat_customer_distribution(), use_container_width=True)
    with col2:
        st.plotly_chart(plot_one_time_vs_repeat_order_distribution(), use_container_width=True)
    st.markdown('---')
    st.markdown("### Customer Revenue Metrics")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(plot_one_time_vs_repeat_revenue_distribution(), use_container_width=True)
    with col2:
        st.plotly_chart(plot_rfm_cust_distribution(), use_container_width=True)
    st.markdown('---')
    st.markdown("### RFM Analysis")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(plot_rfm_revenue_contribution(), use_container_width=True)
    with col2:
        st.plotly_chart(plot_cohort_retention_heatmap(), use_container_width=True)

elif analysis_category == "Device Insights":
    st.header("📱 Device Insights")
    st.markdown("Understand how different devices contribute to your website performance")
    st.markdown('---')
    st.markdown("### Overall Device Metrics")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(plot_device_distribution(), use_container_width=True)
    with col2:
        st.plotly_chart(plot_sessions_by_source_device(), use_container_width=True)
    st.markdown('---')
    st.markdown("### Device & Conversion")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(plot_device_share_by_traffic_source(), use_container_width=True)
    with col2:
        st.plotly_chart(plot_pages_per_session_box_by_source(), use_container_width=True)

elif analysis_category == "Traffic Source Analysis":
    st.header("🌐 Traffic Source Analysis")
    st.markdown("Deep dive into traffic sources and their performance")
    st.markdown('---')
    st.markdown("### Traffic Source Overview")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(plot_sessions_percentage_by_source(), use_container_width=True)
    with col2:
        st.plotly_chart(plot_sessions_by_channel(), use_container_width=True)
    st.markdown('---')
    st.markdown("### Traffic Channel Performance")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(plot_orders_by_channel(), use_container_width=True)
    with col2:
        st.plotly_chart(plot_conversion_rate_by_channel(), use_container_width=True)
    st.markdown('---')
    st.markdown("### Channel Trends & Funnel")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(plot_channel_share_trend(), use_container_width=True)
    with col2:
        st.plotly_chart(plot_new_vs_returning_by_channel(), use_container_width=True)
    st.markdown('---')
    st.markdown("### Advanced Metrics")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(plot_channel_funnel(), use_container_width=True)
    with col2:
        st.plotly_chart(plot_top_campaigns(), use_container_width=True)
    st.markdown('---')
    st.markdown("### Page & Campaign Performance")
    st.subheader("Pageview URL Conversion Contribution")
    st.plotly_chart(plot_pageview_url_conversion_rate_share(), use_container_width=True)
    st.subheader("Top Campaign & Content Combinations")
    st.plotly_chart(plot_top_campaign_content_conversion_share(), use_container_width=True)
    st.markdown('---')
    st.markdown("### Conversion Behavior Analysis")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(plot_time_to_conversion_by_source(), use_container_width=True)
    with col2:
        st.plotly_chart(plot_funnel_dropoff_by_source(), use_container_width=True)
    st.markdown('---')
    st.markdown("### Landing Page & User Retention")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(plot_entrance_rate_by_page_source(), use_container_width=True)
    with col2:
        st.plotly_chart(plot_returning_sessions_share_by_source(), use_container_width=True)

# Business pattern and seasonality Analysis

elif analysis_category == "Business pattern and seasonality Analysis":
    st.header("📊 Data Analysis")
    st.markdown("Advanced data insights including monthly trends, daily patterns, hourly sessions, and product performance")
    
    st.markdown("---")
    st.subheader("📈 Monthly Trends")
    
    col1, col2 = st.columns(2)
    with col1:
        try:
            fig_monthly = plot_monthly_sales_revenue(orders)
            st.plotly_chart(fig_monthly, use_container_width=True)
        except Exception as e:
            st.warning(f"⚠️ Could not load monthly trends: {str(e)}")
    
    with col2:
        try:
            fig_daily = plot_daily_sales_revenue(orders)
            st.plotly_chart(fig_daily, use_container_width=True)
        except Exception as e:
            st.warning(f"⚠️ Could not load daily trends: {str(e)}")
    
    st.markdown("---")
    st.subheader("⏰ Hourly & Product Analysis")
    
    col1, col2 = st.columns(2)
    with col1:
        try:
            fig_hourly = plot_hourly_sessions(sessions)
            st.plotly_chart(fig_hourly, use_container_width=True)
        except Exception as e:
            st.warning(f"⚠️ Could not load hourly data: {str(e)}")
    
    with col2:
        try:
            products_df = pd.read_csv('products.csv')
            fig_product = plot_product_sales(orders, products_df)
            st.plotly_chart(fig_product, use_container_width=True)
        except FileNotFoundError:
            st.warning("⚠️ products.csv not found. Please add it to analyze product performance.")
        except Exception as e:
            st.warning(f"⚠️ Could not load product data: {str(e)}")



# Footer
st.markdown("---")
st.markdown("<p style='text-align:center; color:#666; padding:20px;'>📊 Professional Website Analytics Dashboard | Built with Streamlit</p>", unsafe_allow_html=True)
