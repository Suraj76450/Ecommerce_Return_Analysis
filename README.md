# E-Commerce Return & Refund Analysis: Root Causes & Business Optimization

This is a production-ready, end-to-end data science and business analytics project designed to diagnose why customers return products in e-commerce, measure the true financial impact, and provide automated predictive mitigations to reduce return rates and optimize store profitability.

---

## 🌟 Project Highlights

1. **Interactive Obsidian Dark Dashboard**: Re-engineered with a sleek, premium dark-mode design, sidebar routing, and hardware-accelerated **Plotly Express** interactive vector charts. Users can hover, zoom, and toggle legend metrics in real-time under a sub-100ms execution frame.
2. **Upgraded Machine Learning Pipeline**: Built using Scikit-Learn's state-of-the-art **`HistGradientBoostingClassifier`** (gradient-boosted trees). Incorporating engineered features like `Delivery Delay` (expected vs. actual shipping days) and `Is Delayed` boosted model accuracy to **72.12%** and ROC-AUC to **0.7366**.
3. **⚙️ Data Pipeline Admin Control Center**: An administrative portal integrated directly into the web UI, allowing users to synthesize raw transactions, execute sanitization pipelines, and retrain ML predictors with a single click.
4. **Bracketing & Cohort Diagnostics**: Detects customer bracketing behavior (buying multiple sizes/styles of a single item to return the rest) and isolates high-risk serial returners.
5. **Reverse Logistics Cost Modeling**: Quantifies net financial loss by factoring in flat shipping and restocking fees on top of raw refund totals.
6. **Star Schema Power BI Blueprint**: Detailed blueprint specifying schema relationships, DAX formulas, and visual hierarchies for BI deployment.

---

## 📁 Project Structure

```text
Ecommerce_Return_Analysis/
│
├── data/
│   ├── raw_data.csv               # Synthesized raw data (50,000+ orders with anomalies)
│   ├── cleaned_data.csv           # Cleaned transaction data with engineered features
│   ├── chronic_returners.csv      # Customer segment flagged for excessive returns
│   └── return_prediction_pipeline.pkl # Serialized HistGradientBoosting model pipeline
│
├── notebooks/
│   ├── 01_data_cleaning.ipynb      # Loading, profiling, and sanitizing raw transactions
│   ├── 02_eda.ipynb                # Univariate, bivariate, multivariate & bracketing cohort charts
│   ├── 03_business_analysis.ipynb  # Business questions breakdown and hypothesis testing
│   └── 04_returns_prediction.ipynb # Preprocessing, model training (LR/RF) and evaluations
│
├── dashboard/
│   ├── app.py                     # Streamlit Interactive Web Application
│   └── power_bi_blueprint.md      # Star schema & DAX blueprint for Power BI dashboarding
│
├── reports/
│   └── Final_Report.md            # Comprehensive executive report & business recommendations
│
├── scripts/
│   ├── generate_data.py           # Python data synthesis generator
│   └── build_notebooks.py         # Programmatic notebook compiler from source code
│
├── images/                        # Exported analysis charts
├── README.md                      # Project homepage
└── requirements.txt               # Project dependencies
```

---

## 🚀 Setup & Execution Guide

### 1. Clone & Set Up Workspace
Navigate to the directory and install dependencies:
```bash
git clone https://github.com/Suraj76450/Ecommerce_Return_Analysis.git
cd Ecommerce_Return_Analysis
pip install -r requirements.txt
```

### 2. Launch the Interactive Dashboard
To launch the Streamlit app:
```bash
python -m streamlit run dashboard/app.py
```
This will start the local server and open the web dashboard at **http://localhost:8501**.

---

## ⚙️ Data Pipeline Control Center
The dashboard features an integrated **Data Pipeline Control Panel** where you can trigger backend updates from the UI:
1. **Synthesize**: Slide the input to generate up to $100,000$ raw orders with anomalies and duplicates.
2. **Clean**: Executes Pandas deduplication, currency string cleaning, date standardizations, and imputes missing ratings.
3. **Train**: Splits data, fits the `ColumnTransformer` (scaling numericals and one-hot encoding categoricals), trains the **HistGradientBoosting** model, prints logs, and updates the local serialized pipeline.

---

## 🌍 Real-Life Production Deployment Blueprint

This project is built modularly so that it can be connected directly to a live e-commerce store (e.g. Shopify, WooCommerce, Magento) and run in production.

### Step 1: Connecting to Real Data
To transition to real-life transactions, query your live relational database (e.g. PostgreSQL, BigQuery, Snowflake) and overwrite the raw target file:
```python
import pandas as pd
import psycopg2

conn = psycopg2.connect("dbname=shopify_store user=admin password=secret host=db.mycompany.com")
df_real = pd.read_sql_query("SELECT * FROM orders_and_shipments", conn)
df_real.to_csv("data/raw_data.csv", index=False)
```

### Step 2: Deploying the ML Model as a Live REST API
You can run the trained model pipeline (`return_prediction_pipeline.pkl`) inside a lightweight **FastAPI** web server to serve real-time predictions to your website's checkout page.

#### API Script (`api.py`):
```python
import pickle
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="E-Commerce Return Risk Predictor")

# Load model pipeline
with open("data/return_prediction_pipeline.pkl", "rb") as f:
    model = pickle.load(f)

class CheckoutCart(BaseModel):
    Category: str
    Brand: str
    Shipping_Type: str
    Seller: str
    Segment: str
    Gender: str
    Price: float
    Quantity: int
    Discount: float
    Delivery_Days: int
    Customer_Age: int

@app.post("/predict-return")
def predict_return(cart: CheckoutCart):
    # Process delay metrics
    expected = {"Overnight": 1, "Express": 2, "Standard": 5}[cart.Shipping_Type]
    delay = max(0, cart.Delivery_Days - expected)
    is_delayed = 1 if delay > 0 else 0
    
    # Format input to match training schema
    input_data = pd.DataFrame([{
        "Category": cart.Category, "Brand": cart.Brand, "Shipping Type": cart.Shipping_Type,
        "Seller": cart.Seller, "Segment": cart.Segment, "Gender": cart.Gender,
        "Price": cart.Price, "Quantity": cart.Quantity, "Discount": cart.Discount,
        "Delivery Days": cart.Delivery_Days, "Delivery Delay": delay,
        "Is Delayed": is_delayed, "Customer Age": cart.Customer_Age
    }])
    
    # Run prediction
    probability = model.predict_proba(input_data)[0][1]
    return {"return_probability": float(probability)}
```

### Step 3: Triggering Automated Store Interventions
Once your checkout frontend receives the return probability from the API, it applies real-time preventative measures:
* **High Risk (> 50%)**:
  * Prompt the user to double-check their sizing with a dynamic size guide.
  * Disable Cash on Delivery (COD) to prevent high-risk Return-To-Origin (RTO) cash drain.
* **Medium Risk (25% - 50%)**:
  * Offer a free shipping upgrade to Express (since shipping delay is the single strongest statistical driver of returns).
* **Bracketing Customers**:
  * Block checkout if a customer adds 3 sizes of the same apparel item (e.g. Medium, Large, XL of the same shirt) to nudge them toward fitting support.

---

## 🛠️ Technology Stack
* **Web UI**: Streamlit (Python App Framework), Plotly Express (Browser charts)
* **ML Engines**: Scikit-Learn (HistGradientBoosting, column preprocessors)
* **Data Core**: Pandas, NumPy, SciPy (Statistical T-Tests, ANOVA, Chi-Square validation)
* **Infrastructure**: Git, FastAPI (Deployment framework)
