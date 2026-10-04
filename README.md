# Cart2Insights: Decoding E-Commerce Performance

An end-to-end e-commerce data analytics project built on the Olist Brazilian
E-Commerce public dataset. Covers data cleaning, SQL database design,
feature engineering, exploratory data analysis, statistical hypothesis
testing, and an interactive Streamlit dashboard.

## Problem Statement

An e-commerce platform generates data across customer orders, products,
sellers, payments, deliveries, and reviews — spread across multiple related
tables. This project analyzes that data to uncover actionable business
insights on sales, customer behavior, seller performance, delivery
operations, and customer satisfaction.

## Business Use Cases

- E-commerce performance monitoring
- Customer behavior & segmentation
- Sales & revenue optimization
- Product & seller performance analysis
- Delivery & operational optimization
- Customer experience improvement
- Data-driven business decision making

## Tech Stack

Python · Pandas · MySQL · SQLAlchemy · SciPy · Matplotlib/Seaborn ·
Plotly · Streamlit

## Project Structure

```
cart2insights/
├── data/
│   ├── raw/                  # Original CSVs (not committed — see .gitignore)
│   └── cleaned/              # Cleaned CSVs, output of notebook 03
├── docs/
│   ├── data_dictionary.md    # Column-level documentation for all 9 tables
│   ├── er_diagram.png        # Entity-relationship diagram
│   └── business_insights.md  # Observation → Interpretation → Business Impact
├── notebooks/
│   ├── 01_data_understanding.ipynb
│   ├── 02_data_quality_analysis.ipynb
│   ├── 03_data_cleaning.ipynb       # Cleans data + loads into MySQL
│   ├── 04_feature_engineering.ipynb # Builds order/customer/seller feature tables
│   ├── 05_eda.ipynb                 # Univariate/bivariate/trend/correlation analysis
│   └── 06_statistical_analysis.ipynb # T-test, ANOVA, Chi-Square
├── sql/
│   └── schema.sql             # Table definitions, PK/FK constraints
├── streamlit/
│   ├── app.py                 # Dashboard entry point
│   ├── database.py            # SQLAlchemy connection + query execution
│   ├── queries.py             # Parameterized SQL for every dashboard section
│   └── utils.py                # Filter-building helpers
├── .env.example                # Template for DB credentials (copy to .env)
├── requirements.txt
└── README.md
```

## Dataset

[Olist Brazilian E-Commerce Public Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
— 9 relational tables covering customers, orders, order items, payments,
reviews, products, sellers, geolocation, and category translations.

See [`docs/data_dictionary.md`](docs/data_dictionary.md) for full column
definitions, keys, and relationships, and the ER diagram below.

![ER Diagram](docs/er_diagram.png)

## Approach

1. **Business understanding** — defined objectives and the questions the analysis should answer
2. **Data understanding** — profiled all 9 tables, built the data dictionary and ER diagram
3. **Data quality analysis** — checked missing values, duplicates, invalid values, PK uniqueness, outliers, orphaned foreign keys
4. **Data cleaning** — handled missing values, standardized text/dates, removed invalid records, deduplicated reviews to one-per-order
5. **SQL storage** — loaded cleaned data into MySQL with enforced PK/FK constraints
6. **Feature engineering** — built `order_features`, `customer_features`, `seller_features` tables using SQL CTEs (order value, delivery delay, customer spending, repeat-customer flag, seller revenue, etc.)
7. **Exploratory data analysis** — univariate, bivariate, multivariate, trend, correlation, and distribution analysis
8. **Statistical analysis** — T-test, ANOVA, and Chi-Square tests, each following hypothesis → test → assumption checks → p-value → decision → business insight
9. **Dashboard** — interactive Streamlit app with full date/state/category filtering across 6 sections
10. **Business insights** — translated every major finding into Observation → Interpretation → Business Impact (see [`docs/business_insights.md`](docs/business_insights.md))

## Key Findings

- **Delivery delay is the strongest driver of dissatisfaction**: on-time orders average 4.29★ vs 2.57★ for delayed orders (Welch's T-test, p < 0.000001)
- **Order value varies significantly by category**: from R$71 (telephony) to R$201 (watches & gifts) — nearly 3x spread (One-Way ANOVA + Kruskal-Wallis, p < 0.000001)
- **Payment method is associated with order outcome**: vouchers show a ~2.4x higher problem-order rate than credit cards (Chi-Square, p < 0.000001)
- **Repeat purchase rate is low** (3.1%), consistent with Olist's multi-seller marketplace structure

Full writeups with interpretation and business impact for each finding: [`docs/business_insights.md`](docs/business_insights.md)

## Dashboard

6 sections, each filterable by order date range, customer state, and
product category: Business Overview, Sales Analysis, Customer Analysis,
Seller & Product Analysis, Delivery Analysis, Customer Experience.

## Setup & Installation

**Prerequisites:** Python 3.10+, MySQL Server 8+, Git

```powershell
git clone <your-repo-url>
cd cart2insights
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Create a MySQL database:

```sql
CREATE DATABASE cart2insights CHARACTER SET utf8mb4;
```

Copy `.env.example` to `.env` and fill in your MySQL credentials:

```
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=cart2insights
```

Download the [Olist dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
and place the 9 CSVs in `data/raw/`.

**Run the pipeline** (in order, from `notebooks/`):

1. `01_data_understanding.ipynb`
2. `02_data_quality_analysis.ipynb`
3. `03_data_cleaning.ipynb` — cleans data and loads it into MySQL
4. `04_feature_engineering.ipynb` — builds feature tables
5. `05_eda.ipynb`
6. `06_statistical_analysis.ipynb`

**Launch the dashboard:**

```powershell
cd streamlit
streamlit run app.py
```

## Statistical Tests Summary

| Test | Question | Result | p-value |
|---|---|---|---|
| Welch's T-Test | Does delivery delay affect review score? | Yes — significant | < 0.000001 |
| One-Way ANOVA | Does order value differ by category? | Yes — significant | < 0.000001 |
| Chi-Square | Is payment method associated with order status? | Yes — significant | < 0.000001 |

## Limitations

- The final month of the dataset shows an apparent revenue drop, most
  likely due to incomplete data coverage at the extraction cutoff, not a
  genuine demand decline.
- `geolocation` zip-prefix linkage to `customers`/`sellers` is logical,
  not enforced as a database constraint, since prefixes repeat across many
  individual addresses.
- 17.9% of expected cells in the Chi-Square test fell below the
  conventional count-5 threshold; the result is still reported given the
  large sample size and strong effect, but is noted as a caveat.

## Author

Yogesh PN