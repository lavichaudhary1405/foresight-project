# Project FORESIGHT — AI-Powered Demand & Inventory Intelligence Platform

An AI-powered demand forecasting and inventory intelligence dashboard. It
forecasts SKU-level demand, flags stockout/overstock risk, and shows
everything on an interactive Streamlit dashboard.

## 1. What's in this folder

```
foresight_project/
├── app.py               # Streamlit dashboard (run this)
├── forecast_utils.py    # Forecasting model + inventory risk logic
├── generate_data.py     # Creates a sample dataset (data/sales_inventory.csv)
├── data/
│   └── sales_inventory.csv
├── requirements.txt
└── README.md
```

## 2. Setup (first time)

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Use YOUR real data instead of the sample data

If Zidio gave you a real dataset (check `Zidio_Project_Data_1.1.pdf` /
any CSV/Excel they shared):

1. Save it as `data/sales_inventory.csv`.
2. Make sure it has (or rename its columns to) exactly:
   - `date` (YYYY-MM-DD)
   - `sku` (product ID)
   - `sales_qty` (units sold that day)
   - `stock_qty` (stock remaining that day)
3. Skip `generate_data.py` — it's only for the sample/demo data.

If the real dataset has different columns, tell me what they are and I'll
adjust `forecast_utils.py` to match.

## 4. Run locally

```bash
streamlit run app.py
```

Opens at http://localhost:8501

## 5. Deploy for free (for the "Live Deployment" submission)

1. Push this folder to a **public GitHub repo**.
2. Go to https://share.streamlit.io → "New app".
3. Connect your GitHub repo, set the main file to `app.py`.
4. Click Deploy. You'll get a public URL like
   `https://your-app-name.streamlit.app` — that's your Live Deployment link.

## 6. What to submit on Zidio

| Deliverable        | What to submit |
|---------------------|-----------------|
| Source Code         | Link to the GitHub repo containing this folder |
| Live Deployment      | The `streamlit.app` URL from step 5 |
| Demo Video          | Screen-record yourself using the dashboard (filters, forecast, alerts) |
| Feedback Video       | Short video: what you learned, challenges, key takeaways |
| Project Report      | Overview + tech stack + screenshots + conclusion (see below) |

## 7. How the model works (for your report / viva)

- **Forecasting**: Linear regression on a day index captures the overall
  trend, plus an average weekday offset captures repeating patterns
  (e.g., weekend demand spikes). This is deliberately simple and explainable
  — good for a viva, since you can describe exactly what it's doing.
- **Risk rules**:
  - `Stockout Risk`: current stock < total forecasted demand over the
    horizon (you'll run out before restocking).
  - `Overstock Risk`: current stock > 2x forecasted demand (too much
    capital tied up in slow-moving stock).
  - `Healthy`: anywhere in between.

You can mention in your report that this could be upgraded to Prophet/ARIMA
for more advanced seasonality handling — but the current model is
dependency-light and runs anywhere.
