import os
import pickle
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

# Set page config
st.set_page_config(
    page_title="E-Commerce Return & Refund Analyst",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern premium dashboard design
st.markdown("""
<style>
    /* Styling headers */
    .main-title {
        font-size: 38px;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 2px;
        padding-bottom: 0px;
    }
    .sub-title {
        font-size: 16px;
        color: #4B5563;
        margin-bottom: 25px;
    }
    /* Metric Cards */
    .metric-card {
        background-color: #F8FAFC;
        border-left: 5px solid #3B82F6;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
        margin-bottom: 15px;
    }
    .metric-title {
        font-size: 14px;
        color: #64748B;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 5px;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 800;
        color: #1E293B;
    }
    .metric-delta {
        font-size: 12px;
        color: #EF4444;
        font-weight: 500;
    }
    .metric-delta-green {
        font-size: 12px;
        color: #10B981;
        font-weight: 500;
    }
    /* Divider */
    hr {
        margin-top: 1rem;
        margin-bottom: 1.5rem;
        border: 0;
        border-top: 1px solid #E2E8F0;
    }
</style>
""", unsafe_allow_html=True)

# 1. Load Datasets (Cached)
@st.cache_data
def load_data():
    # Attempt to locate cleaned data
    paths = ["data/cleaned_data.csv", "../data/cleaned_data.csv"]
    data_path = None
    for p in paths:
        if os.path.exists(p):
            data_path = p
            break
            
    if data_path is None:
        st.error("Cleaned data not found. Please run the data generation and cleaning notebooks first.")
        return pd.DataFrame(), pd.DataFrame()
        
    df = pd.read_csv(data_path)
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    
    # Load chronic returners
    chronic_paths = ["data/chronic_returners.csv", "../data/chronic_returners.csv"]
    chronic_path = None
    for cp in chronic_paths:
        if os.path.exists(cp):
            chronic_path = cp
            break
            
    chronic_df = pd.read_csv(chronic_path) if chronic_path else pd.DataFrame()
    return df, chronic_df

df, chronic_df = load_data()

if df.empty:
    st.stop()

# 2. Sidebar Filters
st.sidebar.image("https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?auto=format&fit=crop&q=80&w=200", use_container_width=True)
st.sidebar.header("📊 Filter Controls")

# Year Filter
years = sorted(df["Order Year"].unique())
selected_year = st.sidebar.selectbox("Calendar Year", ["All Years"] + list(years))

# Category Filter
categories = sorted(df["Category"].unique())
selected_categories = st.sidebar.multiselect("Product Categories", categories, default=categories)

# Shipping Type Filter
shipping_types = sorted(df["Shipping Type"].unique())
selected_shipping = st.sidebar.multiselect("Shipping Methods", shipping_types, default=shipping_types)

# Seller Filter
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

# Title block
st.markdown('<div class="main-title">E-Commerce Return & Refund Analysis</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Data-Driven Diagnostics & Optimization Dashboard</div>', unsafe_allow_html=True)

# 3. Create Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Executive Overview",
    "🚚 Operational & Seller Diagnostics",
    "👥 Bracketing & Customer Cohorts",
    "🤖 Real-Time Return Predictor (ML)"
])

# ----------------- TAB 1: EXECUTIVE OVERVIEW -----------------
with tab1:
    # 3.1 Metric Calculations
    t_orders = len(filtered_df)
    t_returned = filtered_df[filtered_df["Return Status"] == "Returned"].shape[0]
    ret_rate = (t_returned / t_orders * 100) if t_orders > 0 else 0
    gross_rev = filtered_df["Total Amount"].sum()
    refund_amt = filtered_df["Refund Amount"].sum()
    logistics_cost = filtered_df["Reverse Logistics Cost"].sum()
    net_loss = filtered_df["Profit Loss"].sum()
    aov = filtered_df["Total Amount"].mean() if t_orders > 0 else 0
    avg_rating = filtered_df["Customer Rating"].mean() if t_orders > 0 else 0
    
    # 3.2 Display KPI Row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #3B82F6;">
            <div class="metric-title">Total Orders</div>
            <div class="metric-value">{t_orders:,}</div>
            <div class="metric-delta-green">Avg Value: ${aov:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #EF4444;">
            <div class="metric-title">Return Rate</div>
            <div class="metric-value">{ret_rate:.2f}%</div>
            <div class="metric-delta">Returned Orders: {t_returned:,}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #10B981;">
            <div class="metric-title">Gross Revenue</div>
            <div class="metric-value">${gross_rev:,.2f}</div>
            <div class="metric-delta-green">Net Revenue: ${gross_rev - refund_amt:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #F59E0B;">
            <div class="metric-title">Refunded Amount</div>
            <div class="metric-value">${refund_amt:,.2f}</div>
            <div class="metric-delta">Lost Revenue: {(refund_amt / gross_rev * 100) if gross_rev > 0 else 0:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col5:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #7C3AED;">
            <div class="metric-title">Net Profit Loss</div>
            <div class="metric-value">${net_loss:,.2f}</div>
            <div class="metric-delta">Logistics Cost: ${logistics_cost:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    
    # 3.3 Charts Row
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.subheader("📅 Monthly Return Volume and Return Rate Trend")
        # Compute monthly trend
        monthly_stats = filtered_df.groupby("Month-Year").agg(
            Orders=("Order ID", "count"),
            Returns=("Return Indicator", "sum")
        ).reset_index()
        monthly_stats["Return Rate (%)"] = (monthly_stats["Returns"] / monthly_stats["Orders"]) * 100
        
        fig, ax1 = plt.subplots(figsize=(10, 5))
        ax2 = ax1.twinx()
        
        # Bars for returns
        sns.barplot(data=monthly_stats, x="Month-Year", y="Returns", color="#93C5FD", ax=ax1, alpha=0.8)
        # Line for return rate
        sns.lineplot(data=monthly_stats, x="Month-Year", y="Return Rate (%)", color="#1E3A8A", marker="o", linewidth=2.5, ax=ax2)
        
        ax1.set_ylabel("Returned Orders", color="#1E3A8A", fontweight="bold")
        ax2.set_ylabel("Return Rate (%)", color="#1E3A8A", fontweight="bold")
        ax1.set_xlabel("Month-Year", fontweight="bold")
        ax1.set_xticklabels(monthly_stats["Month-Year"], rotation=45)
        plt.title("Returns Volume & Rate Monthly Timeline", fontsize=14, fontweight="bold")
        fig.tight_layout()
        st.pyplot(fig)
        plt.close()
        
    with chart_col2:
        st.subheader("💡 Distribution of Product Returns by Category")
        cat_stats = filtered_df.groupby("Category").agg(
            Total=("Order ID", "count"),
            Returned=("Return Indicator", "sum"),
            Rate=("Return Indicator", "mean")
        ).reset_index().sort_values(by="Rate", ascending=False)
        cat_stats["Rate"] *= 100
        
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(data=cat_stats, x="Category", y="Rate", palette="Blues_r", ax=ax)
        ax.set_ylabel("Return Rate (%)", fontweight="bold")
        ax.set_xlabel("Product Category", fontweight="bold")
        plt.title("Return Rate (%) across Product Categories", fontsize=14, fontweight="bold")
        
        # Add labels on top of bars
        for container in ax.containers:
            ax.bar_label(container, fmt="%.1f%%")
            
        fig.tight_layout()
        st.pyplot(fig)
        plt.close()

    chart_col3, chart_col4 = st.columns(2)
    with chart_col3:
        st.subheader("🏷️ Return Reasons Breakdown")
        ret_df = filtered_df[filtered_df["Return Status"] == "Returned"]
        if not ret_df.empty:
            reason_counts = ret_df["Return Reason"].value_counts().reset_index()
            
            fig, ax = plt.subplots(figsize=(10, 5))
            sns.barplot(data=reason_counts, x="count", y="Return Reason", palette="magma", ax=ax)
            ax.set_xlabel("Number of Returned Orders", fontweight="bold")
            ax.set_ylabel("Reason", fontweight="bold")
            plt.title("Primary Reasons for Returns", fontsize=14, fontweight="bold")
            fig.tight_layout()
            st.pyplot(fig)
            plt.close()
        else:
            st.info("No returned items found for current filters.")
            
    with chart_col4:
        st.subheader("⭐ Customer Ratings: Returned vs. Kept Products")
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.boxplot(
            data=filtered_df, 
            x="Return Status", 
            y="Customer Rating", 
            palette={"Not Returned": "#10B981", "Returned": "#EF4444"}, 
            ax=ax
        )
        ax.set_xlabel("Return Status", fontweight="bold")
        ax.set_ylabel("Customer Rating (1-5)", fontweight="bold")
        plt.title("Customer Rating Distribution by Return Status", fontsize=14, fontweight="bold")
        fig.tight_layout()
        st.pyplot(fig)
        plt.close()

# ----------------- TAB 2: OPERATIONAL & SELLER DIAGNOSTICS -----------------
with tab2:
    st.subheader("📦 Delivery Speed & Shipping Channel Analysis")
    st.markdown("Returns are heavily driven by delivery issues. Below is a deep dive into shipping methods and shipping delays.")
    
    op_col1, op_col2 = st.columns(2)
    
    with op_col1:
        st.markdown("**Does delivery delay impact return behavior?**")
        filtered_df["Is Delayed"] = filtered_df["Delivery Delay"] > 0
        delay_stats = filtered_df.groupby("Is Delayed").agg(
            Orders=("Order ID", "count"),
            Returns=("Return Indicator", "sum"),
            Rate=("Return Indicator", "mean")
        ).reset_index()
        delay_stats["Rate"] *= 100
        delay_stats["Is Delayed"] = delay_stats["Is Delayed"].map({True: "Delayed (> Expected Days)", False: "On-Time / Early"})
        
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(data=delay_stats, x="Is Delayed", y="Rate", palette="coolwarm", ax=ax)
        ax.set_ylabel("Return Rate (%)", fontweight="bold")
        ax.set_xlabel("Shipment Delivery Status", fontweight="bold")
        plt.title("Return Rate Comparison: On-Time vs. Delayed Deliveries", fontsize=14, fontweight="bold")
        for container in ax.containers:
            ax.bar_label(container, fmt="%.1f%%")
        fig.tight_layout()
        st.pyplot(fig)
        plt.close()
        
    with op_col2:
        st.markdown("**Which shipping method returns the most?**")
        ship_stats = filtered_df.groupby("Shipping Type").agg(
            Orders=("Order ID", "count"),
            Rate=("Return Indicator", "mean")
        ).reset_index()
        ship_stats["Rate"] *= 100
        ship_stats = ship_stats.sort_values(by="Rate", ascending=False)
        
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(data=ship_stats, x="Shipping Type", y="Rate", palette="viridis", ax=ax)
        ax.set_ylabel("Return Rate (%)", fontweight="bold")
        ax.set_xlabel("Shipping Channel", fontweight="bold")
        plt.title("Return Rate (%) by Shipping Mode", fontsize=14, fontweight="bold")
        for container in ax.containers:
            ax.bar_label(container, fmt="%.1f%%")
        fig.tight_layout()
        st.pyplot(fig)
        plt.close()

    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("🏬 Seller Leaderboards & Reverse Logistics Cost")
    
    op_col3, op_col4 = st.columns(2)
    
    with op_col3:
        st.markdown("**Seller Refund Ratios (Total Refunds / Total Revenue)**")
        seller_stats = filtered_df.groupby("Seller").agg(
            Revenue=("Total Amount", "sum"),
            Refunds=("Refund Amount", "sum")
        ).reset_index()
        seller_stats["Refund Ratio (%)"] = (seller_stats["Refunds"] / seller_stats["Revenue"]) * 100
        seller_stats = seller_stats.sort_values(by="Refund Ratio (%)", ascending=False)
        
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(data=seller_stats, y="Seller", x="Refund Ratio (%)", palette="flare", ax=ax)
        ax.set_xlabel("Refund Ratio (%)", fontweight="bold")
        ax.set_ylabel("Seller Name", fontweight="bold")
        plt.title("Seller Leaderboard: Refund to Revenue Ratio", fontsize=14, fontweight="bold")
        for container in ax.containers:
            ax.bar_label(container, fmt="%.1f%%")
        fig.tight_layout()
        st.pyplot(fig)
        plt.close()
        
    with op_col4:
        st.markdown("**Warehouse Return Volumes & Return Rates**")
        wh_stats = filtered_df.groupby("Warehouse").agg(
            Orders=("Order ID", "count"),
            Returned=("Return Indicator", "sum")
        ).reset_index()
        wh_stats["Return Rate (%)"] = (wh_stats["Returned"] / wh_stats["Orders"]) * 100
        wh_stats = wh_stats.sort_values(by="Return Rate (%)", ascending=False)
        
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(data=wh_stats, x="Warehouse", y="Return Rate (%)", palette="crest", ax=ax)
        ax.set_ylabel("Return Rate (%)", fontweight="bold")
        ax.set_xlabel("Warehouse Location", fontweight="bold")
        plt.title("Return Rate (%) by Dispatch Warehouse", fontsize=14, fontweight="bold")
        for container in ax.containers:
            ax.bar_label(container, fmt="%.1f%%")
        fig.tight_layout()
        st.pyplot(fig)
        plt.close()

# ----------------- TAB 3: BRACKETING & CUSTOMER COHORTS -----------------
with tab3:
    st.subheader("👥 Advanced Customer Return Behaviors")
    st.markdown("""
    **What is Bracketing?**
    Bracketing occurs when a customer purchases multiple variations (sizes, styles, colors) of the same product at the same time,
    testing them at home, and returning all except one.
    """)
    
    # 3.1 Calculate bracketing indices
    # Group by Customer, Order Date, and Product Name
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
        st.markdown("**Which Categories suffer from Bracketing the most?**")
        if brack_count > 0:
            fig, ax = plt.subplots(figsize=(10, 5))
            sns.countplot(data=brack_returned, x="Category", palette="cool", order=brack_returned["Category"].value_counts().index, ax=ax)
            ax.set_ylabel("Returned Items Count", fontweight="bold")
            ax.set_xlabel("Product Category", fontweight="bold")
            plt.title("Bracketing Returns by Category", fontsize=14, fontweight="bold")
            fig.tight_layout()
            st.pyplot(fig)
            plt.close()
        else:
            st.info("No bracketing behavior detected under current filters.")
            
    with bc_col2:
        st.markdown("**Demographics Analysis: Age Groups & Return Rates**")
        age_bins = [18, 25, 35, 45, 55, 75]
        age_labels = ["18-25", "26-35", "36-45", "46-55", "56+"]
        filtered_df["Age Group"] = pd.cut(filtered_df["Customer Age"], bins=age_bins, labels=age_labels)
        
        age_stats = filtered_df.groupby("Age Group", observed=False).agg(
            Rate=("Return Indicator", "mean")
        ).reset_index()
        age_stats["Rate"] *= 100
        
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(data=age_stats, x="Age Group", y="Rate", palette="Purples", ax=ax)
        ax.set_ylabel("Return Rate (%)", fontweight="bold")
        ax.set_xlabel("Customer Age Cohort", fontweight="bold")
        plt.title("Return Rate (%) across Age Cohorts", fontsize=14, fontweight="bold")
        for container in ax.containers:
            ax.bar_label(container, fmt="%.1f%%")
        fig.tight_layout()
        st.pyplot(fig)
        plt.close()

    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("🚨 High-Risk Serial Returners")
    st.markdown("These customers exhibit excessively high return rates (Orders >= 3, Return Rate > 50%). The system flags these accounts for customer service review.")
    
    if not chronic_df.empty:
        # Filter chronic returners present in current filtered subset of customers
        subset_custs = filtered_df["Customer ID"].unique()
        filtered_chronic = chronic_df[chronic_df["Customer ID"].isin(subset_custs)]
        
        # Display table
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
        st.info("No chronic returners data found. Please run Notebook 02 first.")

# ----------------- TAB 4: REAL-TIME RETURN PREDICTOR -----------------
with tab4:
    st.subheader("🤖 Real-Time Returns Predictive Simulator (Machine Learning)")
    st.markdown("Use this panel to simulate a checkout cart and predict the probability that a customer will return the items in their cart. Adjust the operational and catalog settings to see how it affects return likelihood.")
    
    # 4.1 Load serialized model
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
        st.warning("Prediction pipeline pickle file not found. Ensure Notebook 04 has run to train the model.")

    if model_loaded:
        # Input parameters layout
        sim_col1, sim_col2, sim_col3 = st.columns(3)
        
        with sim_col1:
            st.markdown("### 🛒 Product & Pricing")
            sim_category = st.selectbox("Product Category", sorted(df["Category"].unique()))
            # Filter brands by category for consistency
            cat_brands = sorted(df[df["Category"] == sim_category]["Brand"].unique())
            sim_brand = st.selectbox("Product Brand", cat_brands)
            sim_price = st.number_input("Base Item Price ($)", min_value=1.0, max_value=15000.0, value=float(df[df["Category"] == sim_category]["Price"].median()))
            sim_qty = st.slider("Quantity in Cart", min_value=1, max_value=10, value=1)
            
        with sim_col2:
            st.markdown("### 🚚 Logistics & Operations")
            sim_shipping = st.selectbox("Selected Shipping Method", sorted(df["Shipping Type"].unique()))
            # Filter sellers
            sim_seller = st.selectbox("Assigned Seller Merchant", sorted(df["Seller"].unique()))
            sim_delivery = st.slider("Expected/Actual Delivery Days", min_value=1, max_value=20, value=4)
            sim_discount = st.slider("Discount Applied (%)", min_value=0, max_value=60, value=0, step=5) / 100.0
            
        with sim_col3:
            st.markdown("### 👤 Customer Profile")
            sim_age = st.slider("Customer Age", min_value=18, max_value=80, value=35)
            sim_gender = st.selectbox("Gender", sorted(df["Gender"].unique()))
            sim_segment = st.selectbox("Customer Market Segment", sorted(df["Segment"].unique()))

        # Button to run prediction
        if st.button("🔮 Predict Return Probability", type="primary"):
            # Create a single-row dataframe to match model inputs
            input_df = pd.DataFrame([{
                "Category": sim_category,
                "Brand": sim_brand,
                "Shipping Type": sim_shipping,
                "Seller": sim_seller,
                "Segment": sim_segment,
                "Gender": sim_gender,
                "Price": sim_price,
                "Quantity": sim_qty,
                "Discount": sim_discount,
                "Delivery Days": sim_delivery,
                "Customer Age": sim_age
            }])
            
            # Predict probability
            prob = model.predict_proba(input_df)[0][1]
            prob_percent = prob * 100
            
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("## 📊 Prediction Scorecard")
            
            score_col1, score_col2 = st.columns([1, 2])
            
            with score_col1:
                # Color code status
                if prob_percent < 20:
                    status_color = "#10B981"  # Green
                    status_text = "LOW RISK"
                elif prob_percent < 45:
                    status_color = "#F59E0B"  # Orange
                    status_text = "MEDIUM RISK"
                else:
                    status_color = "#EF4444"  # Red
                    status_text = "HIGH RISK"
                    
                st.markdown(f"""
                <div style="background-color: {status_color}22; border: 2px solid {status_color}; border-radius: 8px; padding: 25px; text-align: center;">
                    <div style="font-size: 14px; font-weight: 600; color: #475569; text-transform: uppercase;">Return Likelihood</div>
                    <div style="font-size: 52px; font-weight: 800; color: {status_color}; margin: 10px 0;">{prob_percent:.1f}%</div>
                    <div style="font-size: 18px; font-weight: 700; color: {status_color};">{status_text}</div>
                </div>
                """, unsafe_allow_html=True)
                
            with score_col2:
                st.markdown("### 📋 Predictive Explanations & Recommendations")
                
                # Check top risk drivers
                recs = []
                if sim_delivery > 5:
                    recs.append("⚠️ **Logistics Delay**: The simulated delivery time is long (>{5} days). This is the #1 driver of returns. Recommendation: Offer standard express upgrades or notify customer to prevent 'Late Delivery' cancellations.")
                if sim_category == "Clothing":
                    recs.append("👕 **Sizing fit hazard**: Apparel has a base return rate of 41%. Recommendation: Prompt the user with a dynamic size chart overlay on the checkout page to avoid 'Wrong Size' returns.")
                if sim_discount >= 0.40:
                    recs.append("🏷️ **Impulse purchase discount**: High discount rates (>40%) prompt impulse buying. Recommendation: Include post-checkout follow-up engagement or limit returns on extreme discount clearances.")
                if sim_seller == "Seller E (Budget Imports)":
                    recs.append("🏬 **Seller Merchant Quality Alert**: Seller E has a historical refund rate of 41%. Recommendation: Increase quality inspection controls or trigger pre-shipping inspection certificates for this seller's products.")
                if sim_price > 500:
                    recs.append("💎 **High Ticket Value Item**: Products > $500 carry higher buyer remorse rates. Recommendation: Offer phone support outreach or extended product assurances.")
                    
                if not recs:
                    st.success("✅ This order profile matches standard transaction behavior with low risk vectors. No immediate action required.")
                else:
                    for r in recs:
                        st.markdown(r)
    else:
        st.info("The predictor will become interactive once the model is trained in Notebook 04.")
