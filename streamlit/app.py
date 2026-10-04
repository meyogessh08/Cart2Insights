import streamlit as st
import pandas as pd
import plotly.express as px
import queries as q
from utils import build_params

st.set_page_config(page_title="Cart2Insights", layout="wide", page_icon="🛒")

DARK = "plotly_dark"
ACCENT = "#00C896"

st.title("Cart2Insights: E-Commerce Performance Dashboard")
st.caption("Decoding e-commerce performance across sales, customers, sellers, delivery, and reviews.")

# ---- Sidebar filters (form = runs once on submit, not on every click) ----
states, categories = q.filter_options()
st.sidebar.header("🔍 Filters")
with st.sidebar.form("filters_form"):
    date_range = st.date_input(
        "Order date range",
        value=(pd.Timestamp("2016-01-01"), pd.Timestamp("2018-12-31")),
    )
    sel_states = st.multiselect("State (empty = all)", states, default=[])
    sel_categories = st.multiselect("Category (empty = all)", categories, default=[])
    submitted = st.form_submit_button("Apply Filters", use_container_width=True, type="primary")

if "filters" not in st.session_state or submitted:
    start, end = date_range if len(date_range) == 2 else (date_range[0], date_range[0])
    st.session_state["filters"] = build_params(start, end, sel_states, sel_categories, states, categories)

p = st.session_state["filters"]

tabs = st.tabs(["Overview", "Sales", "Customers", "Sellers & Products", "Delivery", "Customer Experience"])

# ---------- 1. Overview ----------
with tabs[0]:
    k = q.overview_kpis(p).iloc[0]
    cols = st.columns(6)
    kpis = [
        ( "Revenue", f"R$ {k.total_revenue:,.0f}"),
        ("Orders", f"{k.total_orders:,}"),
        ( "Customers", f"{k.total_customers:,}"),
        ( "Sellers", f"{k.total_sellers:,}"),
        ("Avg Order Value", f"R$ {k.avg_order_value:,.2f}" if pd.notna(k.avg_order_value) else "—"),
        ( "Avg Review", f"{k.avg_review_score:.2f}" if pd.notna(k.avg_review_score) else "—"),
    ]
    for col, (icon, label, val) in zip(cols, kpis):
        with col.container(border=True):
            st.markdown(f"{icon} **{label}**")
            st.markdown(f"### {val}")

        st.markdown("")  # spacing
        
    c1, c2 = st.columns([2, 1])

    with c1:
        st.subheader("Revenue Trend")
        mr = q.monthly_revenue(p)
        fig = px.area(mr, x="month", y="revenue", color_discrete_sequence=[ACCENT])
        fig.update_layout(template=DARK, height=300, margin=dict(t=10))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Order Status")
        osb = q.order_status_breakdown(p)
        fig = px.pie(osb, names="order_status", values="n", hole=0.55)
        fig.update_layout(template=DARK, height=300, margin=dict(t=10), showlegend=False)
        fig.update_traces(textinfo="label+percent")
        st.plotly_chart(fig, use_container_width=True)


# ---------- 2. Sales ----------
with tabs[1]:
    st.subheader("Monthly Revenue Trend")
    mr = q.monthly_revenue(p)
    fig = px.line(mr, x="month", y="revenue", markers=True, color_discrete_sequence=[ACCENT])
    fig.update_layout(template=DARK, height=350)
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Revenue by Category")
        rc = q.revenue_by_category(p)
        fig = px.bar(rc, x="revenue", y="category", orientation="h", color_discrete_sequence=[ACCENT])
        fig.update_layout(template=DARK, height=400, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.subheader("Sales by State")
        ss = q.sales_by_state(p)
        fig = px.bar(ss, x="customer_state", y="revenue", color_discrete_sequence=[ACCENT])
        fig.update_layout(template=DARK, height=400)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top Products by Revenue")
    st.dataframe(q.top_products(p), use_container_width=True, hide_index=True)

# ---------- 3. Customers ----------
with tabs[2]:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Repeat vs New Customers")
        rn = q.repeat_vs_new(p)
        fig = px.pie(rn, names="type", values="count", hole=0.5,
                     color_discrete_sequence=[ACCENT, "#444"])
        fig.update_layout(template=DARK, height=350)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.subheader("Top Customers by Spending")
        st.dataframe(q.top_customers(p), use_container_width=True, hide_index=True)

    st.subheader("Customer Distribution by State")
    cd = q.customer_distribution_by_state(p)
    fig = px.bar(cd, x="customer_state", y="customers", color_discrete_sequence=[ACCENT])
    fig.update_layout(template=DARK, height=350)
    st.plotly_chart(fig, use_container_width=True)

# ---------- 4. Sellers & Products ----------
with tabs[3]:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Top Sellers by Revenue")
        st.dataframe(q.top_sellers(p), use_container_width=True, hide_index=True)
    with c2:
        st.subheader("Top Rated Sellers (min 5 reviews)")
        st.dataframe(q.seller_ratings(p).head(10), use_container_width=True, hide_index=True)

    st.subheader("Revenue by Category")
    rc = q.revenue_by_category(p)
    fig = px.bar(rc, x="category", y="revenue", color_discrete_sequence=[ACCENT])
    fig.update_layout(template=DARK, height=400)
    st.plotly_chart(fig, use_container_width=True)

# ---------- 5. Delivery ----------
with tabs[4]:
    d = q.delivery_summary(p).iloc[0]
    pct_late = (d.late_orders / d.delivered_orders * 100) if d.delivered_orders else 0
    c1, c2, c3 = st.columns(3)
    with c1.container(border=True):
        st.markdown("🚚 **Avg Delivery Days**")
        st.markdown(f"### {d.avg_delivery_days:.1f}" if pd.notna(d.avg_delivery_days) else "### —")
    with c2.container(border=True):
        st.markdown("⏰ **% Delayed**")
        st.markdown(f"### {pct_late:.1f}%")
    with c3.container(border=True):
        st.markdown("📦 **Delivered Orders**")
        st.markdown(f"### {d.delivered_orders:,}")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("On-Time vs Delayed")
        pie_df = pd.DataFrame({
            "status": ["On-Time", "Delayed"],
            "count": [d.delivered_orders - d.late_orders, d.late_orders],
        })
        fig = px.pie(pie_df, names="status", values="count", hole=0.5,
                     color_discrete_sequence=[ACCENT, "#E74C3C"])
        fig.update_layout(template=DARK, height=350)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.subheader("Avg Delivery Days by State")
        dbs = q.delivery_by_state(p)
        fig = px.bar(dbs, x="customer_state", y="avg_days", color_discrete_sequence=[ACCENT])
        fig.update_layout(template=DARK, height=350)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Delivery Delay vs Review Score")
    dvr = q.delay_vs_review(p)
    fig = px.bar(dvr, x="review_score", y="avg_delay", color_discrete_sequence=[ACCENT])
    fig.add_hline(y=0, line_dash="dash", line_color="red")
    fig.update_layout(template=DARK, height=350)
    st.plotly_chart(fig, use_container_width=True)

# ---------- 6. Customer Experience ----------
with tabs[5]:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Review Score Distribution")
        rd = q.review_distribution(p)
        fig = px.bar(rd, x="review_score", y="n", color_discrete_sequence=[ACCENT])
        fig.update_layout(template=DARK, height=350)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.subheader("Avg Rating by Category (min 20 reviews)")
        st.dataframe(q.reviews_by_category(p), use_container_width=True, hide_index=True)