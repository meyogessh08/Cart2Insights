import streamlit as st
from database import run_query_filtered

ORDERS_CTE = """
WITH filtered_orders AS (
    SELECT o.order_id, o.customer_id, o.order_status, o.order_purchase_timestamp,
           o.order_delivered_customer_date, o.order_estimated_delivery_date,
           c.customer_state, c.customer_unique_id, c.customer_city
    FROM orders o
    JOIN customers c ON c.customer_id = o.customer_id
    WHERE o.order_purchase_timestamp BETWEEN :start_date AND :end_date
      AND (:use_state = 0 OR c.customer_state IN :states)
)
"""

ITEMS_CTE = ORDERS_CTE + """,
filtered_items AS (
    SELECT oi.order_id, oi.product_id, oi.seller_id, oi.price, oi.freight_value,
           t.product_category_name_english AS category
    FROM order_items oi
    JOIN filtered_orders fo ON fo.order_id = oi.order_id
    JOIN products p ON p.product_id = oi.product_id
    LEFT JOIN product_category_translation t ON t.product_category_name = p.product_category_name
    WHERE (:use_cat = 0 OR t.product_category_name_english IN :categories)
)
"""

ORDERS_PARAMS = ["states"]
ITEMS_PARAMS = ["states", "categories"]

@st.cache_data(ttl=600, show_spinner=False)
def order_status_breakdown(p):
    sql = ORDERS_CTE + """
    SELECT order_status, COUNT(*) AS n
    FROM filtered_orders GROUP BY order_status ORDER BY n DESC
    """
    return run_query_filtered(sql, p, ORDERS_PARAMS)


@st.cache_data(ttl=600, show_spinner=False)
def filter_options():
    states = run_query_filtered(
        "SELECT DISTINCT customer_state FROM customers ORDER BY 1", {}, []
    ).customer_state.tolist()
    cats = run_query_filtered(
        "SELECT DISTINCT product_category_name_english FROM product_category_translation "
        "WHERE product_category_name_english IS NOT NULL ORDER BY 1", {}, []
    ).product_category_name_english.tolist()
    return states, cats


# ---------- 1. Business Overview ----------
@st.cache_data(ttl=600, show_spinner=False)
def overview_kpis(p):
    sql = ITEMS_CTE + """
    SELECT
        (SELECT COALESCE(SUM(price + freight_value), 0) FROM filtered_items) AS total_revenue,
        (SELECT COUNT(DISTINCT order_id) FROM filtered_orders) AS total_orders,
        (SELECT COUNT(DISTINCT customer_unique_id) FROM filtered_orders) AS total_customers,
        (SELECT COUNT(DISTINCT seller_id) FROM filtered_items) AS total_sellers,
        (SELECT AVG(price) FROM (
            SELECT order_id, SUM(price + freight_value) AS price FROM filtered_items GROUP BY order_id
        ) x) AS avg_order_value,
        (SELECT AVG(r.review_score) FROM order_reviews r
            JOIN filtered_orders fo ON fo.order_id = r.order_id) AS avg_review_score
    """
    return run_query_filtered(sql, p, ITEMS_PARAMS)


# ---------- 2. Sales Analysis ----------
@st.cache_data(ttl=600, show_spinner=False)
def monthly_revenue(p):
    sql = ITEMS_CTE + """
    SELECT DATE_FORMAT(fo.order_purchase_timestamp, '%Y-%m') AS month,
           SUM(fi.price + fi.freight_value) AS revenue
    FROM filtered_items fi JOIN filtered_orders fo ON fo.order_id = fi.order_id
    GROUP BY 1 ORDER BY 1
    """
    return run_query_filtered(sql, p, ITEMS_PARAMS)

@st.cache_data(ttl=600, show_spinner=False)
def revenue_by_category(p):
    sql = ITEMS_CTE + """
    SELECT category, SUM(price + freight_value) AS revenue
    FROM filtered_items GROUP BY category ORDER BY revenue DESC LIMIT 10
    """
    return run_query_filtered(sql, p, ITEMS_PARAMS)

@st.cache_data(ttl=600, show_spinner=False)
def top_products(p):
    sql = ITEMS_CTE + """
    SELECT product_id, SUM(price) AS revenue, COUNT(*) AS units_sold
    FROM filtered_items GROUP BY product_id ORDER BY revenue DESC LIMIT 10
    """
    return run_query_filtered(sql, p, ITEMS_PARAMS)

@st.cache_data(ttl=600, show_spinner=False)
def sales_by_state(p):
    sql = ITEMS_CTE + """
    SELECT fo.customer_state, SUM(fi.price + fi.freight_value) AS revenue
    FROM filtered_items fi JOIN filtered_orders fo ON fo.order_id = fi.order_id
    GROUP BY fo.customer_state ORDER BY revenue DESC
    """
    return run_query_filtered(sql, p, ITEMS_PARAMS)


# ---------- 3. Customer Analysis ----------
@st.cache_data(ttl=600, show_spinner=False)
def customer_spending(p):
    sql = ITEMS_CTE + """
    SELECT fo.customer_unique_id,
           COUNT(DISTINCT fo.order_id) AS orders,
           SUM(fi.price + fi.freight_value) AS total_spent
    FROM filtered_items fi JOIN filtered_orders fo ON fo.order_id = fi.order_id
    GROUP BY fo.customer_unique_id
    """
    return run_query_filtered(sql, p, ITEMS_PARAMS)

def repeat_vs_new(p):
    df = customer_spending(p)
    df["type"] = df["orders"].apply(lambda n: "Repeat" if n >= 2 else "New")
    return df.groupby("type").size().reset_index(name="count")

def top_customers(p, n=10):
    return customer_spending(p).sort_values("total_spent", ascending=False).head(n)

@st.cache_data(ttl=600, show_spinner=False)
def customer_distribution_by_state(p):
    sql = ORDERS_CTE + """
    SELECT customer_state, COUNT(DISTINCT customer_unique_id) AS customers
    FROM filtered_orders GROUP BY customer_state ORDER BY customers DESC
    """
    return run_query_filtered(sql, p, ORDERS_PARAMS)


# ---------- 4. Seller & Product Analysis ----------
@st.cache_data(ttl=600, show_spinner=False)
def top_sellers(p, n=10):
    sql = ITEMS_CTE + """
    SELECT seller_id, SUM(price + freight_value) AS revenue, COUNT(*) AS items_sold
    FROM filtered_items GROUP BY seller_id ORDER BY revenue DESC LIMIT :n
    """
    return run_query_filtered(sql, {**p, "n": n}, ITEMS_PARAMS)

@st.cache_data(ttl=600, show_spinner=False)
def seller_ratings(p):
    sql = ITEMS_CTE + """
    SELECT fi.seller_id, AVG(r.review_score) AS avg_rating, COUNT(*) AS review_count
    FROM filtered_items fi
    JOIN order_reviews r ON r.order_id = fi.order_id
    GROUP BY fi.seller_id HAVING COUNT(*) >= 5
    ORDER BY avg_rating DESC
    """
    return run_query_filtered(sql, p, ITEMS_PARAMS)


# ---------- 5. Delivery Analysis ----------
@st.cache_data(ttl=600, show_spinner=False)
def delivery_summary(p):
    sql = ORDERS_CTE + """
    SELECT
        AVG(DATEDIFF(order_delivered_customer_date, order_purchase_timestamp)) AS avg_delivery_days,
        SUM(CASE WHEN order_delivered_customer_date > order_estimated_delivery_date THEN 1 ELSE 0 END) AS late_orders,
        COUNT(order_delivered_customer_date) AS delivered_orders
    FROM filtered_orders WHERE order_delivered_customer_date IS NOT NULL
    """
    return run_query_filtered(sql, p, ORDERS_PARAMS)

@st.cache_data(ttl=600, show_spinner=False)
def delivery_by_state(p):
    sql = ORDERS_CTE + """
    SELECT customer_state,
           AVG(DATEDIFF(order_delivered_customer_date, order_purchase_timestamp)) AS avg_days
    FROM filtered_orders WHERE order_delivered_customer_date IS NOT NULL
    GROUP BY customer_state ORDER BY avg_days DESC
    """
    return run_query_filtered(sql, p, ORDERS_PARAMS)

@st.cache_data(ttl=600, show_spinner=False)
def delay_vs_review(p):
    sql = ORDERS_CTE + """
    SELECT r.review_score,
           AVG(DATEDIFF(fo.order_delivered_customer_date, fo.order_estimated_delivery_date)) AS avg_delay
    FROM filtered_orders fo
    JOIN order_reviews r ON r.order_id = fo.order_id
    WHERE fo.order_delivered_customer_date IS NOT NULL
    GROUP BY r.review_score ORDER BY r.review_score
    """
    return run_query_filtered(sql, p, ORDERS_PARAMS)


# ---------- 6. Customer Experience ----------
@st.cache_data(ttl=600, show_spinner=False)
def review_distribution(p):
    sql = ORDERS_CTE + """
    SELECT r.review_score, COUNT(*) AS n
    FROM filtered_orders fo JOIN order_reviews r ON r.order_id = fo.order_id
    GROUP BY r.review_score ORDER BY r.review_score
    """
    return run_query_filtered(sql, p, ORDERS_PARAMS)

@st.cache_data(ttl=600, show_spinner=False)
def reviews_by_category(p):
    sql = ITEMS_CTE + """
    SELECT fi.category, AVG(r.review_score) AS avg_score, COUNT(*) AS n
    FROM filtered_items fi JOIN order_reviews r ON r.order_id = fi.order_id
    GROUP BY fi.category HAVING COUNT(*) >= 20
    ORDER BY avg_score DESC
    """
    return run_query_filtered(sql, p, ITEMS_PARAMS)

@st.cache_data(ttl=600, show_spinner=False)
def seller_rank_by_category(p):
    """Uses RANK() window function to find the top seller within each category by revenue."""
    sql = ITEMS_CTE + """
    , ranked AS (
        SELECT category, seller_id,
               SUM(price + freight_value) AS revenue,
               RANK() OVER (PARTITION BY category ORDER BY SUM(price + freight_value) DESC) AS rnk
        FROM filtered_items
        WHERE category IS NOT NULL
        GROUP BY category, seller_id
    )
    SELECT category, seller_id, revenue
    FROM ranked WHERE rnk = 1
    ORDER BY revenue DESC
    LIMIT 10
    """
    return run_query_filtered(sql, p, ITEMS_PARAMS)


@st.cache_data(ttl=600, show_spinner=False)
def rating_vs_delivery_speed(p):
    """Rating vs delivery performance, for Customer Experience tab."""
    sql = ORDERS_CTE + """
    SELECT r.review_score,
           AVG(DATEDIFF(fo.order_delivered_customer_date, fo.order_purchase_timestamp)) AS avg_delivery_days
    FROM filtered_orders fo
    JOIN order_reviews r ON r.order_id = fo.order_id
    WHERE fo.order_delivered_customer_date IS NOT NULL
    GROUP BY r.review_score ORDER BY r.review_score
    """
    return run_query_filtered(sql, p, ORDERS_PARAMS)

