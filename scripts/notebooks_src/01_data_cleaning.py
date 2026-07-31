# %% [markdown]
# # Phase 1: Data Cleaning - E-Commerce Return & Refund Analysis
# This notebook handles the importing, profiling, cleaning, and preparation of the raw transactional dataset.
# 
# ### Tasks:
# 1. Load the raw dataset and inspect its structure, data types, and initial anomalies.
# 2. Remove duplicate records.
# 3. Clean and standardize invalid data types (e.g. converting formatted prices to floats).
# 4. Handle impossible/invalid values (e.g. negative prices, quantities, and delivery days).
# 5. Impute or flag missing values appropriately.
# 6. Recalculate derivative columns (e.g. `Total Amount` and `Refund Amount`) to ensure calculations are correct.
# 7. Export the cleaned dataset to `data/cleaned_data.csv`.

# %% [code]
import os
import numpy as np
import pandas as pd

# Define paths relative to the notebooks folder
raw_data_path = "../data/raw_data.csv"
cleaned_data_path = "../data/cleaned_data.csv"

# %% [markdown]
# ## 1. Load Raw Data and Initial Inspection

# %% [code]
# Load the raw dataset
print("Loading raw data...")
df = pd.read_csv(raw_data_path)

# Display general info
print("\n--- Dataset Info ---")
df.info()

# Print first few rows
print("\n--- First 5 Rows ---")
print(df.head())

# Print total null values per column
print("\n--- Missing Values count ---")
print(df.isnull().sum())

# %% [markdown]
# ## 2. Handle Duplicate Records

# %% [code]
# Check for duplicate rows
duplicates_count = df.duplicated().sum()
print(f"Number of duplicate rows identified: {duplicates_count}")

# Drop duplicates
if duplicates_count > 0:
    df = df.drop_duplicates()
    print(f"Duplicates removed. New dataset shape: {df.shape}")

# %% [markdown]
# ## 3. Clean and Fix Data Types
# We need to clean the `Price` column (which contains `$` symbols in some rows) and the `Order Date` column (which contains mixed string formats).

# %% [code]
# Clean Price Column
# Inspect a sample of prices that are strings
print("Sample prices before cleaning:")
print(df["Price"].sample(10, random_state=42))

# Remove currency symbol '$' and commas, and cast to float
df["Price"] = df["Price"].astype(str).str.replace("$", "", regex=False).str.replace(",", "", regex=False)
df["Price"] = pd.to_numeric(df["Price"], errors="coerce")

print("\nSample prices after cleaning:")
print(df["Price"].sample(5, random_state=42))

# %% [code]
# Clean Order Date Column
# Show a sample of date formats
print("Sample order dates before cleaning:")
print(df["Order Date"].sample(10, random_state=42))

# Convert to datetime using format='mixed' to handle MM/DD/YYYY, YYYY-MM-DD and DD-MMM-YYYY formats
df["Order Date"] = pd.to_datetime(df["Order Date"], format="mixed", errors="coerce")

print("\nSample order dates after cleaning:")
print(df["Order Date"].sample(5, random_state=42))

# Verify if any date conversions failed
failed_dates = df["Order Date"].isnull().sum()
print(f"Number of failed date conversions: {failed_dates}")
if failed_dates > 0:
    # Drop rows with invalid dates since Order Date is a key field
    df = df.dropna(subset=["Order Date"])
    print(f"Removed rows with invalid dates. New shape: {df.shape}")

# %% [markdown]
# ## 4. Clean Impossible / Invalid Values
# We need to address:
# - Negative values in `Price`, `Quantity`, and `Delivery Days`.
# - Quantity values of zero.

# %% [code]
# Address negative prices
neg_price_count = (df["Price"] < 0).sum()
print(f"Orders with negative prices: {neg_price_count}")

if neg_price_count > 0:
    # Set negative prices to absolute values (assuming it's a negative sign error)
    df["Price"] = df["Price"].abs()
    print("Negative prices corrected using absolute values.")

# Address zero or negative quantities
invalid_qty_count = (df["Quantity"] <= 0).sum()
print(f"Orders with zero or negative quantities: {invalid_qty_count}")

if invalid_qty_count > 0:
    # Set zero or negative quantities to 1 (most logical value for a transaction)
    df.loc[df["Quantity"] <= 0, "Quantity"] = 1
    print("Zero or negative quantities reset to 1.")

# Address negative delivery days
neg_delivery_count = (df["Delivery Days"] < 0).sum()
print(f"Orders with negative delivery days: {neg_delivery_count}")

if neg_delivery_count > 0:
    # Take the absolute value for negative delivery days
    df["Delivery Days"] = df["Delivery Days"].abs()
    print("Negative delivery days corrected using absolute values.")

# %% [markdown]
# ## 5. Handle Missing Values (Imputation)
# Let's inspect missing values in remaining columns and handle them systematically:
# - `Customer Rating`: Fill with the median rating of the product's category.
# - `Shipping Type`: Fill with the mode ("Standard").
# - `State` and `City`: Fill with "Unknown State" and "Unknown City".
# - `Return Reason`:
#   - If return status is 'Returned' but reason is missing, set to 'Not Specified'.
#   - If return status is 'Not Returned', ensure the reason is NaN.

# %% [code]
# Impute Customer Rating
print("Customer Rating missing values:", df["Customer Rating"].isnull().sum())
# Impute using category-wise median rating
df["Customer Rating"] = df["Customer Rating"].fillna(
    df.groupby("Category")["Customer Rating"].transform("median")
)
print("Customer Rating missing values after imputation:", df["Customer Rating"].isnull().sum())

# Impute Shipping Type
print("Shipping Type missing values:", df["Shipping Type"].isnull().sum())
shipping_mode = df["Shipping Type"].mode()[0]
df["Shipping Type"] = df["Shipping Type"].fillna(shipping_mode)
print("Shipping Type missing values after imputation:", df["Shipping Type"].isnull().sum())

# Impute State and City
print("State missing values:", df["State"].isnull().sum())
print("City missing values:", df["City"].isnull().sum())
df["State"] = df["State"].fillna("Unknown State")
df["City"] = df["City"].fillna("Unknown City")

# Fix Return Reason and Refund Amount based on Return Status
print("\nFixing Return Reason and Refund Amount logical consistency...")
# Case 1: Returned but missing reason -> "Not Specified"
df.loc[(df["Return Status"] == "Returned") & (df["Return Reason"].isna()), "Return Reason"] = "Not Specified"

# Case 2: Not Returned -> Return Reason must be NaN and Refund Amount must be 0.0
df.loc[df["Return Status"] == "Not Returned", "Return Reason"] = np.nan
df.loc[df["Return Status"] == "Not Returned", "Refund Amount"] = 0.0

print("Missing values count after imputation:")
print(df.isnull().sum())

# %% [markdown]
# ## 6. Recalculate Total and Refund Amounts
# To guarantee consistency, we recalculate `Total Amount` as `Price * Quantity * (1 - Discount)` and verify that `Refund Amount` equals the `Total Amount` for returned orders.

# %% [code]
# Recalculate Total Amount
df["Total Amount"] = (df["Price"] * df["Quantity"] * (1 - df["Discount"])).round(2)

# Verify Refund Amount for Returned items equals the Recalculated Total Amount
returned_mask = df["Return Status"] == "Returned"
df.loc[returned_mask, "Refund Amount"] = df.loc[returned_mask, "Total Amount"]

# For non-returned items, refund must be 0
df.loc[~returned_mask, "Refund Amount"] = 0.0

print("Recalculations completed. Sample of returned items:")
print(df[returned_mask][["Order ID", "Quantity", "Price", "Discount", "Total Amount", "Refund Amount"]].head())

# %% [markdown]
# ## 7. Export Cleaned Data
# We verify the final shape and data schema, then write to `data/cleaned_data.csv`.

# %% [code]
# Inspect final clean dataset
print("Cleaned Dataset Shape:", df.shape)
print("\n--- Cleaned Dataset Sample ---")
print(df.head())

# Save to CSV
os.makedirs(os.path.dirname(cleaned_data_path), exist_ok=True)
df.to_csv(cleaned_data_path, index=False)
print(f"\nCleaned dataset successfully exported to {cleaned_data_path}!")
