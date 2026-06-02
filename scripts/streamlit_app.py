import os
import sqlite3
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from pathlib import Path

# Path-safe resolution
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = os.path.join(BASE_DIR, "data", "db", "bluestock_mf.db")

st.set_page_config(page_title="Bluestock MF Analytics", layout="wide", page_icon="📈")

@st.cache_data
def fetch_fund_data():
    """Reads database securely and maps tracking data structures."""
    if not os.path.exists(DB_PATH):
        st.error("Database file missing! Run `python scripts/etl_pipeline.py` first.")
        return pd.DataFrame(), pd.DataFrame()
        
    conn = sqlite3.connect(DB_PATH)
    df_nav = pd.read_sql_query("SELECT * FROM nav_history ORDER BY nav_date ASC;", conn)
    df_master = pd.read_sql_query("SELECT * FROM fund_master;", conn)
    conn.close()
    
    df_nav["nav_date"] = pd.to_datetime(df_nav["nav_date"])
    # Merge names for crisp rendering
    df_complete = df_nav.merge(df_master, on="scheme_code")
    return df_complete, df_master

# Load cached data matrices
df_clean, df_master = fetch_fund_data()

if df_clean.empty:
    st.stop()

# --- SIDEBAR INTERACTIVE CONTROL FILTERS ---
st.sidebar.header("Navigation & Controls")
target_fund = st.sidebar.selectbox("Select Target Mutual Fund", df_master["scheme_name"].unique())
sim_runs = st.sidebar.slider("Monte Carlo Simulations", min_value=100, max_value=2000, value=1000, step=100)

# Isolate data rows belonging strictly to selected scope
fund_df = df_clean[df_clean["scheme_name"] == target_fund].sort_values("nav_date")
latest_nav = fund_df["nav"].iloc[-1]
latest_date = fund_df["nav_date"].iloc[-1].strftime('%Y-%m-%d')

# --- MAIN DASHBOARD FRAMEWORK ---
st.title("📈 Bluestock Mutual Fund Analytics Workspace")
st.caption(f"Production Framework Engine | Active Scheme Focus: {target_fund}")

# Row 1: High-Level Operational KPI Cards
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Latest Asset Value (NAV)", f"₹{latest_nav:,.2f}", delta=f"As of {latest_date}")
with col2:
    st.metric("Total Historical Timeline", f"{len(fund_df):,} Days")
with col3:
    st.metric("Category / Risk Allocation", fund_df["sub_category"].iloc[0], delta=fund_df["risk_grade"].iloc[0], delta_color="inverse")

st.markdown("---")

# Tab Management Layout
tab1, tab2 = st.tabs(["📊 Historical Trajectory", "🔮 5-Year Monte Carlo Projections"])

with tab1:
    st.subheader("Time-Series Price Performance")
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Scatter(x=fund_df["nav_date"], y=fund_df["nav"], mode='lines', name='NAV', line=dict(color='#2c3e50', width=2)))
    fig_hist.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis_title="Timeline",
        yaxis_title="Net Asset Value (INR)",
        hovermode="x unified",
        template="plotly_white"
    )
    st.plotly_chart(fig_hist, use_container_width=True)

with tab2:
    st.subheader(f"Geometric Brownian Motion Simulation ({sim_runs} Paths)")
    
    # 1. Math Analytics Calculations (Using standard 252 trading days baseline framework)
    fund_df["daily_return"] = fund_df["nav"].pct_change()
    daily_mu = fund_df["daily_return"].mean()
    daily_sigma = fund_df["daily_return"].std()
    
    # Avoid mathematical exceptions on faulty asset entries
    if pd.isna(daily_mu) or daily_sigma == 0:
        daily_mu, daily_sigma = 0.0005, 0.01 
        
    # 5 Year forward planning vector (5 * 252 = 1260 horizon points)
    trading_days_horizon = 5 * 252
    dt = 1
    
    # Drift and Variance parameter tuning formulas
    drift = daily_mu - (0.5 * (daily_sigma ** 2))
    
    # 2. Vectorized Simulation Matrix Building
    shock = np.random.normal(0, 1, (trading_days_horizon, sim_runs))
    exponent = np.exp(drift * dt + daily_sigma * np.sqrt(dt) * shock)
    
    # Stack configurations sequentially and perform cumulative product compounding
    sim_paths = np.zeros_like(exponent)
    sim_paths[0] = latest_nav * exponent[0]
    for t in range(1, trading_days_horizon):
        sim_paths[t] = sim_paths[t-1] * exponent[t]
        
    # 3. Aggregate Probability Distribution Uncertainty Bands
    percentile_10 = np.percentile(sim_paths, 10, axis=1)
    percentile_50 = np.percentile(sim_paths, 50, axis=1)
    percentile_90 = np.percentile(sim_paths, 90, axis=1)
    
    future_dates = pd.date_range(start=fund_df["nav_date"].iloc[-1], periods=trading_days_horizon, freq="B")

    # 4. Interactive Uncertainty Corridor Plot Rendering
    fig_sim = go.Figure()
    fig_sim.add_trace(go.Scatter(x=future_dates, y=percentile_90, mode='lines', line=dict(width=0.5, color='rgba(46, 204, 113, 0.2)'), name='90th Percentile (Optimistic Case)'))
    fig_sim.add_trace(go.Scatter(x=future_dates, y=percentile_50, mode='lines', line=dict(color='#27ae60', width=2), name='50th Percentile (Median Path)'))
    fig_sim.add_trace(go.Scatter(x=future_dates, y=percentile_10, mode='lines', line=dict(width=0.5, color='rgba(231, 76, 60, 0.2)'), fill='tonexty', fillcolor='rgba(46, 204, 113, 0.05)', name='10th Percentile (Pessimistic Case)'))
    
    fig_sim.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis_title="Simulation Projection Timeline",
        yaxis_title="Projected Asset Value (INR)",
        hovermode="x unified",
        template="plotly_white"
    )
    st.plotly_chart(fig_sim, use_container_width=True)
    
    # Dynamic Quantile Summary Box
    st.info(f"🔮 **Simulation Performance Outlook Summary:** In a median statistical scenario (50th percentile), the system predicts {target_fund} scaling from its baseline price of **₹{latest_nav:,.2f}** up to **₹{percentile_50[-1]:,.2f}** over the next 5 years.")