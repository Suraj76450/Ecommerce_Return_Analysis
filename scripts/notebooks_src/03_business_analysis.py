# %% [markdown]
# # Phase 3: Business Questions & Statistical Analysis
# This notebook answers the specific business questions defined in the project scope and performs descriptive and inferential statistical analysis.
# 
# ### Statistical Tests:
# 1. **Chi-Square Test of Independence**: Is there a significant relationship between Product Category and Return Status?
# 2. **Two-Sample T-Test**: Do delayed orders have a significantly higher return rate compared to on-time orders?
# 3. **ANOVA (Analysis of Variance)**: Are the mean refund amounts significantly different across different Brands?
# 4. **Correlation Analysis**: What is the correlation between Discount level and Return Status?

# %% [code]
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

# Set plotting style
sns.set_theme(style="whitegrid")

# Paths
input_path = "../data/cleaned_data.csv"
df = pd.read_csv(input_path)

# Ensure date is parsed
df["Order Date"] = pd.to_datetime(df["Order Date"])

# %% [markdown]
# ## 1. Financial KPIs
# We start by calculating the overall high-level business indicators.

# %% [code]
total_orders = len(df)
returned_orders = df[df["Return Status"] == "Returned"].shape[0]
return_rate = (returned_orders / total_orders) * 100

gross_revenue = df["Total Amount"].sum()
total_refunds = df["Refund Amount"].sum()
total_logistics_cost = df["Reverse Logistics Cost"].sum()
net_profit_loss = df["Profit Loss"].sum()

avg_delivery_time = df["Delivery Days"].mean()
avg_rating = df["Customer Rating"].mean()
avg_order_value = df["Total Amount"].mean()
avg_refund_per_return = df[df["Return Status"] == "Returned"]["Refund Amount"].mean()

print("=== E-Commerce Returns KPIs ===")
print(f"Total Orders:                  {total_orders:,}")
print(f"Total Returned Orders:         {returned_orders:,}")
print(f"Return Rate (%):               {return_rate:.2f}%")
print(f"Total Gross Revenue:          ${gross_revenue:,.2f}")
print(f"Total Refunded Amount:        ${total_refunds:,.2f}")
print(f"Total Reverse Logistics Costs: ${total_logistics_cost:,.2f}")
print(f"Net Profit Loss from Returns:  ${net_profit_loss:,.2f}")
print(f"Average Delivery Time (Days):  {avg_delivery_time:.2f}")
print(f"Average Customer Rating:       {avg_rating:.2f} / 5.0")
print(f"Average Order Value (AOV):     ${avg_order_value:,.2f}")
print(f"Average Refund per Return:     ${avg_refund_per_return:,.2f}")

# %% [markdown]
# ## 2. Product Analysis

# %% [code]
# 2.1 Category with the highest return rate
category_stats = df.groupby("Category").agg(
    Total_Orders=("Order ID", "count"),
    Returned_Orders=("Return Indicator", "sum"),
    Return_Rate=("Return Indicator", "mean")
).reset_index()
category_stats["Return_Rate"] *= 100
category_stats = category_stats.sort_values(by="Return_Rate", ascending=False)
print("--- Return Rate by Category ---")
print(category_stats.to_string(index=False))

# 2.2 Top 5 returned products (absolute volume)
top_returned_products = df[df["Return Status"] == "Returned"]["Product Name"].value_counts().head(5)
print("\n--- Top 5 Returned Products ---")
print(top_returned_products)

# 2.3 Top 5 brands by refund amount
brand_refunds = df.groupby("Brand")["Refund Amount"].sum().reset_index().sort_values(by="Refund Amount", ascending=False).head(5)
print("\n--- Top 5 Brands by Total Refund ---")
print(brand_refunds.to_string(index=False))

# 2.4 Return rate by price range
# Define price bins
price_bins = [0, 20, 50, 100, 200, 500, 10000]
price_labels = ["$0-$20", "$20-$50", "$50-$100", "$100-$200", "$200-$500", "$500+"]
df["Price Range"] = pd.cut(df["Price"], bins=price_bins, labels=price_labels)

price_stats = df.groupby("Price Range", observed=False).agg(
    Total_Orders=("Order ID", "count"),
    Return_Rate=("Return Indicator", "mean")
).reset_index()
price_stats["Return_Rate"] *= 100
print("\n--- Return Rate by Price Range ---")
print(price_stats.to_string(index=False))

# %% [markdown]
# ## 3. Customer Analysis

# %% [code]
# 3.1 Return rate by Customer Age Group
age_bins = [18, 25, 35, 45, 55, 75]
age_labels = ["18-25", "26-35", "36-45", "46-55", "56+"]
df["Age Group"] = pd.cut(df["Customer Age"], bins=age_bins, labels=age_labels)

age_stats = df.groupby("Age Group", observed=False).agg(
    Total_Orders=("Order ID", "count"),
    Return_Rate=("Return Indicator", "mean")
).reset_index()
age_stats["Return_Rate"] *= 100
print("--- Return Rate by Age Group ---")
print(age_stats.to_string(index=False))

# 3.2 Return rate by Gender
gender_stats = df.groupby("Gender").agg(
    Total_Orders=("Order ID", "count"),
    Return_Rate=("Return Indicator", "mean")
).reset_index()
gender_stats["Return_Rate"] *= 100
print("\n--- Return Rate by Gender ---")
print(gender_stats.to_string(index=False))

# 3.3 Return rate by Customer Segment
segment_stats = df.groupby("Segment").agg(
    Total_Orders=("Order ID", "count"),
    Return_Rate=("Return Indicator", "mean")
).reset_index()
segment_stats["Return_Rate"] *= 100
print("\n--- Return Rate by Customer Segment ---")
print(segment_stats.to_string(index=False))

# 3.4 Repeat Customers vs. One-time Customers Return Rate
cust_orders = df.groupby("Customer ID")["Order ID"].count().reset_index()
cust_orders.columns = ["Customer ID", "Order Count"]
df = df.merge(cust_orders, on="Customer ID", how="left")
df["Customer Type"] = np.where(df["Order Count"] > 1, "Repeat Customer", "One-Time Customer")

repeat_stats = df.groupby("Customer Type").agg(
    Total_Orders=("Order ID", "count"),
    Return_Rate=("Return Indicator", "mean")
).reset_index()
repeat_stats["Return_Rate"] *= 100
print("\n--- Return Rate by Customer Type ---")
print(repeat_stats.to_string(index=False))

# %% [markdown]
# ## 4. Time Analysis

# %% [code]
# 4.1 Return count and rate by month
df["Month_Name"] = df["Order Date"].dt.strftime("%B")
month_stats = df.groupby("Month_Name").agg(
    Total_Orders=("Order ID", "count"),
    Returns=("Return Indicator", "sum"),
    Return_Rate=("Return Indicator", "mean")
).reindex(["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
month_stats["Return_Rate"] *= 100
print("--- Return Stats by Month ---")
print(month_stats.reset_index())

# 4.2 Returns by day of the week
day_stats = df.groupby("Weekday").agg(
    Total_Orders=("Order ID", "count"),
    Returns=("Return Indicator", "sum"),
    Return_Rate=("Return Indicator", "mean")
).reindex(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
day_stats["Return_Rate"] *= 100
print("\n--- Return Stats by Day of Week ---")
print(day_stats.reset_index())

# %% [markdown]
# ## 5. Geographic Analysis

# %% [code]
# 5.1 Return rate by State
state_stats = df.groupby("State").agg(
    Total_Orders=("Order ID", "count"),
    Return_Rate=("Return Indicator", "mean")
).reset_index().sort_values(by="Return_Rate", ascending=False)
state_stats["Return_Rate"] *= 100
print("--- Return Rate by State (Top 5) ---")
print(state_stats.head(5).to_string(index=False))

# 5.2 Cities with the highest refund amount
city_refunds = df.groupby(["City", "State"])["Refund Amount"].sum().reset_index().sort_values(by="Refund Amount", ascending=False)
print("\n--- Top 5 Cities by Total Refund Amount ---")
print(city_refunds.head(5).to_string(index=False))

# %% [markdown]
# ## 6. Delivery & Shipping Analysis

# %% [code]
# 6.1 Does delayed delivery increase returns?
df["Is Delayed"] = df["Delivery Delay"] > 0
delay_stats = df.groupby("Is Delayed").agg(
    Total_Orders=("Order ID", "count"),
    Return_Rate=("Return Indicator", "mean")
).reset_index()
delay_stats["Return_Rate"] *= 100
print("--- Return Rate: Delayed vs. On-Time ---")
print(delay_stats.to_string(index=False))

# 6.2 Return rate by shipping type
shipping_stats = df.groupby("Shipping Type").agg(
    Total_Orders=("Order ID", "count"),
    Return_Rate=("Return Indicator", "mean")
).reset_index().sort_values(by="Return_Rate", ascending=False)
shipping_stats["Return_Rate"] *= 100
print("\n--- Return Rate by Shipping Type ---")
print(shipping_stats.to_string(index=False))

# %% [markdown]
# ## 7. Seller & Warehouse Analysis

# %% [code]
# 7.1 Refund percentage by Seller
seller_stats = df.groupby("Seller").agg(
    Total_Revenue=("Total Amount", "sum"),
    Total_Refunds=("Refund Amount", "sum")
).reset_index()
seller_stats["Refund Percentage"] = (seller_stats["Total_Refunds"] / seller_stats["Total_Revenue"]) * 100
seller_stats = seller_stats.sort_values(by="Refund Percentage", ascending=False)
print("--- Refund Percentage by Seller ---")
print(seller_stats.to_string(index=False))

# 7.2 Warehouse generating the most returned products
warehouse_stats = df.groupby("Warehouse").agg(
    Total_Orders=("Order ID", "count"),
    Returned_Orders=("Return Indicator", "sum"),
    Return_Rate=("Return Indicator", "mean")
).reset_index().sort_values(by="Returned_Orders", ascending=False)
warehouse_stats["Return_Rate"] *= 100
print("\n--- Returns by Warehouse ---")
print(warehouse_stats.to_string(index=False))

# %% [markdown]
# ## 8. Statistical Inference & Hypothesis Testing

# %% [code]
# 8.1 Chi-Square Test of Independence: Category vs. Return Status
print("=== Hypothesis Test 1: Chi-Square Test ===")
print("Null Hypothesis (H0): Return Status is independent of Product Category.")
print("Alternative Hypothesis (H1): Return Status is dependent on Product Category.")

contingency_table = pd.crosstab(df["Category"], df["Return Status"])
chi2, p_val, dof, expected = stats.chi2_contingency(contingency_table)

print(f"Chi-square statistic: {chi2:.4f}")
print(f"p-value:              {p_val:.4e}")

if p_val < 0.05:
    print("Result: Reject H0. There is a statistically significant relationship between Product Category and Return Status.")
else:
    print("Result: Fail to reject H0. Return Status is independent of Category.")

# 8.2 Two-Sample T-Test: Return rates for Delayed vs. On-Time Delivery
print("\n=== Hypothesis Test 2: Two-Sample T-Test ===")
print("Null Hypothesis (H0): There is no difference in the return rates of delayed and on-time shipments.")
print("Alternative Hypothesis (H1): Delayed shipments have a different return rate than on-time shipments.")

delayed_returns = df[df["Is Delayed"] == True]["Return Indicator"]
ontime_returns = df[df["Is Delayed"] == False]["Return Indicator"]

t_stat, p_val = stats.ttest_ind(delayed_returns, ontime_returns, equal_var=False)

print(f"T-statistic: {t_stat:.4f}")
print(f"p-value:     {p_val:.4e}")

if p_val < 0.05:
    print("Result: Reject H0. Delayed shipments have a statistically significant difference in return rates compared to on-time shipments.")
else:
    print("Result: Fail to reject H0. No significant difference in return rates.")

# 8.3 ANOVA (One-way): Refund Amounts across different Brands
print("\n=== Hypothesis Test 3: One-Way ANOVA ===")
print("Null Hypothesis (H0): Mean refund amounts are identical across all brands.")
print("Alternative Hypothesis (H1): At least one brand has a different mean refund amount.")

# Get returned items only
returned_items = df[df["Return Status"] == "Returned"]
brands = returned_items["Brand"].unique()

# Group refund amounts by brand
brand_groups = [returned_items[returned_items["Brand"] == brand]["Refund Amount"] for brand in brands]

f_stat, p_val = stats.f_oneway(*brand_groups)

print(f"F-statistic: {f_stat:.4f}")
print(f"p-value:     {p_val:.4e}")

if p_val < 0.05:
    print("Result: Reject H0. There is a statistically significant difference in mean refund amounts across different brands.")
else:
    print("Result: Fail to reject H0. No significant difference in mean refund amounts.")

# 8.4 Correlation Analysis: Discount levels vs Return Status
print("\n=== Hypothesis Test 4: Pearson Correlation ===")
corr, p_val = stats.pearsonr(df["Discount"], df["Return Indicator"])
print(f"Pearson Correlation Coefficient: {corr:.4f}")
print(f"p-value:                         {p_val:.4e}")

if p_val < 0.05:
    print("Result: The correlation is statistically significant.")
else:
    print("Result: The correlation is not statistically significant.")
