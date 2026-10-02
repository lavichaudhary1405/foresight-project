"""
Project FORESIGHT - AI-Powered Demand & Inventory Intelligence Platform
--------------------------------------------------------------------------
Streamlit dashboard: sales trends, SKU-level demand forecast, and
stockout/overstock risk alerts.

Run locally:
    streamlit run app.py

Deploy free:
    1. Push this folder to a GitHub repo.
    2. Go to https://share.streamlit.io -> "New app" -> connect the repo.
    3. Set main file path to app.py -> Deploy.
"""

import pandas as pd
import streamlit as st

from forecast_utils import load_data, forecast_all, inventory_risk

st.set_page_config(page_title="Project FORESIGHT", layout="wide")

st.title("📈 Project FORESIGHT")
st.caption("AI-Powered Demand Forecasting & Inventory Intelligence Platform")

# ---------------------------------------------------------------------
# Sidebar controls
# ---------------------------------------------------------------------
st.sidebar.header("Controls")

df = load_data()
all_skus = sorted(df["sku"].unique())
selected_skus = st.sidebar.multiselect("Select SKU(s)", all_skus, default=all_skus[:3])
horizon = st.sidebar.slider("Forecast horizon (days)", min_value=7, max_value=90, value=30, step=7)

if not selected_skus:
    st.warning("Select at least one SKU from the sidebar to see charts.")
    st.stop()

filtered_df = df[df["sku"].isin(selected_skus)]

# ---------------------------------------------------------------------
# Forecast + risk (computed on ALL skus so the alert table is complete)
# ---------------------------------------------------------------------
with st.spinner("Running forecast model..."):
    forecast_df = forecast_all(df, periods=horizon)
    risk_df = inventory_risk(df, forecast_df, horizon=horizon)

# ---------------------------------------------------------------------
# Top KPIs
# ---------------------------------------------------------------------
col1, col2, col3 = st.columns(3)
col1.metric("Total SKUs", len(all_skus))
col2.metric("Stockout Risk SKUs", int((risk_df["risk_status"] == "⚠️ Stockout Risk").sum()))
col3.metric("Overstock Risk SKUs", int((risk_df["risk_status"] == "📦 Overstock Risk").sum()))

st.divider()

# ---------------------------------------------------------------------
# Sales trend chart
# ---------------------------------------------------------------------
st.subheader("Historical Sales Trend")
pivot_sales = filtered_df.pivot(index="date", columns="sku", values="sales_qty")
st.line_chart(pivot_sales)

# ---------------------------------------------------------------------
# Forecast chart
# ---------------------------------------------------------------------
st.subheader(f"Demand Forecast — next {horizon} days")
fc_filtered = forecast_df[forecast_df["sku"].isin(selected_skus)]
pivot_fc = fc_filtered.pivot(index="date", columns="sku", values="forecast_sales")
st.line_chart(pivot_fc)

# ---------------------------------------------------------------------
# Inventory risk table
# ---------------------------------------------------------------------
st.subheader("Inventory Risk Alerts")
st.dataframe(
    risk_df[risk_df["sku"].isin(selected_skus)].reset_index(drop=True),
    use_container_width=True,
)

st.caption(
    "Stockout Risk = current stock < predicted demand for the horizon. "
    "Overstock Risk = current stock > 2x predicted demand."
)

# ---------------------------------------------------------------------
# Raw data (optional expandable)
# ---------------------------------------------------------------------
with st.expander("View raw data"):
    st.dataframe(filtered_df.reset_index(drop=True), use_container_width=True)
