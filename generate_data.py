"""
Project FORESIGHT - Sample Data Generator
-------------------------------------------
Generates a synthetic demand & inventory dataset (data/sales_inventory.csv)
so the forecasting model and dashboard have something to run on.

IMPORTANT: If Zidio gave you a real dataset (Zidio_Project_Data_1.1.pdf or a
CSV/Excel file), use that instead — just make sure the columns are named:
    date, sku, sales_qty, stock_qty
(or update COLUMN NAMES in app.py to match your real file).

Run:
    python generate_data.py
"""

import numpy as np
import pandas as pd

np.random.seed(42)

N_DAYS = 365
N_SKUS = 8
start_date = pd.Timestamp("2025-01-01")
dates = pd.date_range(start_date, periods=N_DAYS, freq="D")

skus = [f"SKU-{i:03d}" for i in range(1, N_SKUS + 1)]

rows = []
for sku in skus:
    base_demand = np.random.randint(20, 100)
    trend = np.random.uniform(-0.02, 0.05)
    seasonality_amp = np.random.uniform(5, 25)
    stock = np.random.randint(500, 1500)

    for i, d in enumerate(dates):
        seasonal = seasonality_amp * np.sin(2 * np.pi * i / 30)
        weekly = 10 if d.dayofweek in (5, 6) else 0  # weekend bump
        noise = np.random.normal(0, 8)
        demand = max(0, base_demand + trend * i + seasonal + weekly + noise)
        demand = int(round(demand))

        stock -= demand
        # periodic restock
        if stock < base_demand * 5:
            restock = np.random.randint(200, 600)
            stock += restock
        stock = max(stock, 0)

        rows.append(
            {
                "date": d,
                "sku": sku,
                "sales_qty": demand,
                "stock_qty": stock,
            }
        )

df = pd.DataFrame(rows)
df.to_csv("data/sales_inventory.csv", index=False)
print(f"Saved data/sales_inventory.csv with {len(df)} rows, {N_SKUS} SKUs.")
print(df.head())
