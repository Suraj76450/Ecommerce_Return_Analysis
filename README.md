# E-Commerce Return and Refund Analysis: Identifying Root Causes & Business Optimization Opportunities

This is an end-to-end data science and business analytics project designed to diagnose why customers return products in e-commerce, measure the true financial impact, and provide actionable recommendations to reduce return rates and optimize profitability.

---

## 🌟 Project Highlights
1. **Interactive Streamlit Web Dashboard**: Live local dashboard showing KPIs, trends, operational performance, bracketing behavior, and real-time returns prediction.
2. **Machine Learning Predictive pipeline**: A Random Forest classifier that predicts return probabilities based on order profiles, showing feature importances (e.g. logistics delays).
3. **Bracketing & Cohort Analysis**: Identifies bracketing behavior (buying multiple sizes/variations to return the rest) and isolates chronic returner segments.
4. **Reverse Logistics Cost Modeling**: Calculates net profit loss by incorporating flat shipping and restocking overhead on top of refund totals.
5. **Statistical Verification**: Leverages Chi-Square, T-Tests, ANOVA, and Correlation to validate findings mathematically.
6. **Power BI Development Blueprint**: Detailed guide specifying star schema model, relationships, exact DAX formulas, and visual hierarchies.

---

## 📁 Project Structure

```text
Ecommerce_Return_Analysis/
│
├── data/
│   ├── raw_data.csv               # Synthesized raw data (50,000+ orders with anomalies)
│   ├── cleaned_data.csv           # Cleaned transaction data with engineered features
│   ├── chronic_returners.csv      # Customer segment flagged for excessive returns
│   └── return_prediction_pipeline.pkl # Serialized ML model pipeline
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
Navigate to the directory and ensure python is installed.

```bash
cd Ecommerce_Return_Analysis
pip install -r requirements.txt
```

### 2. (Optional) Re-Generate Dataset
The raw data is already generated. If you want to recreate it or change the sample size, run:
```bash
python scripts/generate_data.py
```

### 3. Run Analysis Notebooks
You can open the Jupyter Notebook interface to inspect the analysis:
```bash
jupyter notebook
```
Open and run the notebooks in the `notebooks/` folder in numerical sequence (`01` through `04`).
*(Note: If you run the source python files instead, you can run them from the notebooks directory: `python ../scripts/notebooks_src/01_data_cleaning.py`, etc.)*

### 4. Launch the Interactive Dashboard
To launch the Streamlit app:
```bash
streamlit run dashboard/app.py
```
This will start a local server and open the web dashboard in your browser.

---

## 💡 Key Business Findings
* **The Logistics Delay Trap**: On-time orders show a **17.29%** return rate, which swells to **48.20%** if the order is delayed. Reducing delays is the highest-leverage operational trigger.
* **Apparel Fit Challenge**: Clothing returns are the highest (**41.35%**), primarily caused by "Wrong Size" (55%+). Implementing fit advisory modules is key.
* **Quality Leakage**: Seller E (Budget Imports) exhibits a refund-to-revenue ratio of **41.06%**, heavily driven by "Defective" and "Damaged" products. Quality audits are highly recommended.
* **Chronic Cohorts**: 8.45% of users represent "chronic returners" but generate **14.02%** of all returns.
* **Bracketing Impact**: Bracketing behaviors account for 1.08% of orders and lead to **$114K+** in refund capital drain.

---

## 🛠️ Technology Stack
* **Language**: Python 3.10+
* **Data Processing**: Pandas, NumPy
* **Visualization**: Matplotlib, Seaborn
* **Statistical Analysis**: SciPy (Stats module)
* **Machine Learning**: Scikit-Learn (Logistic Regression, Random Forests, preprocessing pipelines)
* **Dashboarding**: Streamlit (Python Web App), Power BI (DAX, Star Schema)
