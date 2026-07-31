import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_ecommerce_data(num_orders=50000, seed=42):
    np.random.seed(seed)
    random.seed(seed)

    # 1. Base Product Catalog
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

    # 2. Setup IDs
    customer_ids = [f"CUST-{random.randint(1000, 9999)}" for _ in range(8000)] # 8k customers for 50k orders (repeat buyers)
    order_ids = [f"ORD-{i:06d}" for i in range(100001, 100001 + num_orders)]

    # Generate consistent profiles for customers
    customer_profiles = {}
    for cust_id in customer_ids:
        age = random.randint(18, 70)
        gender = np.random.choice(["Male", "Female", "Other"], p=[0.48, 0.49, 0.03])
        segment = np.random.choice(["Consumer", "Corporate", "Home Office"], p=[0.60, 0.25, 0.15])
        customer_profiles[cust_id] = {
            "Age": age,
            "Gender": gender,
            "Segment": segment
        }

    # 3. Setup Geography
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

    # 4. Warehouses and Sellers
    sellers = ["Seller A (Global Retail)", "Seller B (Direct Electronics)", "Seller C (Fashion Hub)", "Seller D (Home Goods Co)", "Seller E (Budget Imports)"]
    warehouses = ["Warehouse North", "Warehouse South", "Warehouse East", "Warehouse West"]

    data = []

    # Start dates for transaction history (last 2 years)
    start_date = datetime(2024, 1, 1)

    for i in range(num_orders):
        order_id = order_ids[i]
        customer_id = random.choice(customer_ids)
        
        # Get demographic info
        profile = customer_profiles[customer_id]
        customer_age = profile["Age"]
        gender = profile["Gender"]
        segment = profile["Segment"]
        
        # Date distribution: slightly higher volumes during holidays
        days_offset = random.randint(0, 729)
        order_datetime = start_date + timedelta(days=days_offset)
        
        # Select Category and Product
        category = random.choice(list(products.keys()))
        prod_info = random.choice(products[category])
        product_name = prod_info["name"]
        brand = prod_info["brand"]
        base_price = prod_info["price"]
        
        # Quantity distribution (skewed towards 1)
        quantity = np.random.choice([1, 2, 3, 4, 5], p=[0.75, 0.15, 0.06, 0.03, 0.01])
        
        # Discount distribution: mostly no discount, sometimes promotions
        discount = np.random.choice([0.0, 0.1, 0.2, 0.3, 0.4, 0.5], p=[0.50, 0.20, 0.15, 0.08, 0.05, 0.02])
        
        # Calculate Total Amount
        total_amount = round((base_price * quantity) * (1 - discount), 2)
        
        # Location
        state = random.choice(states)
        city = random.choice(geo_data[state])
        
        # Shipping and Delivery
        shipping_type = np.random.choice(["Standard", "Express", "Overnight"], p=[0.70, 0.22, 0.08])
        
        # Delivery delay logic: standard takes 3-10 days, express 1-4, overnight 1-2
        if shipping_type == "Standard":
            expected_days = 5
            # 10% chance of a major shipping delay
            if random.random() < 0.10:
                delivery_days = random.randint(8, 15)
            else:
                delivery_days = random.randint(3, 7)
        elif shipping_type == "Express":
            expected_days = 2
            if random.random() < 0.05:
                delivery_days = random.randint(4, 7)
            else:
                delivery_days = random.randint(1, 3)
        else: # Overnight
            expected_days = 1
            if random.random() < 0.03:
                delivery_days = random.randint(2, 4)
            else:
                delivery_days = 1
                
        # Seller & Warehouse
        # Align clothing to Seller C, electronics to Seller B, others mixed
        if category == "Clothing" and random.random() < 0.70:
            seller = "Seller C (Fashion Hub)"
        elif category == "Electronics" and random.random() < 0.70:
            seller = "Seller B (Direct Electronics)"
        else:
            seller = random.choice(sellers)
            
        warehouse = random.choice(warehouses)
        
        # Customer Rating (mostly high, but delayed orders and bad products get lower)
        # Base rating probabilities
        rating_probs = [0.05, 0.05, 0.15, 0.30, 0.45] # 1, 2, 3, 4, 5 stars
        
        # Adjust rating based on delivery delay
        is_delayed = delivery_days > expected_days
        if is_delayed:
            rating_probs = [0.25, 0.25, 0.25, 0.15, 0.10]
            
        # Adjust based on Seller E (Budget Imports has lower quality)
        if seller == "Seller E (Budget Imports)":
            rating_probs = [0.15, 0.20, 0.25, 0.25, 0.15]
            
        customer_rating = np.random.choice([1, 2, 3, 4, 5], p=rating_probs)
        
        # RETURN LOGIC (CORRELATIONS)
        # Base return probability
        return_prob = 0.05
        
        # Category influence
        if category == "Clothing":
            return_prob += 0.15  # Sizing issue is huge in clothing
        elif category == "Electronics":
            return_prob += 0.08  # Tech issues / buyer remorse
        elif category == "Books":
            return_prob -= 0.03  # Books rarely get returned
            
        # Shipping delay influence
        if is_delayed:
            return_prob += 0.12  # Customer got it late, might not need it anymore
            
        # Discount influence (impulse buying with high discounts leads to returns)
        if discount >= 0.40:
            return_prob += 0.10
            
        # Rating influence (strongest correlation)
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
            
        # Seller influence
        if seller == "Seller E (Budget Imports)":
            return_prob += 0.08
            
        # Clip probability between 0 and 0.95
        return_prob = max(0.01, min(0.95, return_prob))
        
        # Determine Return Status
        if random.random() < return_prob:
            return_status = "Returned"
            
            # Select Return Reason
            reasons = ["Changed Mind", "Wrong Size", "Damaged", "Defective", "Not as Described", "Late Delivery"]
            weights = [0.2, 0.2, 0.15, 0.15, 0.2, 0.1]
            
            # Adjust weights based on situation
            if category == "Clothing":
                # Clothing heavily returned due to sizing
                reasons = ["Wrong Size", "Not as Described", "Changed Mind", "Damaged", "Defective", "Late Delivery"]
                weights = [0.55, 0.15, 0.15, 0.05, 0.05, 0.05]
            elif is_delayed and random.random() < 0.60:
                # High chance reason is Late Delivery if it was delayed
                reasons = ["Late Delivery", "Changed Mind", "Not as Described", "Damaged", "Defective", "Wrong Size"]
                weights = [0.60, 0.15, 0.10, 0.05, 0.05, 0.05]
            elif customer_rating in [1, 2]:
                # Low ratings return due to defective or damaged
                reasons = ["Defective", "Damaged", "Not as Described", "Changed Mind", "Wrong Size", "Late Delivery"]
                weights = [0.40, 0.30, 0.20, 0.05, 0.03, 0.02]
                
            return_reason = np.random.choice(reasons, p=weights)
            refund_amount = total_amount
        else:
            return_status = "Not Returned"
            return_reason = None
            refund_amount = 0.0

        # Save order info
        data.append({
            "Order ID": order_id,
            "Customer ID": customer_id,
            "Customer Age": customer_age,
            "Gender": gender,
            "Segment": segment,
            "Order Date": order_datetime,
            "Product Name": product_name,
            "Category": category,
            "Brand": brand,
            "Quantity": quantity,
            "Price": base_price,
            "Discount": discount,
            "Total Amount": total_amount,
            "State": state,
            "City": city,
            "Seller": seller,
            "Delivery Days": delivery_days,
            "Shipping Type": shipping_type,
            "Return Status": return_status,
            "Return Reason": return_reason,
            "Refund Amount": refund_amount,
            "Customer Rating": customer_rating,
            "Warehouse": warehouse
        })

    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Simulate Bracketing (Serial Returns Cohort)
    bracketing_customers = list(set(df["Customer ID"].sample(500, random_state=42)))
    bracketing_rows = []
    
    for cust in bracketing_customers:
        cust_rows = df[df["Customer ID"] == cust]
        if len(cust_rows) == 0:
            continue
        base_row = cust_rows.iloc[0].copy()
        
        if base_row["Category"] == "Clothing":
            p_name = base_row["Product Name"]
            o_date = base_row["Order Date"]
            
            for suffix in ["-B1", "-B2"]:
                new_row = base_row.copy()
                new_row["Order ID"] = base_row["Order ID"] + suffix
                new_row["Quantity"] = 1
                new_row["Discount"] = base_row["Discount"]
                new_row["Total Amount"] = round(new_row["Price"] * (1 - new_row["Discount"]), 2)
                new_row["Return Status"] = "Returned"
                new_row["Return Reason"] = "Wrong Size"
                new_row["Refund Amount"] = new_row["Total Amount"]
                new_row["Customer Rating"] = 4
                bracketing_rows.append(new_row)
                
    if bracketing_rows:
        df = pd.concat([df, pd.DataFrame(bracketing_rows)], ignore_index=True)

    # 5. INJECT ANOMALIES (Dirty Data)
    
    # 5.1 Duplicates (1.5%)
    dup_indices = np.random.choice(df.index, size=int(len(df) * 0.015), replace=False)
    dups = df.loc[dup_indices].copy()
    df = pd.concat([df, dups], ignore_index=True)
    
    # 5.2 Missing values
    # Nulls in rating (2.5%)
    rating_null_indices = np.random.choice(df.index, size=int(len(df) * 0.025), replace=False)
    df.loc[rating_null_indices, "Customer Rating"] = np.nan
    
    # Nulls in Shipping Type (1%)
    ship_null_indices = np.random.choice(df.index, size=int(len(df) * 0.01), replace=False)
    df.loc[ship_null_indices, "Shipping Type"] = np.nan
    
    # Incomplete logs: returned but missing reason (1.5% of returned)
    returned_indices = df[df["Return Status"] == "Returned"].index
    missing_reason_indices = np.random.choice(returned_indices, size=int(len(returned_indices) * 0.015), replace=False)
    df.loc[missing_reason_indices, "Return Reason"] = np.nan
    
    # Nulls in State / City (0.5%)
    geo_null_indices = np.random.choice(df.index, size=int(len(df) * 0.005), replace=False)
    df.loc[geo_null_indices, "State"] = np.nan
    df.loc[geo_null_indices, "City"] = np.nan

    # 5.3 Incorrect types/formats
    # Price formatted as string with '$' (4% of rows)
    df["Price"] = df["Price"].astype(object)
    price_str_indices = np.random.choice(df.index, size=int(len(df) * 0.04), replace=False)
    df.loc[price_str_indices, "Price"] = df.loc[price_str_indices, "Price"].apply(lambda x: f"${x:,.2f}")
    
    # Mixed Date formats
    date_str_indices1 = np.random.choice(df.index, size=int(len(df) * 0.3), replace=False)
    date_str_indices2 = np.random.choice(list(set(df.index) - set(date_str_indices1)), size=int(len(df) * 0.2), replace=False)
    
    df["Order Date"] = df["Order Date"].astype(object)
    df.loc[date_str_indices1, "Order Date"] = df.loc[date_str_indices1, "Order Date"].apply(lambda d: d.strftime("%m/%d/%Y"))
    df.loc[date_str_indices2, "Order Date"] = df.loc[date_str_indices2, "Order Date"].apply(lambda d: d.strftime("%d-%b-%Y"))
    df.loc[df["Order Date"].apply(lambda d: isinstance(d, datetime)), "Order Date"] = df.loc[df["Order Date"].apply(lambda d: isinstance(d, datetime)), "Order Date"].apply(lambda d: d.strftime("%Y-%m-%d"))

    # 5.4 Impossible values
    neg_price_indices = np.random.choice(df.index, size=20, replace=False)
    df.loc[neg_price_indices, "Price"] = -49.90
    
    zero_qty_indices = np.random.choice(df.index, size=15, replace=False)
    df.loc[zero_qty_indices, "Quantity"] = np.random.choice([0, -1, -2], size=15)
    
    neg_delivery_indices = np.random.choice(df.index, size=25, replace=False)
    df.loc[neg_delivery_indices, "Delivery Days"] = -3
    
    # 5.5 Outliers
    outlier_qty_indices = np.random.choice(df.index, size=5, replace=False)
    df.loc[outlier_qty_indices, "Quantity"] = 500
    df.loc[outlier_qty_indices, "Total Amount"] = df.loc[outlier_qty_indices, "Price"].apply(lambda x: float(str(x).replace('$','')) if isinstance(x, str) else x) * 500
    
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    return df

if __name__ == "__main__":
    print("Generating e-commerce returns dataset with customer profiles...")
    df = generate_ecommerce_data(num_orders=50000)
    
    os.makedirs("data", exist_ok=True)
    output_path = os.path.join("data", "raw_data.csv")
    df.to_csv(output_path, index=False)
    print(f"Dataset successfully created and saved to {output_path}!")
    print(f"Total Rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")
