# %% [markdown]
# # Phase 4: Predictive returns modeling (Machine Learning)
# This notebook builds a machine learning classification model to predict whether a customer will return a purchased product.
# 
# ### Tasks:
# 1. Prepare features and encode categorical variables.
# 2. Split data into training and test sets.
# 3. Train a baseline Logistic Regression model and a Random Forest Classifier.
# 4. Evaluate performance using confusion matrices, classification reports, and ROC-AUC scores.
# 5. Extract and visualize feature importances to identify key drivers of product returns.
# 6. Save the trained model pipeline for use in the interactive Streamlit dashboard.

# %% [code]
import os
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve

# Paths
input_path = "../data/cleaned_data.csv"
model_dir = "../dashboard"
os.makedirs(model_dir, exist_ok=True)
images_dir = "../images"

# Load cleaned data
df = pd.read_csv(input_path)

# %% [markdown]
# ## 1. Feature Preparation & Selection
# We will use transaction-level and customer-level features to predict the `Return Indicator`.

# %% [code]
# Define features and target
features = [
    "Category", "Brand", "Shipping Type", "Seller", "Segment", "Gender",
    "Price", "Quantity", "Discount", "Delivery Days", "Customer Age"
]
target = "Return Indicator"

X = df[features]
y = df[target]

print("Features selected:")
print(features)
print("\nTarget shape:", y.shape)

# Identify numerical and categorical columns
num_features = ["Price", "Quantity", "Discount", "Delivery Days", "Customer Age"]
cat_features = ["Category", "Brand", "Shipping Type", "Seller", "Segment", "Gender"]

# Split data into train and test sets (80/20 split)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)

print(f"\nTrain set shape: {X_train.shape}")
print(f"Test set shape:  {X_test.shape}")

# %% [markdown]
# ## 2. Preprocessing & Pipeline Construction
# We use a `ColumnTransformer` to scale numerical features and one-hot encode categorical features.

# %% [code]
# Define preprocessor
preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), num_features),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_features)
    ]
)

# Create preprocessed datasets to inspect shape
X_train_preprocessed = preprocessor.fit_transform(X_train)
cat_encoder = preprocessor.named_transformers_["cat"]
encoded_cat_names = cat_encoder.get_feature_names_out(cat_features)
all_feature_names = num_features + list(encoded_cat_names)

print(f"Number of features after encoding: {len(all_feature_names)}")

# %% [markdown]
# ## 3. Train Models
# We compare a linear model (Logistic Regression) with a tree-based ensemble (Random Forest).

# %% [code]
# 3.1 Logistic Regression Pipeline
lr_pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("classifier", LogisticRegression(max_iter=1000, random_state=42))
    ]
)

print("Training Logistic Regression Model...")
lr_pipeline.fit(X_train, y_train)

# 3.2 Random Forest Pipeline
rf_pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1))
    ]
)

print("Training Random Forest Model...")
rf_pipeline.fit(X_train, y_train)

# %% [markdown]
# ## 4. Model Evaluation

# %% [code]
# Helper function to evaluate model
def evaluate_model(model, name, X_test, y_test):
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    
    print(f"\n=== {name} Classification Report ===")
    print(classification_report(y_test, y_pred))
    
    auc = roc_auc_score(y_test, y_prob)
    print(f"ROC-AUC Score: {auc:.4f}")
    
    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(6, 4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False)
    plt.title(f"{name} Confusion Matrix")
    plt.ylabel("Actual")
    plt.xlabel("Predicted")
    plt.tight_layout()
    plt.savefig(f"{images_dir}/{name.lower().replace(' ', '_')}_confusion_matrix.png")
    plt.close()

evaluate_model(lr_pipeline, "Logistic Regression", X_test, y_test)
evaluate_model(rf_pipeline, "Random Forest", X_test, y_test)

# Plot ROC Curves
plt.figure()
for model, name in [(lr_pipeline, "Logistic Regression"), (rf_pipeline, "Random Forest")]:
    y_prob = model.predict_proba(X_test)[:, 1]
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    auc = roc_auc_score(y_test, y_prob)
    plt.plot(fpr, tpr, label=f"{name} (AUC = {auc:.3f})")

plt.plot([0, 1], [0, 1], "k--", label="Random Guess")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curves Comparison")
plt.legend(loc="lower right")
plt.tight_layout()
plt.savefig(f"{images_dir}/roc_curves_comparison.png")
plt.close()

# %% [markdown]
# ## 5. Feature Importances
# We extract feature importances from the Random Forest model to determine what variables drive returns the most.

# %% [code]
# Extract feature importances
importances = rf_pipeline.named_steps["classifier"].feature_importances_

# Map to names
feat_importances = pd.Series(importances, index=all_feature_names)
top_feats = feat_importances.sort_values(ascending=False).head(15)

plt.figure(figsize=(10, 6))
sns.barplot(x=top_feats.values, y=top_feats.index, palette="viridis")
plt.title("Top 15 Feature Importances (Random Forest)")
plt.xlabel("Relative Importance Score")
plt.tight_layout()
plt.savefig(f"{images_dir}/feature_importances.png")
plt.close()

print("\nTop 10 Feature Importances:")
print(top_feats.head(10))

# %% [markdown]
# ## 6. Save Model for Dashboard Integration
# We save the trained Random Forest pipeline using `pickle`. Since the pipeline contains both the `preprocessor` and the `classifier`, we can pass raw Pandas dataframes directly into `model.predict()` in the Streamlit app.

# %% [code]
# Save the pipeline
model_file_path = os.path.join(model_dir, "return_prediction_pipeline.pkl")
with open(model_file_path, "wb") as f:
    pickle.dump(rf_pipeline, f)

print(f"\nModel pipeline successfully serialized and saved to {model_file_path}!")
