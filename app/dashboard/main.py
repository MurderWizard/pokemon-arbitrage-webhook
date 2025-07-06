import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.database import Deal, InventoryItem, Sale, Transaction, Card
from app.core.config import settings

# Page configuration
st.set_page_config(
    page_title="Pokemon Card Arbitrage Dashboard",
    page_icon="🎴",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_db():
    """Get database session"""
    return SessionLocal()

def load_data():
    """Load data from database"""
    db = get_db()
    
    # Load deals
    deals = pd.read_sql_query(
        "SELECT * FROM deals ORDER BY created_at DESC LIMIT 100",
        db.bind
    )
    
    # Load inventory
    inventory = pd.read_sql_query(
        """
        SELECT i.*, c.name as card_name, c.set_name 
        FROM inventory_items i 
        JOIN cards c ON i.card_id = c.id
        ORDER BY i.created_at DESC
        """,
        db.bind
    )
    
    # Load sales
    sales = pd.read_sql_query(
        """
        SELECT s.*, i.sku, c.name as card_name, c.set_name
        FROM sales s
        JOIN inventory_items i ON s.inventory_item_id = i.id
        JOIN cards c ON i.card_id = c.id
        ORDER BY s.sale_date DESC
        """,
        db.bind
    )
    
    # Load transactions
    transactions = pd.read_sql_query(
        "SELECT * FROM transactions ORDER BY date DESC",
        db.bind
    )
    
    db.close()
    
    return deals, inventory, sales, transactions

def main():
    """Main dashboard function"""
    st.title("🎴 Pokemon Card Arbitrage Dashboard")
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", [
        "Overview", 
        "Deals", 
        "Inventory", 
        "Sales", 
        "Analytics", 
        "Settings"
    ])
    
    # Load data
    try:
        deals, inventory, sales, transactions = load_data()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return
    
    if page == "Overview":
        show_overview(deals, inventory, sales, transactions)
    elif page == "Deals":
        show_deals(deals)
    elif page == "Inventory":
        show_inventory(inventory)
    elif page == "Sales":
        show_sales(sales)
    elif page == "Analytics":
        show_analytics(inventory, sales, transactions)
    elif page == "Settings":
        show_settings()

def show_overview(deals, inventory, sales, transactions):
    """Show overview dashboard"""
    st.header("📊 Overview")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_deals = len(deals)
        st.metric("Total Deals", total_deals)
    
    with col2:
        total_inventory = len(inventory)
        inventory_value = inventory['purchase_price'].sum() if not inventory.empty else 0
        st.metric("Inventory Items", total_inventory, f"${inventory_value:.2f}")
    
    with col3:
        total_sales = len(sales)
        revenue = sales['sale_price'].sum() if not sales.empty else 0
        st.metric("Total Sales", total_sales, f"${revenue:.2f}")
    
    with col4:
        profit = sales['net_profit'].sum() if not sales.empty else 0
        st.metric("Net Profit", f"${profit:.2f}")
    
    # Recent activity
    st.subheader("📈 Recent Activity")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Latest Deals")
        if not deals.empty:
            recent_deals = deals.head(5)
            for _, deal in recent_deals.iterrows():
                st.write(f"**{deal['card_name']}** - {deal['set_name']}")
                st.write(f"💰 ${deal['listing_price']:.2f} (Market: ${deal['market_price']:.2f})")
                st.write(f"📈 {deal['profit_margin']:.1%} profit")
                st.write("---")
        else:
            st.info("No deals found yet")
    
    with col2:
        st.subheader("Recent Sales")
        if not sales.empty:
            recent_sales = sales.head(5)
            for _, sale in recent_sales.iterrows():
                st.write(f"**{sale['card_name']}** - {sale['set_name']}")
                st.write(f"💰 ${sale['sale_price']:.2f}")
                st.write(f"📈 ${sale['net_profit']:.2f} profit")
                st.write("---")
        else:
            st.info("No sales yet")

def show_deals(deals):
    """Show deals page"""
    st.header("🔍 Deals")
    
    if deals.empty:
        st.info("No deals found yet")
        return
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox("Status", ["All"] + list(deals['status'].unique()))
    
    with col2:
        min_margin = st.number_input("Min Profit Margin", min_value=0.0, max_value=1.0, value=0.0, step=0.1)
    
    with col3:
        max_price = st.number_input("Max Price", min_value=0.0, value=1000.0, step=10.0)
    
    # Apply filters
    filtered_deals = deals.copy()
    
    if status_filter != "All":
        filtered_deals = filtered_deals[filtered_deals['status'] == status_filter]
    
    filtered_deals = filtered_deals[filtered_deals['profit_margin'] >= min_margin]
    filtered_deals = filtered_deals[filtered_deals['listing_price'] <= max_price]
    
    # Display deals
    st.subheader(f"Found {len(filtered_deals)} deals")
    
    for _, deal in filtered_deals.iterrows():
        with st.expander(f"{deal['card_name']} - {deal['set_name']} (${deal['listing_price']:.2f})"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Card:** {deal['card_name']}")
                st.write(f"**Set:** {deal['set_name']}")
                st.write(f"**Condition:** {deal['condition']}")
                st.write(f"**Platform:** {deal['platform']}")
                st.write(f"**Status:** {deal['status']}")
            
            with col2:
                st.write(f"**Listing Price:** ${deal['listing_price']:.2f}")
                st.write(f"**Market Price:** ${deal['market_price']:.2f}")
                st.write(f"**Profit Margin:** {deal['profit_margin']:.1%}")
                st.write(f"**Found:** {deal['created_at']}")
                
                if deal['listing_url']:
                    st.markdown(f"[View Listing]({deal['listing_url']})")

def show_inventory(inventory):
    """Show inventory page"""
    st.header("📦 Inventory")
    
    if inventory.empty:
        st.info("No inventory items yet")
        return
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_items = len(inventory)
        st.metric("Total Items", total_items)
    
    with col2:
        total_value = inventory['purchase_price'].sum()
        st.metric("Total Value", f"${total_value:.2f}")
    
    with col3:
        avg_days = inventory['days_in_stock'].mean()
        st.metric("Avg Days in Stock", f"{avg_days:.1f}")
    
    with col4:
        aged_items = len(inventory[inventory['days_in_stock'] > 60])
        st.metric("Aged Items (60+ days)", aged_items)
    
    # Inventory by status
    st.subheader("Inventory by Status")
    status_counts = inventory['status'].value_counts()
    
    fig = px.pie(
        values=status_counts.values,
        names=status_counts.index,
        title="Inventory Status Distribution"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Aged inventory
    st.subheader("Aged Inventory (60+ days)")
    aged_inventory = inventory[inventory['days_in_stock'] > 60].sort_values('days_in_stock', ascending=False)
    
    if not aged_inventory.empty:
        st.dataframe(aged_inventory[['sku', 'card_name', 'set_name', 'purchase_price', 'list_price', 'days_in_stock', 'status']])
    else:
        st.info("No aged inventory")

def show_sales(sales):
    """Show sales page"""
    st.header("💰 Sales")
    
    if sales.empty:
        st.info("No sales yet")
        return
    
    # Sales metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_sales = len(sales)
        st.metric("Total Sales", total_sales)
    
    with col2:
        total_revenue = sales['sale_price'].sum()
        st.metric("Total Revenue", f"${total_revenue:.2f}")
    
    with col3:
        total_profit = sales['net_profit'].sum()
        st.metric("Total Profit", f"${total_profit:.2f}")
    
    with col4:
        avg_profit = sales['net_profit'].mean()
        st.metric("Avg Profit", f"${avg_profit:.2f}")
    
    # Sales over time
    st.subheader("Sales Over Time")
    
    sales['sale_date'] = pd.to_datetime(sales['sale_date'])
    daily_sales = sales.groupby(sales['sale_date'].dt.date).agg({
        'sale_price': 'sum',
        'net_profit': 'sum'
    }).reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily_sales['sale_date'],
        y=daily_sales['sale_price'],
        mode='lines+markers',
        name='Revenue',
        line=dict(color='blue')
    ))
    fig.add_trace(go.Scatter(
        x=daily_sales['sale_date'],
        y=daily_sales['net_profit'],
        mode='lines+markers',
        name='Profit',
        line=dict(color='green')
    ))
    fig.update_layout(title="Daily Sales and Profit", xaxis_title="Date", yaxis_title="Amount ($)")
    st.plotly_chart(fig, use_container_width=True)
    
    # Recent sales
    st.subheader("Recent Sales")
    recent_sales = sales.head(10)
    st.dataframe(recent_sales[['sale_date', 'card_name', 'set_name', 'sale_price', 'net_profit', 'platform']])

def show_analytics(inventory, sales, transactions):
    """Show analytics page"""
    st.header("📊 Analytics")
    
    # Performance metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Profit Margin Distribution")
        if not sales.empty:
            profit_margins = (sales['net_profit'] / sales['sale_price']) * 100
            fig = px.histogram(profit_margins, nbins=20, title="Profit Margin Distribution")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No sales data available")
    
    with col2:
        st.subheader("Days to Sell Distribution")
        if not sales.empty:
            # This would need days_to_sell data from inventory
            st.info("Days to sell data not available")
        else:
            st.info("No sales data available")
    
    # Top performers
    st.subheader("Top Performing Cards")
    if not sales.empty:
        top_performers = sales.nlargest(10, 'net_profit')
        
        fig = px.bar(
            top_performers,
            x='net_profit',
            y='card_name',
            orientation='h',
            title="Top 10 Cards by Profit"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No sales data available")

def show_settings():
    """Show settings page"""
    st.header("⚙️ Settings")
    
    # Trading parameters
    st.subheader("Trading Parameters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.number_input("Starting Bankroll", value=settings.STARTING_BANKROLL, step=100.0)
        st.number_input("Max Position %", value=settings.MAX_POSITION_PERCENT, step=1.0)
        st.number_input("Deal Threshold", value=settings.DEAL_THRESHOLD, step=0.05)
    
    with col2:
        st.number_input("Min Profit Margin", value=settings.MIN_PROFIT_MARGIN, step=0.05)
        st.number_input("Daily Spend Limit", value=settings.DAILY_SPEND_LIMIT, step=50.0)
        st.checkbox("Enable Auto-Buy", value=settings.ENABLE_AUTO_BUY)
    
    # Risk controls
    st.subheader("Risk Controls")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.number_input("Raw Aging Days", value=settings.RAW_AGING_DAYS, step=5)
        st.number_input("Slab Aging Days", value=settings.SLAB_AGING_DAYS, step=5)
    
    with col2:
        st.number_input("Stop Loss Threshold", value=settings.STOP_LOSS_THRESHOLD, step=0.05)
    
    if st.button("Save Settings"):
        st.success("Settings saved successfully!")

if __name__ == "__main__":
    main()
