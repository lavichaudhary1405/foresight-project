"""
Project FORESIGHT - Forecasting & Inventory Logic
----------------------------------------------------
Simple, dependency-light demand forecasting (linear regression + moving
average on residual seasonality) and stockout/overstock risk rules.

Kept intentionally simple (no Prophet/ARIMA) so it installs and runs
anywhere with just pandas/numpy/scikit-learn.
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


def load_data(path="data/sales_inventory.csv"):
    df = pd.read_csv(path, parse_dates=["date"])
    df = df.sort_values(["sku", "date"]).reset_index(drop=True)
    return df


def forecast_sku(df_sku: pd.DataFrame, periods: int = 30) -> pd.DataFrame:
    """
    Forecast future demand for a single SKU using:
      1) Linear trend (sklearn LinearRegression) on day index
      2) + average weekday seasonal effect (captures weekend bumps etc.)
    Returns a DataFrame with columns: date, forecast_sales
    """
    df_sku = df_sku.copy()
    df_sku["day_idx"] = np.arange(len(df_sku))
    df_sku["weekday"] = df_sku["date"].dt.dayofweek

    # 1) Trend
    X = df_sku[["day_idx"]].values
    y = df_sku["sales_qty"].values
    model = LinearRegression()
    model.fit(X, y)

    # 2) Weekday seasonal offset = avg(actual - trend) per weekday
    trend_pred = model.predict(X)
    residual = y - trend_pred
    df_sku["residual"] = residual
    weekday_offset = df_sku.groupby("weekday")["residual"].mean()

    last_idx = df_sku["day_idx"].max()
    last_date = df_sku["date"].max()
    future_idx = np.arange(last_idx + 1, last_idx + 1 + periods)
    future_dates = pd.date_range(last_date + pd.Timedelta(days=1), periods=periods)

    future_trend = model.predict(future_idx.reshape(-1, 1))
    future_weekday = future_dates.dayofweek.map(weekday_offset).fillna(0).values

    forecast_vals = np.clip(future_trend + future_weekday, a_min=0, a_max=None)

    return pd.DataFrame(
        {"date": future_dates, "sku": df_sku["sku"].iloc[0], "forecast_sales": forecast_vals}
    )


def forecast_all(df: pd.DataFrame, periods: int = 30) -> pd.DataFrame:
    """Run forecast_sku for every SKU in the dataset and concatenate results."""
    parts = []
    for sku, grp in df.groupby("sku"):
        parts.append(forecast_sku(grp, periods=periods))
    return pd.concat(parts, ignore_index=True)


def inventory_risk(df: pd.DataFrame, forecast_df: pd.DataFrame, horizon: int = 30) -> pd.DataFrame:
    """
    Compare each SKU's current stock vs. its predicted demand over the
    forecast horizon, and flag risk:
      - Stockout Risk: current stock < forecasted demand for horizon
      - Overstock Risk: current stock > 2x forecasted demand for horizon
      - Healthy: otherwise
    """
    latest_stock = (
        df.sort_values("date").groupby("sku")["stock_qty"].last().rename("current_stock")
    )
    future_demand = forecast_df.groupby("sku")["forecast_sales"].sum().rename("predicted_demand")

    result = pd.concat([latest_stock, future_demand], axis=1).reset_index()
    result["predicted_demand"] = result["predicted_demand"].round(0)

    def classify(row):
        if row["current_stock"] < row["predicted_demand"]:
            return "⚠️ Stockout Risk"
        elif row["current_stock"] > 2 * row["predicted_demand"]:
            return "📦 Overstock Risk"
        else:
            return "✅ Healthy"

    result["risk_status"] = result.apply(classify, axis=1)
    result["horizon_days"] = horizon
    return result
