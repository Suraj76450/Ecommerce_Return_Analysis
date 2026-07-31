# %% [markdown]
# # Phase 2: Exploratory Data Analysis (EDA) & Feature Engineering
# This notebook implements:
# 1. **Feature Engineering**: Creating additional columns (Return Rate indicator, Delivery Delay, Discount %, Weekday, Month, Year, Reverse Logistics Cost, and Net Financial Impact).
# 2. **Univariate Analysis**: Examining the distribution of individual columns.
# 3. **Bivariate Analysis**: Visualizing relations between pairs of variables (e.g., category vs. return rate).
# 4. **Multivariate Analysis**: Combining multiple columns to surface deep insights.
# 5. **Advanced Analyses**: Cohort analysis and Customer Bracketing (purchasing multiple sizes/colors to return all but one).
# 6. **Save Visualization Images**: Exporting key plots to the `images/` folder for use in reporting and dashboard layouts.

# %% [code]
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set plotting style
sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (10, 6)
plt.rcParams["font.size"] = 12

# Paths
input_path = "../data/cleaned_data.csv"
output_path = "../data/cleaned_data.csv" # Overwriting with engineered features
images_dir = "../images"
os.makedirs(images_dir, exist_ok=True)

# %% [markdown]
# ## 1. Load Data & Feature Engineering

# %% [code]
df = pd.read_csv(input_path)
df["Order Date"] = pd.to_datetime(df["Order Date"])

# 1.1 Return Rate Indicator
df["Return Indicator"] = (df["Return Status"] == "Returned").astype(int)

# 1.2 Expected Delivery Days mapping
shipping_expected = {"Overnight": 1, "Express": 2, "Standard": 5}
expected_days = df["Shipping Type"].map(shipping_expected)

# 1.3 Delivery Delay (Actual - Expected, clipped at 0)
df["Delivery Delay"] = (df["Delivery Days"] - expected_days).clip(lower=0)

# 1.4 Discount Percentage
df["Discount Percentage"] = df["Discount"] * 100

# 1.5 Date components
df["Order Month"] = df["Order Date"].dt.month
df["Order Year"] = df["Order Date"].dt.year
df["Weekday"] = df["Order Date"].dt.day_name()
df["Month-Year"] = df["Order Date"].dt.to_period("M").astype(str)

# 1.6 Reverse Logistics Cost
# Flat $5.00 return shipping + 10% restocking overhead fee for returned items
df["Reverse Logistics Cost"] = np.where(
    df["Return Status"] == "Returned",
    5.00 + (0.10 * df["Total Amount"]),
    0.00
)

# 1.7 Net Financial Impact
# If returned, company loses refund amount (which equals total amount) and incurs reverse logistics cost.
# If not returned, net financial impact is total amount.
df["Net Financial Impact"] = np.where(
    df["Return Status"] == "Returned",
    -df["Reverse Logistics Cost"],
    df["Total Amount"]
)

# Profit Loss from Returns (Refund + Reverse Logistics Cost)
df["Profit Loss"] = np.where(
    df["Return Status"] == "Returned",
    df["Refund Amount"] + df["Reverse Logistics Cost"],
    0.00
)

print("Feature Engineering complete. First 3 rows:")
print(df[["Order ID", "Shipping Type", "Delivery Days", "Delivery Delay", "Reverse Logistics Cost", "Net Financial Impact"]].head(3))

# Save engineered dataset back
df.to_csv(output_path, index=False)

# %% [markdown]
# ## 2. Univariate Analysis

# %% [code]
# 2.1 Product Category distribution
plt.figure()
sns.countplot(data=df, x="Category", order=df["Category"].value_counts().index, palette="viridis")
plt.title("Distribution of Orders by Category")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"{images_dir}/category_distribution.png")
plt.close()

# 2.2 Return Reason distribution (for returned items only)
plt.figure()
returned_df = df[df["Return Status"] == "Returned"]
sns.countplot(data=returned_df, y="Return Reason", order=returned_df["Return Reason"].value_counts().index, palette="magma")
plt.title("Primary Reasons for Returns")
plt.tight_layout()
plt.savefig(f"{images_dir}/return_reasons_distribution.png")
plt.close()

# 2.3 Customer Rating distribution
plt.figure()
sns.countplot(data=df, x="Customer Rating", palette="rocket")
plt.title("Distribution of Customer Ratings")
plt.tight_layout()
plt.savefig(f"{images_dir}/ratings_distribution.png")
plt.close()

# 2.4 Delivery Days distribution
plt.figure()
sns.histplot(data=df, x="Delivery Days", bins=15, kde=True, color="teal")
plt.title("Distribution of Delivery Days")
plt.tight_layout()
plt.savefig(f"{images_dir}/delivery_days_distribution.png")
plt.close()

print("Univariate analysis plots exported to images/ directory.")

# %% [markdown]
# ## 3. Bivariate Analysis

# %% [code]
# 3.1 Category vs Return Rate
plt.figure()
category_returns = df.groupby("Category")["Return Indicator"].mean().reset_index().sort_values(by="Return Indicator", ascending=False)
sns.barplot(data=category_returns, x="Category", y="Return Indicator", palette="Blues_r")
plt.title("Return Rate by Product Category")
plt.ylabel("Return Rate (%)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"{images_dir}/category_vs_return_rate.png")
plt.close()

# 3.2 Shipping Type vs Return Rate
plt.figure()
shipping_returns = df.groupby("Shipping Type")["Return Indicator"].mean().reset_index().sort_values(by="Return Indicator", ascending=False)
sns.barplot(data=shipping_returns, x="Shipping Type", y="Return Indicator", palette="crest")
plt.title("Return Rate by Shipping Type")
plt.ylabel("Return Rate (%)")
plt.tight_layout()
plt.savefig(f"{images_dir}/shipping_type_vs_return_rate.png")
plt.close()

# 3.3 State vs Refund Amount (Top States by Refunds)
plt.figure()
state_refunds = df.groupby("State")["Refund Amount"].sum().reset_index().sort_values(by="Refund Amount", ascending=False)
sns.barplot(data=state_refunds, x="State", y="Refund Amount", palette="flare")
plt.title("Total Refund Amount by State")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"{images_dir}/state_vs_refunds.png")
plt.close()

# 3.4 Discount % vs Return Rate
plt.figure()
discount_returns = df.groupby("Discount Percentage")["Return Indicator"].mean().reset_index()
sns.lineplot(data=discount_returns, x="Discount Percentage", y="Return Indicator", marker="o", linewidth=2.5, color="red")
plt.title("Return Rate vs. Discount Applied")
plt.ylabel("Return Rate (%)")
plt.tight_layout()
plt.savefig(f"{images_dir}/discount_vs_return_rate.png")
plt.close()

print("Bivariate analysis plots exported to images/ directory.")

# %% [markdown]
# ## 4. Multivariate Analysis

# %% [code]
# 4.1 Heatmap: Category vs State vs Return Rate
pivot_table = df.pivot_table(values="Return Indicator", index="Category", columns="State", aggfunc="mean")
plt.figure(figsize=(12, 7))
sns.heatmap(pivot_table, annot=True, fmt=".2f", cmap="YlOrRd", cbar_kws={"label": "Return Rate"})
plt.title("Return Rate Heatmap: Category vs State")
plt.tight_layout()
plt.savefig(f"{images_dir}/category_state_returns_heatmap.png")
plt.close()

# 4.2 Correlation Matrix of Numerical Features
numerical_cols = ["Price", "Quantity", "Discount Percentage", "Total Amount", "Delivery Days", "Delivery Delay", "Customer Rating", "Return Indicator", "Reverse Logistics Cost", "Net Financial Impact"]
corr_matrix = df[numerical_cols].corr()
plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm", square=True)
plt.title("Correlation Matrix of Numerical Features")
plt.tight_layout()
plt.savefig(f"{images_dir}/correlation_matrix.png")
plt.close()

print("Multivariate analysis plots exported to images/ directory.")

# %% [markdown]
# ## 5. Advanced Analysis: Cohort & Customer Bracketing

# %% [code]
# 5.1 Bracketing Analysis
# Bracketing is defined as ordering the same Product Name on the same day by the same Customer ID,
# with a return occurring for one or more items.
# Group by Customer, Date, Product Name to identify bracketing events
order_groups = df.groupby(["Customer ID", "Order Date", "Product Name"])

# Filter groups that have size > 1 (bought multiple times/variations on same day)
bracketing_candidates = order_groups.filter(lambda x: len(x) > 1)

# Inside these candidate groups, check if at least one item was returned
bracketed_orders = bracketing_candidates.groupby(["Customer ID", "Order Date", "Product Name"]).filter(
    lambda x: (x["Return Status"] == "Returned").any()
)

print(f"\n--- Bracketing Analysis Summary ---")
print(f"Total rows involved in bracketing behavior: {len(bracketed_orders)}")
print(f"Percentage of total orders that are bracketing-related: {len(bracketed_orders) / len(df) * 100:.2f}%")
print(f"Total loss due to bracketing returns: ${bracketed_orders[bracketed_orders['Return Status']=='Returned']['Total Amount'].sum():,.2f}")

# Plot Return Reasons for Bracketing Orders
plt.figure()
sns.countplot(data=bracketed_orders[bracketed_orders["Return Status"] == "Returned"], x="Category", palette="cool")
plt.title("Bracketing Returns by Category")
plt.tight_layout()
plt.savefig(f"{images_dir}/bracketing_returns_by_category.png")
plt.close()

# 5.2 Serial Returners Cohort Analysis
# Identify chronic returners: Customers with at least 3 orders and a Return Rate > 50%
customer_stats = df.groupby("Customer ID").agg(
    Total_Orders=("Order ID", "count"),
    Returned_Orders=("Return Indicator", "sum"),
    Return_Rate=("Return Indicator", "mean")
).reset_index()

chronic_returners = customer_stats[(customer_stats["Total_Orders"] >= 3) & (customer_stats["Return_Rate"] > 0.50)]
print(f"\n--- Chronic Returners Analysis ---")
print(f"Total number of customers: {len(customer_stats)}")
print(f"Number of chronic returners (Orders >= 3, Return Rate > 50%): {len(chronic_returners)}")
print(f"Chronic returners percentage: {len(chronic_returners) / len(customer_stats) * 100:.2f}%")
print(f"Total returned orders by chronic returners: {chronic_returners['Returned_Orders'].sum()}")
print(f"Percentage of all returned orders caused by chronic returners: {chronic_returners['Returned_Orders'].sum() / df['Return Indicator'].sum() * 100:.2f}%")

# Save chronic returners list for seller/business reference
chronic_returners.to_csv("../data/chronic_returners.csv", index=False)
print("Chronic returners saved to data/chronic_returners.csv")
