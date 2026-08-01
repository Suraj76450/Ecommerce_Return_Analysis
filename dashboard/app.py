import os
import pickle
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Set page config
st.set_page_config(
    page_title="E-Commerce Return & Refund Analyst",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Obsidian Dark Mode & Glassmorphic layout
st.markdown("""
<style>
    /* Import modern Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&display=swap');
    
    /* Apply globally */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        font-family: 'Outfit', sans-serif;
        background-color: #0B0F19 !important;
        color: #F8FAFC !important;
    }
    
    /* Sidebar Styling override */
    [data-testid="stSidebar"] {
        background-color: #0F172A !important;
        border-right: 1px solid #1E293B !important;
    }
    
    /* Sidebar text colors */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] span {
        color: #F1F5F9 !important;
    }
    
    /* Main Heading Gradient */
    .main-title {
        font-family: 'Outfit', sans-serif;
        font-size: 44px;
        font-weight: 800;
        background: linear-gradient(90deg, #60A5FA 0%, #3B82F6 50%, #8B5CF6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2px;
        letter-spacing: -0.02em;
    }
    .sub-title {
        font-family: 'Outfit', sans-serif;
        font-size: 16px;
        color: #94A3B8;
        margin-bottom: 30px;
        font-weight: 400;
    }
    
    /* Obsidian Glassmorphic Metric Cards */
    .metric-card {
        background: rgba(30, 41, 59, 0.45);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 22px;
        backdrop-filter: blur(10px);
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 15px;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        border-color: rgba(96, 165, 250, 0.35);
        box-shadow: 0 15px 40px -15px rgba(59, 130, 246, 0.3);
    }
    .metric-title {
        font-size: 12px;
        color: #94A3B8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 34px;
        font-weight: 800;
        color: #FFFFFF;
        letter-spacing: -0.01em;
    }
    .metric-delta {
        font-size: 12px;
        color: #F87171;
        font-weight: 500;
        margin-top: 4px;
    }
    .metric-delta-green {
        font-size: 12px;
        color: #34D399;
        font-weight: 500;
        margin-top: 4px;
    }
    
    /* Custom divider line */
    hr {
        border: 0;
        height: 1px;
        background: linear-gradient(90deg, rgba(255,255,255,0.01), rgba(255,255,255,0.08) 50%, rgba(255,255,255,0.01));
        margin: 25px 0;
    }
    
    /* Card wrapper for charts */
    .chart-container {
        background: rgba(15, 23, 42, 0.45);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    }
    
    /* Sidebar styling overrides for radio buttons */
    div[data-testid="stSidebarUserContent"] div.stRadio > label {
        color: #94A3B8 !important;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 11px;
        letter-spacing: 0.05em;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to find workspace data
def get_path(filename):
    paths = [filename, f"data/{filename}", f"../data/{filename}", f"../{filename}"]
    for p in paths:
        if os.path.exists(p):
            return os.path.abspath(p)
    os.makedirs("data", exist_ok=True)
    return os.path.abspath(os.path.join("data", filename))

# --- DATA PIPELINE BACKEND FUNCTIONS ---

def run_data_generation_backend(num_orders, progress_bar):
    import random
    from datetime import datetime
    random.seed(42)
    np.random.seed(42)
    
    progress_bar.progress(10, "Initializing product catalogs...")
    products = {
        "Electronics": [
            {"name": "iPhone 15 Pro", "brand": "Apple", "price": 999.00},
            {"name": "iPad Air", "brand": "Apple", "price": 599.00},
            {"name": "Galaxy S23 Ultra", "brand": "Samsung", "price": 1199.00},
            {"name": "Galaxy Buds Pro", "brand": "Samsung", "price": 199.00},
            {"name": "Sony WH-1000XM5", "brand": "Sony", "price": 399.00},
            {"name": "Dell XPS 13", "brand": "Dell", "price": 1299.00}
        ],
        "Clothing": [
            {"name": "Running Shoes", "brand": "Nike", "price": 130.00},
            {"name": "Windbreaker Jacket", "brand": "Nike", "price": 85.00},
            {"name": "Ultraboost Sneakers", "brand": "Adidas", "price": 190.00},
            {"name": "Classic 501 Jeans", "brand": "Levi's", "price": 79.50},
            {"name": "Denim Jacket", "brand": "Levi's", "price": 98.00},
            {"name": "Summer Floral Dress", "brand": "Zara", "price": 59.90},
            {"name": "Slim Fit Chinos", "brand": "Zara", "price": 49.90}
        ],
        "Home & Kitchen": [
            {"name": "Instant Pot Duo 7-in-1", "brand": "Instant Pot", "price": 99.95},
            {"name": "K-Classic Coffee Maker", "brand": "Keurig", "price": 89.00},
            {"name": "Air Fryer XL", "brand": "Ninja", "price": 159.99},
            {"name": "Blender Professional", "brand": "Ninja", "price": 120.00},
            {"name": "Robot Vacuum Cleaner", "brand": "iRobot", "price": 299.00}
        ],
        "Beauty": [
            {"name": "Regenerist Moisturizer", "brand": "Olay", "price": 28.50},
            {"name": "Advanced Night Repair", "brand": "Estee Lauder", "price": 115.00},
            {"name": "Matte Lipstick", "brand": "MAC", "price": 23.00},
            {"name": "Supersonic Hair Dryer", "brand": "Dyson", "price": 429.99}
        ],
        "Books": [
            {"name": "Harry Potter Box Set", "brand": "Scholastic", "price": 85.00},
            {"name": "Atomic Habits", "brand": "Penguin", "price": 16.20},
            {"name": "Thinking, Fast and Slow", "brand": "Farrar", "price": 18.00},
            {"name": "The Alchemist", "brand": "HarperOne", "price": 15.00}
        ],
        "Sports": [
            {"name": "Premium Yoga Mat", "brand": "Gaiam", "price": 29.98},
            {"name": "NBA Replica Basketball", "brand": "Spalding", "price": 34.99},
            {"name": "Adjustable Dumbbell Set", "brand": "Bowflex", "price": 399.00},
            {"name": "Waterproof Camping Tent", "brand": "Coleman", "price": 149.99}
        ]
    }

    progress_bar.progress(25, "Generating customer profiles...")
    customer_ids = [f"CUST-{random.randint(1000, 9999)}" for _ in range(int(num_orders * 0.16))]
    order_ids = [f"ORD-{i:06d}" for i in range(100001, 100001 + num_orders)]

    customer_profiles = {}
    for cust_id in customer_ids:
        age = random.randint(18, 70)
        gender = np.random.choice(["Male", "Female", "Other"], p=[0.48, 0.49, 0.03])
        segment = np.random.choice(["Consumer", "Corporate", "Home Office"], p=[0.60, 0.25, 0.15])
        customer_profiles[cust_id] = {"Age": age, "Gender": gender, "Segment": segment}

    geo_data = {
        "California": ["Los Angeles", "San Francisco", "San Diego", "San Jose"],
        "Texas": ["Houston", "Austin", "Dallas", "San Antonio"],
        "New York": ["New York City", "Buffalo", "Rochester", "Albany"],
        "Florida": ["Miami", "Orlando", "Tampa", "Jacksonville"],
        "Illinois": ["Chicago", "Springfield", "Naperville", "Rockford"],
        "Pennsylvania": ["Philadelphia", "Pittsburgh", "Allentown", "Erie"],
        "Ohio": ["Columbus", "Cleveland", "Cincinnati", "Toledo"],
        "Georgia": ["Atlanta", "Savannah", "Augusta", "Athens"],
        "North Carolina": ["Charlotte", "Raleigh", "Greensboro", "Durham"],
        "Michigan": ["Detroit", "Grand Rapids", "Lansing", "Ann Arbor"]
    }
    states = list(geo_data.keys())
    sellers = ["Seller A (Global Retail)", "Seller B (Direct Electronics)", "Seller C (Fashion Hub)", "Seller D (Home Goods Co)", "Seller E (Budget Imports)"]
    warehouses = ["Warehouse North", "Warehouse South", "Warehouse East", "Warehouse West"]

    data = []
    start_date = pd.Timestamp("2024-01-01")

    progress_bar.progress(45, "Synthesizing transaction logs...")
    for i in range(num_orders):
        order_id = order_ids[i]
        customer_id = random.choice(customer_ids)
        profile = customer_profiles[customer_id]
        
        days_offset = random.randint(0, 729)
        order_datetime = start_date + pd.Timedelta(days=days_offset)
        
        category = random.choice(list(products.keys()))
        prod_info = random.choice(products[category])
        product_name = prod_info["name"]
        brand = prod_info["brand"]
        base_price = prod_info["price"]
        
        quantity = np.random.choice([1, 2, 3, 4, 5], p=[0.75, 0.15, 0.06, 0.03, 0.01])
        discount = np.random.choice([0.0, 0.1, 0.2, 0.3, 0.4, 0.5], p=[0.50, 0.20, 0.15, 0.08, 0.05, 0.02])
        total_amount = round((base_price * quantity) * (1 - discount), 2)
        
        state = random.choice(states)
        city = random.choice(geo_data[state])
        
        shipping_type = np.random.choice(["Standard", "Express", "Overnight"], p=[0.70, 0.22, 0.08])
        if shipping_type == "Standard":
            expected_days = 5
            delivery_days = random.randint(8, 15) if random.random() < 0.10 else random.randint(3, 7)
        elif shipping_type == "Express":
            expected_days = 2
            delivery_days = random.randint(4, 7) if random.random() < 0.05 else random.randint(1, 3)
        else:
            expected_days = 1
            delivery_days = random.randint(2, 4) if random.random() < 0.03 else 1
            
        if category == "Clothing" and random.random() < 0.70:
            seller = "Seller C (Fashion Hub)"
        elif category == "Electronics" and random.random() < 0.70:
            seller = "Seller B (Direct Electronics)"
        else:
            seller = random.choice(sellers)
        warehouse = random.choice(warehouses)
        
        rating_probs = [0.05, 0.05, 0.15, 0.30, 0.45]
        if delivery_days > expected_days:
            rating_probs = [0.25, 0.25, 0.25, 0.15, 0.10]
        if seller == "Seller E (Budget Imports)":
            rating_probs = [0.15, 0.20, 0.25, 0.25, 0.15]
        customer_rating = np.random.choice([1, 2, 3, 4, 5], p=rating_probs)
        
        return_prob = 0.05
        if category == "Clothing":
            return_prob += 0.15
        elif category == "Electronics":
            return_prob += 0.08
        elif category == "Books":
            return_prob -= 0.03
            
        if delivery_days > expected_days:
            return_prob += 0.12
        if discount >= 0.40:
            return_prob += 0.10
        if customer_rating == 1:
            return_prob += 0.60
        elif customer_rating == 2:
            return_prob += 0.35
        elif customer_rating == 3:
            return_prob += 0.15
        elif customer_rating == 4:
            return_prob -= 0.02
        else:
            return_prob -= 0.04
            
        if seller == "Seller E (Budget Imports)":
            return_prob += 0.08
        return_prob = max(0.01, min(0.95, return_prob))
        
        if random.random() < return_prob:
            return_status = "Returned"
            reasons = ["Changed Mind", "Wrong Size", "Damaged", "Defective", "Not as Described", "Late Delivery"]
            weights = [0.2, 0.2, 0.15, 0.15, 0.2, 0.1]
            if category == "Clothing":
                reasons = ["Wrong Size", "Not as Described", "Changed Mind", "Damaged", "Defective", "Late Delivery"]
                weights = [0.55, 0.15, 0.15, 0.05, 0.05, 0.05]
            elif delivery_days > expected_days and random.random() < 0.60:
                reasons = ["Late Delivery", "Changed Mind", "Not as Described", "Damaged", "Defective", "Wrong Size"]
                weights = [0.60, 0.15, 0.10, 0.05, 0.05, 0.05]
            elif customer_rating in [1, 2]:
                reasons = ["Defective", "Damaged", "Not as Described", "Changed Mind", "Wrong Size", "Late Delivery"]
                weights = [0.40, 0.30, 0.20, 0.05, 0.03, 0.02]
            return_reason = np.random.choice(reasons, p=weights)
            refund_amount = total_amount
        else:
            return_status = "Not Returned"
            return_reason = None
            refund_amount = 0.0

        data.append({
            "Order ID": order_id, "Customer ID": customer_id, "Customer Age": profile["Age"],
            "Gender": profile["Gender"], "Segment": profile["Segment"], "Order Date": order_datetime,
            "Product Name": product_name, "Category": category, "Brand": brand, "Quantity": quantity,
            "Price": base_price, "Discount": discount, "Total Amount": total_amount, "State": state,
            "City": city, "Seller": seller, "Delivery Days": delivery_days, "Shipping Type": shipping_type,
            "Return Status": return_status, "Return Reason": return_reason, "Refund Amount": refund_amount,
            "Customer Rating": customer_rating, "Warehouse": warehouse
        })

    df_gen = pd.DataFrame(data)
    
    # Bracketing simulation
    progress_bar.progress(70, "Simulating buyer sizing behaviors (Bracketing)...")
    bracketing_customers = list(set(df_gen["Customer ID"].sample(min(500, int(num_orders*0.05)), random_state=42)))
    bracketing_rows = []
    for cust in bracketing_customers:
        cust_rows = df_gen[df_gen["Customer ID"] == cust]
        if len(cust_rows) == 0:
            continue
        base_row = cust_rows.iloc[0].copy()
        if base_row["Category"] == "Clothing":
            for suffix in ["-B1", "-B2"]:
                new_row = base_row.copy()
                new_row["Order ID"] = base_row["Order ID"] + suffix
                new_row["Quantity"] = 1
                new_row["Total Amount"] = round(new_row["Price"] * (1 - new_row["Discount"]), 2)
                new_row["Return Status"] = "Returned"
                new_row["Return Reason"] = "Wrong Size"
                new_row["Refund Amount"] = new_row["Total Amount"]
                new_row["Customer Rating"] = 4
                bracketing_rows.append(new_row)
    if bracketing_rows:
        df_gen = pd.concat([df_gen, pd.DataFrame(bracketing_rows)], ignore_index=True)

    progress_bar.progress(85, "Injecting duplicates and dirty records...")
    dup_indices = np.random.choice(df_gen.index, size=int(len(df_gen) * 0.015), replace=False)
    df_gen = pd.concat([df_gen, df_gen.loc[dup_indices].copy()], ignore_index=True)
    df_gen.loc[np.random.choice(df_gen.index, size=int(len(df_gen) * 0.025), replace=False), "Customer Rating"] = np.nan
    df_gen.loc[np.random.choice(df_gen.index, size=int(len(df_gen) * 0.01), replace=False), "Shipping Type"] = np.nan
    ret_indices = df_gen[df_gen["Return Status"] == "Returned"].index
    df_gen.loc[np.random.choice(ret_indices, size=int(len(ret_indices) * 0.015), replace=False), "Return Reason"] = np.nan
    geo_nulls = np.random.choice(df_gen.index, size=int(len(df_gen) * 0.005), replace=False)
    df_gen.loc[geo_nulls, "State"] = np.nan
    df_gen.loc[geo_nulls, "City"] = np.nan
    
    df_gen["Price"] = df_gen["Price"].astype(object)
    df_gen.loc[np.random.choice(df_gen.index, size=int(len(df_gen) * 0.04), replace=False), "Price"] = \
        df_gen.loc[np.random.choice(df_gen.index, size=int(len(df_gen) * 0.04), replace=False), "Price"].apply(lambda x: f"${x:,.2f}" if isinstance(x, (int, float)) else x)
    
    df_gen["Order Date"] = df_gen["Order Date"].apply(lambda d: d.strftime("%m/%d/%Y") if random.random() < 0.3 else d.strftime("%Y-%m-%d"))
    
    df_gen.loc[np.random.choice(df_gen.index, size=20, replace=False), "Price"] = -49.90
    df_gen.loc[np.random.choice(df_gen.index, size=15, replace=False), "Quantity"] = 0
    df_gen.loc[np.random.choice(df_gen.index, size=25, replace=False), "Delivery Days"] = -3
    
    progress_bar.progress(95, "Writing raw_data.csv to disk...")
    raw_path = get_path("raw_data.csv")
    df_gen.to_csv(raw_path, index=False)
    progress_bar.progress(100, "Done!")
    return len(df_gen), raw_path


def run_data_cleaning_backend(progress_bar):
    log = []
    log.append("🧼 Starting cleaning pipeline...")
    
    raw_path = get_path("raw_data.csv")
    if not os.path.exists(raw_path):
        raise FileNotFoundError("Raw data file does not exist. Please run generation first.")
        
    df_clean = pd.read_csv(raw_path)
    log.append(f"Loaded raw data: {df_clean.shape[0]} rows, {df_clean.shape[1]} columns")
    progress_bar.progress(20, "Deduplicating rows...")
    
    init_len = len(df_clean)
    df_clean = df_clean.drop_duplicates()
    log.append(f"Removed {init_len - len(df_clean)} duplicate records.")
    
    progress_bar.progress(40, "Sanitizing numerical fields...")
    df_clean["Price"] = df_clean["Price"].astype(str).str.replace("$", "", regex=False).str.replace(",", "", regex=False)
    df_clean["Price"] = pd.to_numeric(df_clean["Price"], errors="coerce")
    df_clean["Price"] = df_clean["Price"].abs()
    df_clean["Price"] = df_clean["Price"].fillna(df_clean.groupby("Product Name")["Price"].transform("median"))
    
    df_clean.loc[df_clean["Quantity"] <= 0, "Quantity"] = 1
    df_clean["Delivery Days"] = df_clean["Delivery Days"].abs()
    df_clean["Delivery Days"] = df_clean["Delivery Days"].fillna(df_clean["Delivery Days"].median()).astype(int)
    log.append("Standardized Price, Quantity, and Delivery Days columns.")
    
    progress_bar.progress(60, "Imputing missing fields...")
    df_clean["Order Date"] = pd.to_datetime(df_clean["Order Date"], format="mixed", errors="coerce")
    df_clean = df_clean.dropna(subset=["Order Date"])
    
    df_clean["Customer Rating"] = df_clean["Customer Rating"].fillna(df_clean.groupby("Category")["Customer Rating"].transform("median"))
    shipping_mode = df_clean["Shipping Type"].mode()[0]
    df_clean["Shipping Type"] = df_clean["Shipping Type"].fillna(shipping_mode)
    df_clean["State"] = df_clean["State"].fillna("Unknown State")
    df_clean["City"] = df_clean["City"].fillna("Unknown City")
    log.append("Imputed ratings, shipping methods, and empty geolocation tags.")
    
    progress_bar.progress(85, "Engineering dynamic features...")
    df_clean.loc[(df_clean["Return Status"] == "Returned") & (df_clean["Return Reason"].isna()), "Return Reason"] = "Not Specified"
    df_clean.loc[df_clean["Return Status"] == "Not Returned", "Return Reason"] = np.nan
    df_clean.loc[df_clean["Return Status"] == "Not Returned", "Refund Amount"] = 0.0
    df_clean["Total Amount"] = (df_clean["Price"] * df_clean["Quantity"] * (1 - df_clean["Discount"])).round(2)
    returned_mask = df_clean["Return Status"] == "Returned"
    df_clean.loc[returned_mask, "Refund Amount"] = df_clean.loc[returned_mask, "Total Amount"]
    
    df_clean["Return Indicator"] = (df_clean["Return Status"] == "Returned").astype(int)
    shipping_expected = {"Overnight": 1, "Express": 2, "Standard": 5}
    expected_days = df_clean["Shipping Type"].map(shipping_expected)
    df_clean["Delivery Delay"] = (df_clean["Delivery Days"] - expected_days).clip(lower=0)
    df_clean["Discount Percentage"] = df_clean["Discount"] * 100
    df_clean["Order Month"] = df_clean["Order Date"].dt.month
    df_clean["Order Year"] = df_clean["Order Date"].dt.year
    df_clean["Weekday"] = df_clean["Order Date"].dt.day_name()
    df_clean["Month-Year"] = df_clean["Order Date"].dt.to_period("M").astype(str)
    
    df_clean["Reverse Logistics Cost"] = np.where(df_clean["Return Status"] == "Returned", 5.00 + (0.10 * df_clean["Total Amount"]), 0.00)
    df_clean["Net Financial Impact"] = np.where(df_clean["Return Status"] == "Returned", -df_clean["Reverse Logistics Cost"], df_clean["Total Amount"])
    df_clean["Profit Loss"] = np.where(df_clean["Return Status"] == "Returned", df_clean["Refund Amount"] + df_clean["Reverse Logistics Cost"], 0.00)
    
    customer_stats = df_clean.groupby("Customer ID").agg(
        Total_Orders=("Order ID", "count"),
        Returned_Orders=("Return Indicator", "sum"),
        Return_Rate=("Return Indicator", "mean")
    ).reset_index()
    chronic = customer_stats[(customer_stats["Total_Orders"] >= 3) & (customer_stats["Return_Rate"] > 0.50)]
    
    clean_path = get_path("cleaned_data.csv")
    chronic_path = get_path("chronic_returners.csv")
    df_clean.to_csv(clean_path, index=False)
    chronic.to_csv(chronic_path, index=False)
    
    log.append(f"Successfully exported cleaned data: {df_clean.shape[0]} rows to cleaned_data.csv")
    log.append(f"Flagged {len(chronic)} chronic returners in chronic_returners.csv")
    
    progress_bar.progress(100, "Done!")
    return "\n".join(log)


def run_model_training_backend(progress_bar):
    log = []
    log.append("🧠 Loading clean datasets...")
    clean_path = get_path("cleaned_data.csv")
    df_ml = pd.read_csv(clean_path)
    progress_bar.progress(20, "Splitting train/test split...")
    
    features = [
        "Category", "Brand", "Shipping Type", "Seller", "Segment", "Gender",
        "Price", "Quantity", "Discount", "Delivery Days", "Customer Age"
    ]
    target = "Return Indicator"
    X = df_ml[features]
    y = df_ml[target]
    
    num_features = ["Price", "Quantity", "Discount", "Delivery Days", "Customer Age"]
    cat_features = ["Category", "Brand", "Shipping Type", "Seller", "Segment", "Gender"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)
    
    progress_bar.progress(40, "Building model preprocessors...")
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), num_features),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_features)
        ]
    )
    
    progress_bar.progress(60, "Training Random Forest Pipeline...")
    rf_pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1))
        ]
    )
    rf_pipeline.fit(X_train, y_train)
    
    progress_bar.progress(80, "Evaluating model scoring...")
    y_pred = rf_pipeline.predict(X_test)
    y_prob = rf_pipeline.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_prob)
    acc = (y_pred == y_test).mean()
    
    log.append("Random Forest training completed.")
    log.append(f"Model Accuracy: {acc*100:.2f}%")
    log.append(f"Model ROC-AUC Score: {auc:.4f}")
    
    progress_bar.progress(95, "Serializing ML pipeline pkl...")
    model_path = "dashboard/return_prediction_pipeline.pkl" if os.path.exists("dashboard") else "return_prediction_pipeline.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(rf_pipeline, f)
        
    log.append(f"Model successfully saved to {os.path.abspath(model_path)}!")
    progress_bar.progress(100, "Done!")
    return "\n".join(log)

# --- WEB APPLICATION RENDERING LAYOUT ---

# Load Datasets (Cached)
@st.cache_data
def load_data():
    df = pd.read_csv(get_path("cleaned_data.csv"))
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    
    chronic_path = get_path("chronic_returners.csv")
    chronic_df = pd.read_csv(chronic_path) if os.path.exists(chronic_path) else pd.DataFrame()
    return df, chronic_df

# Check if clean data exists to render visual layouts
clean_data_exists = os.path.exists(get_path("cleaned_data.csv"))
if clean_data_exists:
    df, chronic_df = load_data()
else:
    df, chronic_df = pd.DataFrame(), pd.DataFrame()

# 1. Sidebar Navigation Configuration
st.sidebar.image("https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?auto=format&fit=crop&q=80&w=200", use_container_width=True)
menu_options = [
    "📈 Executive Overview",
    "🚚 Operational Diagnostics",
    "👥 Bracketing & Customer Cohorts",
    "🤖 Return Predictor (ML)",
    "⚙️ Data Pipeline Control Panel"
]
page = st.sidebar.radio("📁 Navigation Pages", menu_options)

# 2. Sidebar Filters (only shown for analytics pages)
if page in ["📈 Executive Overview", "🚚 Operational Diagnostics", "👥 Bracketing & Customer Cohorts"]:
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 Filters")
    if not df.empty:
        years = sorted(df["Order Year"].unique())
        selected_year = st.sidebar.selectbox("Calendar Year", ["All Years"] + list(years))
        categories = sorted(df["Category"].unique())
        selected_categories = st.sidebar.multiselect("Product Categories", categories, default=categories)
        shipping_types = sorted(df["Shipping Type"].unique())
        selected_shipping = st.sidebar.multiselect("Shipping Methods", shipping_types, default=shipping_types)
        sellers = sorted(df["Seller"].unique())
        selected_sellers = st.sidebar.multiselect("Sellers", sellers, default=sellers)

        # Apply Filters to main DataFrame
        filtered_df = df.copy()
        if selected_year != "All Years":
            filtered_df = filtered_df[filtered_df["Order Year"] == selected_year]
        if selected_categories:
            filtered_df = filtered_df[filtered_df["Category"].isin(selected_categories)]
        if selected_shipping:
            filtered_df = filtered_df[filtered_df["Shipping Type"].isin(selected_shipping)]
        if selected_sellers:
            filtered_df = filtered_df[filtered_df["Seller"].isin(selected_sellers)]
    else:
        st.sidebar.info("Please compile the dataset in the Control Panel tab to enable filters.")

# Title block
st.markdown('<div class="main-title">E-Commerce Return & Refund Analysis</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Data-Driven Diagnostics & Optimization Dashboard</div>', unsafe_allow_html=True)

# ----------------- PAGE 1: EXECUTIVE OVERVIEW -----------------
if page == "📈 Executive Overview":
    if df.empty:
        st.warning("⚠️ No cleaned dataset found. Please navigate to the **⚙️ Data Pipeline Control Panel** page and initialize your dataset first.")
    else:
        # Metric Calculations
        t_orders = len(filtered_df)
        t_returned = filtered_df[filtered_df["Return Status"] == "Returned"].shape[0]
        ret_rate = (t_returned / t_orders * 100) if t_orders > 0 else 0
        gross_rev = filtered_df["Total Amount"].sum()
        refund_amt = filtered_df["Refund Amount"].sum()
        logistics_cost = filtered_df["Reverse Logistics Cost"].sum()
        net_loss = filtered_df["Profit Loss"].sum()
        aov = filtered_df["Total Amount"].mean() if t_orders > 0 else 0
        
        # Display KPI Row
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card" style="border-left: 4px solid #3B82F6;">
                <div class="metric-title">Total Orders</div>
                <div class="metric-value">{t_orders:,}</div>
                <div class="metric-delta-green">Avg Value: ${aov:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
            <div class="metric-card" style="border-left: 4px solid #F87171;">
                <div class="metric-title">Return Rate</div>
                <div class="metric-value">{ret_rate:.2f}%</div>
                <div class="metric-delta">Returned: {t_returned:,}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col3:
            st.markdown(f"""
            <div class="metric-card" style="border-left: 4px solid #34D399;">
                <div class="metric-title">Gross Revenue</div>
                <div class="metric-value">${gross_rev:,.2f}</div>
                <div class="metric-delta-green">Net Revenue: ${gross_rev - refund_amt:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col4:
            st.markdown(f"""
            <div class="metric-card" style="border-left: 4px solid #FBBF24;">
                <div class="metric-title">Refunded Amount</div>
                <div class="metric-value">${refund_amt:,.2f}</div>
                <div class="metric-delta">Sales Loss: {(refund_amt / gross_rev * 100) if gross_rev > 0 else 0:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col5:
            st.markdown(f"""
            <div class="metric-card" style="border-left: 4px solid #A78BFA;">
                <div class="metric-title">Net Profit Loss</div>
                <div class="metric-value">${net_loss:,.2f}</div>
                <div class="metric-delta">Logistics: ${logistics_cost:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Charts Row (Interactive Plotly Rendering)
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            monthly_stats = filtered_df.groupby("Month-Year").agg(
                Orders=("Order ID", "count"),
                Returns=("Return Indicator", "sum")
            ).reset_index()
            monthly_stats["Return Rate (%)"] = (monthly_stats["Returns"] / monthly_stats["Orders"]) * 100
            
            # Fast dual axis chart using Plotly Graphic Objects
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=monthly_stats["Month-Year"], 
                y=monthly_stats["Returns"], 
                name="Returns", 
                marker_color="rgba(59, 130, 246, 0.6)"
            ))
            fig.add_trace(go.Scatter(
                x=monthly_stats["Month-Year"], 
                y=monthly_stats["Return Rate (%)"], 
                name="Return Rate", 
                yaxis="y2", 
                line=dict(color="#60A5FA", width=3), 
                mode="lines+markers"
            ))
            fig.update_layout(
                title="Returns Volume & Rate Monthly Timeline",
                yaxis=dict(title=dict(text="Returned Orders", font=dict(color="#94A3B8")), gridcolor="#1E293B"),
                yaxis2=dict(title=dict(text="Return Rate (%)", font=dict(color="#94A3B8")), overlaying="y", side="right", showgrid=False),
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=350,
                margin=dict(l=10, r=10, t=40, b=10),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)
            
        with chart_col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            cat_stats = filtered_df.groupby("Category").agg(
                Rate=("Return Indicator", "mean")
            ).reset_index().sort_values(by="Rate", ascending=False)
            cat_stats["Rate"] *= 100
            
            fig = px.bar(
                cat_stats, x="Category", y="Rate", 
                title="Return Rate (%) across Product Categories",
                labels={"Rate": "Return Rate (%)"}, 
                text="Rate", 
                template="plotly_dark"
            )
            fig.update_traces(
                texttemplate="%{text:.1f}%", 
                textposition="outside", 
                marker_color="rgba(139, 92, 246, 0.7)"
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", 
                plot_bgcolor="rgba(0,0,0,0)", 
                height=350,
                margin=dict(l=10, r=10, t=40, b=10),
                yaxis=dict(gridcolor="#1E293B")
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)

        chart_col3, chart_col4 = st.columns(2)
        with chart_col3:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            ret_df = filtered_df[filtered_df["Return Status"] == "Returned"]
            if not ret_df.empty:
                reason_counts = ret_df["Return Reason"].value_counts().reset_index()
                fig = px.bar(
                    reason_counts, x="count", y="Return Reason", 
                    orientation="h", 
                    title="Primary Reasons for Returns",
                    labels={"count": "Returned Orders"}, 
                    template="plotly_dark"
                )
                fig.update_traces(marker_color="rgba(244, 63, 94, 0.7)")
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", 
                    plot_bgcolor="rgba(0,0,0,0)", 
                    height=320,
                    margin=dict(l=10, r=10, t=40, b=10),
                    xaxis=dict(gridcolor="#1E293B")
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            else:
                st.info("No returned items found for current filters.")
            st.markdown('</div>', unsafe_allow_html=True)
                
        with chart_col4:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            fig = px.box(
                filtered_df, x="Return Status", y="Customer Rating", 
                title="Customer Rating Distribution by Return Status",
                color="Return Status", 
                color_discrete_map={"Not Returned": "#10B981", "Returned": "#EF4444"}, 
                template="plotly_dark"
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", 
                plot_bgcolor="rgba(0,0,0,0)", 
                height=320,
                margin=dict(l=10, r=10, t=40, b=10),
                yaxis=dict(gridcolor="#1E293B"),
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)

# ----------------- PAGE 2: OPERATIONAL DIAGNOSTICS -----------------
elif page == "🚚 Operational Diagnostics":
    if df.empty:
        st.warning("⚠️ No cleaned dataset found. Please navigate to the **⚙️ Data Pipeline Control Panel** page and initialize your dataset first.")
    else:
        st.subheader("📦 Delivery Speed & Shipping Channel Analysis")
        op_col1, op_col2 = st.columns(2)
        
        with op_col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            filtered_df["Is Delayed"] = filtered_df["Delivery Delay"] > 0
            delay_stats = filtered_df.groupby("Is Delayed").agg(
                Rate=("Return Indicator", "mean")
            ).reset_index()
            delay_stats["Rate"] *= 100
            delay_stats["Is Delayed"] = delay_stats["Is Delayed"].map({True: "Delayed (> Target)", False: "On-Time / Early"})
            
            fig = px.bar(
                delay_stats, x="Is Delayed", y="Rate", 
                title="Return Rate: On-Time vs. Delayed Deliveries", 
                labels={"Rate": "Return Rate (%)"}, 
                text="Rate", 
                template="plotly_dark"
            )
            fig.update_traces(
                texttemplate="%{text:.1f}%", 
                textposition="outside", 
                marker_color=["rgba(52, 211, 153, 0.7)", "rgba(248, 113, 113, 0.7)"]
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", 
                plot_bgcolor="rgba(0,0,0,0)", 
                height=350,
                margin=dict(l=10, r=10, t=40, b=10),
                yaxis=dict(gridcolor="#1E293B")
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)
            
        with op_col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            ship_stats = filtered_df.groupby("Shipping Type").agg(
                Rate=("Return Indicator", "mean")
            ).reset_index().sort_values(by="Rate", ascending=False)
            ship_stats["Rate"] *= 100
            
            fig = px.bar(
                ship_stats, x="Shipping Type", y="Rate", 
                title="Return Rate (%) by Shipping Mode", 
                labels={"Rate": "Return Rate (%)"}, 
                text="Rate", 
                template="plotly_dark"
            )
            fig.update_traces(
                texttemplate="%{text:.1f}%", 
                textposition="outside", 
                marker_color="rgba(6, 182, 212, 0.7)"
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", 
                plot_bgcolor="rgba(0,0,0,0)", 
                height=350,
                margin=dict(l=10, r=10, t=40, b=10),
                yaxis=dict(gridcolor="#1E293B")
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)
        st.subheader("🏬 Seller Leaderboards & Warehouse Volumes")
        op_col3, op_col4 = st.columns(2)
        
        with op_col3:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            seller_stats = filtered_df.groupby("Seller").agg(
                Revenue=("Total Amount", "sum"),
                Refunds=("Refund Amount", "sum")
            ).reset_index()
            seller_stats["Refund Ratio (%)"] = (seller_stats["Refunds"] / seller_stats["Revenue"]) * 100
            seller_stats = seller_stats.sort_values(by="Refund Ratio (%)", ascending=True) # Ascending for hbar sort
            
            fig = px.bar(
                seller_stats, y="Seller", x="Refund Ratio (%)", 
                orientation="h", 
                title="Seller Leaderboard: Refund to Revenue Ratio", 
                text="Refund Ratio (%)", 
                template="plotly_dark"
            )
            fig.update_traces(
                texttemplate="%{text:.1f}%", 
                textposition="outside", 
                marker_color="rgba(245, 158, 11, 0.7)"
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", 
                plot_bgcolor="rgba(0,0,0,0)", 
                height=350,
                margin=dict(l=10, r=10, t=40, b=10),
                xaxis=dict(gridcolor="#1E293B")
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)
            
        with op_col4:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            wh_stats = filtered_df.groupby("Warehouse").agg(
                Orders=("Order ID", "count"),
                Returned=("Return Indicator", "sum")
            ).reset_index()
            wh_stats["Return Rate (%)"] = (wh_stats["Returned"] / wh_stats["Orders"]) * 100
            wh_stats = wh_stats.sort_values(by="Return Rate (%)", ascending=False)
            
            fig = px.bar(
                wh_stats, x="Warehouse", y="Return Rate (%)", 
                title="Return Rate (%) by Dispatch Warehouse", 
                text="Return Rate (%)", 
                template="plotly_dark"
            )
            fig.update_traces(
                texttemplate="%{text:.1f}%", 
                textposition="outside", 
                marker_color="rgba(16, 185, 129, 0.7)"
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", 
                plot_bgcolor="rgba(0,0,0,0)", 
                height=350,
                margin=dict(l=10, r=10, t=40, b=10),
                yaxis=dict(gridcolor="#1E293B")
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)

# ----------------- PAGE 3: BRACKETING & CUSTOMER COHORTS -----------------
elif page == "👥 Bracketing & Customer Cohorts":
    if df.empty:
        st.warning("⚠️ No cleaned dataset found. Please navigate to the **⚙️ Data Pipeline Control Panel** page and initialize your dataset first.")
    else:
        st.subheader("👥 Advanced Customer Return Behaviors")
        st.markdown("""
        **Bracketing** occurs when a customer purchases multiple variations (sizes, styles) of the same product at once,
        testing them at home, and returning the incorrect sizes.
        """)
        
        # Calculate bracketing indices
        order_groups = filtered_df.groupby(["Customer ID", "Order Date", "Product Name"])
        bracketing_candidates = order_groups.filter(lambda x: len(x) > 1)
        bracketed_orders = bracketing_candidates.groupby(["Customer ID", "Order Date", "Product Name"]).filter(
            lambda x: (x["Return Status"] == "Returned").any()
        )
        
        brack_count = len(bracketed_orders)
        brack_pct = (brack_count / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
        brack_returned = bracketed_orders[bracketed_orders["Return Status"] == "Returned"]
        brack_loss = brack_returned["Total Amount"].sum()
        
        b_col1, b_col2, b_col3 = st.columns(3)
        with b_col1:
            st.metric("Bracketing-Related Orders", f"{brack_count:,}", f"{brack_pct:.2f}% of Total Orders")
        with b_col2:
            st.metric("Total Returned Bracketed Items", f"{len(brack_returned):,}")
        with b_col3:
            st.metric("Financial Impact of Bracketing", f"${brack_loss:,.2f}", "Gross Refunds Loss")
            
        st.markdown("<hr>", unsafe_allow_html=True)
        
        bc_col1, bc_col2 = st.columns(2)
        with bc_col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            if brack_count > 0:
                brack_grp = brack_returned.groupby("Category").size().reset_index(name="count").sort_values(by="count", ascending=False)
                fig = px.bar(
                    brack_grp, x="Category", y="count", 
                    title="Bracketing Returns by Category", 
                    labels={"count": "Returned Items"}, 
                    template="plotly_dark"
                )
                fig.update_traces(marker_color="rgba(236, 72, 153, 0.7)")
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", 
                    plot_bgcolor="rgba(0,0,0,0)", 
                    height=350,
                    margin=dict(l=10, r=10, t=40, b=10),
                    yaxis=dict(gridcolor="#1E293B")
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            else:
                st.info("No bracketing behavior detected under current filters.")
            st.markdown('</div>', unsafe_allow_html=True)
                
        with bc_col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            age_bins = [18, 25, 35, 45, 55, 75]
            age_labels = ["18-25", "26-35", "36-45", "46-55", "56+"]
            filtered_df["Age Group"] = pd.cut(filtered_df["Customer Age"], bins=age_bins, labels=age_labels)
            
            age_stats = filtered_df.groupby("Age Group", observed=False).agg(
                Rate=("Return Indicator", "mean")
            ).reset_index()
            age_stats["Rate"] *= 100
            
            fig = px.bar(
                age_stats, x="Age Group", y="Rate", 
                title="Return Rate (%) across Age Cohorts", 
                labels={"Rate": "Return Rate (%)"}, 
                text="Rate", 
                template="plotly_dark"
            )
            fig.update_traces(
                texttemplate="%{text:.1f}%", 
                textposition="outside", 
                marker_color="rgba(168, 85, 247, 0.7)"
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", 
                plot_bgcolor="rgba(0,0,0,0)", 
                height=350,
                margin=dict(l=10, r=10, t=40, b=10),
                yaxis=dict(gridcolor="#1E293B")
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)
        st.subheader("🚨 High-Risk Serial Returners")
        st.markdown("These customers exhibit excessively high return rates (Orders >= 3, Return Rate > 50%). The system flags these accounts for review.")
        
        if not chronic_df.empty:
            subset_custs = filtered_df["Customer ID"].unique()
            filtered_chronic = chronic_df[chronic_df["Customer ID"].isin(subset_custs)]
            st.dataframe(
                filtered_chronic.sort_values(by="Return_Rate", ascending=False).rename(
                    columns={
                        "Customer ID": "Customer ID",
                        "Total_Orders": "Lifetime Orders",
                        "Returned_Orders": "Returned Orders",
                        "Return_Rate": "Return Rate Ratio"
                    }
                ),
                use_container_width=True
            )
        else:
            st.info("No chronic returners data found. Please compile the dataset in the Control Panel.")

# ----------------- PAGE 4: RETURN PREDICTOR (ML) -----------------
elif page == "🤖 Return Predictor (ML)":
    st.subheader("🤖 Real-Time Returns Predictive Simulator (Machine Learning)")
    st.markdown("Use this panel to simulate a checkout cart and predict the probability that a customer will return the items in their cart.")
    
    model_paths = ["return_prediction_pipeline.pkl", "dashboard/return_prediction_pipeline.pkl", "../dashboard/return_prediction_pipeline.pkl"]
    model_file_path = None
    for mp in model_paths:
        if os.path.exists(mp):
            model_file_path = mp
            break
            
    model_loaded = False
    model = None
    if model_file_path:
        try:
            with open(model_file_path, "rb") as f:
                model = pickle.load(f)
            model_loaded = True
        except Exception as e:
            st.error(f"Failed to load the trained model pipeline. Error: {e}")
    else:
        st.warning("⚠️ Prediction pipeline pickle file not found. Please navigate to the **⚙️ Data Pipeline Control Panel** and click **Train Model** first.")

    if model_loaded and not df.empty:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        sim_col1, sim_col2, sim_col3 = st.columns(3)
        
        with sim_col1:
            st.markdown("### 🛒 Product & Pricing")
            sim_category = st.selectbox("Product Category", sorted(df["Category"].unique()))
            cat_brands = sorted(df[df["Category"] == sim_category]["Brand"].unique())
            sim_brand = st.selectbox("Product Brand", cat_brands)
            sim_price = st.number_input("Base Item Price ($)", min_value=1.0, max_value=15000.0, value=float(df[df["Category"] == sim_category]["Price"].median()))
            sim_qty = st.slider("Quantity in Cart", min_value=1, max_value=10, value=1)
            
        with sim_col2:
            st.markdown("### 🚚 Logistics & Operations")
            sim_shipping = st.selectbox("Selected Shipping Method", sorted(df["Shipping Type"].unique()))
            sim_seller = st.selectbox("Assigned Seller Merchant", sorted(df["Seller"].unique()))
            sim_delivery = st.slider("Expected/Actual Delivery Days", min_value=1, max_value=20, value=4)
            sim_discount = st.slider("Discount Applied (%)", min_value=0, max_value=60, value=0, step=5) / 100.0
            
        with sim_col3:
            st.markdown("### 👤 Customer Profile")
            sim_age = st.slider("Customer Age", min_value=18, max_value=80, value=35)
            sim_gender = st.selectbox("Gender", sorted(df["Gender"].unique()))
            sim_segment = st.selectbox("Customer Market Segment", sorted(df["Segment"].unique()))

        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("🔮 Predict Return Probability", type="primary"):
            input_df = pd.DataFrame([{
                "Category": sim_category, "Brand": sim_brand, "Shipping Type": sim_shipping,
                "Seller": sim_seller, "Segment": sim_segment, "Gender": sim_gender,
                "Price": sim_price, "Quantity": sim_qty, "Discount": sim_discount,
                "Delivery Days": sim_delivery, "Customer Age": sim_age
            }])
            
            prob = model.predict_proba(input_df)[0][1]
            prob_percent = prob * 100
            
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("## 📊 Prediction Scorecard")
            score_col1, score_col2 = st.columns([1, 2])
            
            with score_col1:
                if prob_percent < 20:
                    status_color = "#34D399"
                    status_text = "LOW RISK"
                elif prob_percent < 45:
                    status_color = "#FBBF24"
                    status_text = "MEDIUM RISK"
                else:
                    status_color = "#F87171"
                    status_text = "HIGH RISK"
                    
                st.markdown(f"""
                <div style="background-color: {status_color}18; border: 2px solid {status_color}; border-radius: 12px; padding: 25px; text-align: center; box-shadow: 0 4px 20px {status_color}22;">
                    <div style="font-size: 13px; font-weight: 600; color: #94A3B8; text-transform: uppercase; letter-spacing:0.05em;">Return Likelihood</div>
                    <div style="font-size: 54px; font-weight: 800; color: {status_color}; margin: 12px 0;">{prob_percent:.1f}%</div>
                    <div style="font-size: 18px; font-weight: 700; color: {status_color}; letter-spacing:0.02em;">{status_text}</div>
                </div>
                """, unsafe_allow_html=True)
                
            with score_col2:
                st.markdown('<div class="chart-container" style="padding: 25px; height: 100%;">', unsafe_allow_html=True)
                st.markdown("### 📋 Predictive Explanations & Recommendations")
                recs = []
                if sim_delivery > 5:
                    recs.append("⚠️ **Logistics Delay**: The simulated delivery time is long. This is the #1 driver of returns. Recommendation: Offer standard express upgrades.")
                if sim_category == "Clothing":
                    recs.append("👕 **Sizing fit hazard**: Apparel has a base return rate of 41%. Recommendation: Prompt the user with a dynamic size chart overlay.")
                if sim_discount >= 0.40:
                    recs.append("🏷️ **Impulse purchase discount**: High discount rates (>40%) prompt impulse buying. Recommendation: Include post-checkout follow-up engagement.")
                if sim_seller == "Seller E (Budget Imports)":
                    recs.append("🏬 **Seller Merchant Quality Alert**: Seller E has a historical refund rate of 41%. Recommendation: Increase quality inspection controls.")
                if sim_price > 500:
                    recs.append("💎 **High Ticket Value Item**: Products > $500 carry higher buyer remorse rates. Recommendation: Offer phone support outreach.")
                    
                if not recs:
                    st.success("✅ This order profile matches standard transaction behavior with low risk vectors. No immediate action required.")
                else:
                    for r in recs:
                        st.markdown(r)
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("The predictor will become interactive once data files are compiled and model is trained.")

# ----------------- PAGE 5: DATA PIPELINE CONTROL PANEL -----------------
elif page == "⚙️ Data Pipeline Control Panel":
    st.subheader("⚙️ Local Data Pipeline Admin Panel")
    st.markdown("""
    This control panel allows you to run, synthesize, clean, and train the entire data project pipeline directly from this web interface.
    No Jupyter Notebook or terminal command execution required!
    """)
    
    col_gen, col_clean, col_train = st.columns(3)
    
    with col_gen:
        st.markdown("""
        <div style="background: rgba(59, 130, 246, 0.12); border: 1px solid rgba(96, 165, 250, 0.25); border-radius:14px; padding:22px; height:380px; box-shadow: 0 4px 30px rgba(59, 130, 246, 0.05); backdrop-filter: blur(10px);">
            <h3 style="color:#60A5FA; margin-top:0px; font-weight:800; font-size:20px;">1. Synthesize Raw Data</h3>
            <p style="font-size:13.5px; color:#94A3B8; line-height:1.5;">Generates a new raw transactional dataset representing live e-commerce sales with simulated anomalies, bracketing fits, and shipping lags.</p>
        </div>
        """, unsafe_allow_html=True)
        
        num_orders_input = st.slider("Select Order Record Count", min_value=5000, max_value=100000, value=50000, step=5000)
        
        if st.button("🚀 Generate Raw Data", use_container_width=True):
            st.info("Generating raw dataset...")
            gen_progress = st.progress(0)
            try:
                rows_gen, saved_to = run_data_generation_backend(num_orders_input, gen_progress)
                st.success(f"Generated {rows_gen:,} rows! Saved to: `{saved_to}`")
                st.toast("Raw data successfully generated!", icon="🚀")
            except Exception as e:
                st.error(f"Generation failed: {e}")
                
    with col_clean:
        st.markdown("""
        <div style="background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(52, 211, 153, 0.25); border-radius:14px; padding:22px; height:380px; box-shadow: 0 4px 30px rgba(16, 185, 129, 0.05); backdrop-filter: blur(10px);">
            <h3 style="color:#34D399; margin-top:0px; font-weight:800; font-size:20px;">2. Clean & Process Data</h3>
            <p style="font-size:13.5px; color:#94A3B8; line-height:1.5;">Executes the sanitization rules (removes duplicates, casts currencies/dates, fixes negatives, imputes ratings) and calculates logistics overhead.</p>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        
        if st.button("🧼 Run Data Cleaning", use_container_width=True):
            st.info("Running cleaning pipeline...")
            clean_progress = st.progress(0)
            try:
                audit_log = run_data_cleaning_backend(clean_progress)
                st.success("Cleaned data generated successfully!")
                st.toast("Data cleaning completed!", icon="🧼")
                
                with st.expander("📝 View Cleaning Audit Log", expanded=True):
                    st.code(audit_log)
                    
                st.cache_data.clear()
            except Exception as e:
                st.error(f"Cleaning failed: {e}")
                
    with col_train:
        st.markdown("""
        <div style="background: rgba(236, 72, 153, 0.12); border: 1px solid rgba(244, 114, 182, 0.25); border-radius:14px; padding:22px; height:380px; box-shadow: 0 4px 30px rgba(236, 72, 153, 0.05); backdrop-filter: blur(10px);">
            <h3 style="color:#F472B6; margin-top:0px; font-weight:800; font-size:20px;">3. Train Predictor (ML)</h3>
            <p style="font-size:13.5px; color:#94A3B8; line-height:1.5;">Splits the cleaned dataset, standardizes columns, trains a Random Forest Classifier to identify return risks, and exports the serialized pipeline.</p>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        
        if st.button("🧠 Train ML Model", use_container_width=True):
            st.info("Training predictor model...")
            train_progress = st.progress(0)
            try:
                ml_log = run_model_training_backend(train_progress)
                st.success("Model pipeline successfully trained!")
                st.toast("Predictive model trained!", icon="🧠")
                
                with st.expander("📊 View Model Training Log", expanded=True):
                    st.code(ml_log)
            except Exception as e:
                st.error(f"Training failed: {e}")
