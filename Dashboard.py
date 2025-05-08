


import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt

# --------------------- PAGE CONFIG --------------------- #
st.set_page_config(
    page_title="Coffee Shop Sales Dashboard",
    page_icon="☕",
    layout="wide"
)
alt.themes.enable("dark")

# --------------------- LOAD DATA --------------------- #
@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_coffee_sales_dataset.csv")
    df["order_date"] = pd.to_datetime(df["date"] + " " + df["time"], errors='coerce')
    return df
df = load_data()

# --------------------- SIDEBAR FILTERS --------------------- #
st.sidebar.header("Filters")
locations = st.sidebar.multiselect("Select Location:", options=df["location"].unique(), default=df["location"].unique())
categories = st.sidebar.multiselect("Select Category:", options=df["category"].unique(), default=df["category"].unique())

if "order_date" in df.columns:
    min_date = df["order_date"].min()
    max_date = df["order_date"].max()
    start_date, end_date = st.sidebar.date_input("Select Date Range:", [min_date, max_date])
    df = df[(df["order_date"] >= pd.to_datetime(start_date)) & (df["order_date"] <= pd.to_datetime(end_date))]

# Apply filters
df = df[(df["location"].isin(locations)) & (df["category"].isin(categories))]

# --------------------- KPI SECTION --------------------- #
def show_kpis(data):
    col1, col2, col3, col4 = st.columns(4)
    total_revenue = data["sales"].sum()
    total_orders = data["id"].nunique()
    aov = total_revenue / total_orders if total_orders else 0
    peak_location = data.groupby("location")["sales"].sum().idxmax()
    peak_location_sales = data.groupby("location")["sales"].sum().max()

    col1.metric("Total Revenue", f"${total_revenue:,.2f}")
    col2.metric("Total Orders", f"{total_orders:,}")
    col3.metric("Average Order Value", f"${aov:.2f}")
    col4.metric("Top Location", f"{peak_location}", f"${peak_location_sales:,.2f}")

# --------------------- CHART FUNCTIONS --------------------- #
def plot_monthly_sales(data):
    revenue = data.groupby("month")["sales"].sum().reset_index()
    month_order = ["January", "February", "March", "April", "May", "June"]
    revenue["month"] = pd.Categorical(revenue["month"], categories=month_order, ordered=True)
    revenue = revenue.sort_values("month")
    return px.bar(revenue, x="month", y="sales", title="Sales by Month", color="month")

def plot_location_sales(data):
    location_rev = data.groupby("location")["sales"].sum().reset_index()
    return px.pie(location_rev, names="location", values="sales", title="Sales by Location", hole=0.4)

def plot_top_products(data):
    top_products = data.groupby("product")["sales"].sum().reset_index().sort_values(by="sales", ascending=False).head(10)
    return px.bar(top_products, x="sales", y="product", title="Top 10 Products", orientation="h", color="product")

def plot_category_aov(data):
    category_aov = data.groupby("category")["sales"].mean().reset_index().sort_values("sales", ascending=False)
    return px.bar(category_aov, x="sales", y="category", title="Avg Order Value by Category", color="category")

def plot_category_popularity(data):
    cat_count = data["category"].value_counts().reset_index()
    cat_count.columns = ["category", "count"]
    return px.bar(cat_count, x="count", y="category", title="Popular Categories", color="category")

def plot_hourly_orders(data):
    hourly = data.groupby("hour")["id"].count().reset_index(name="orders")
    return px.line(hourly, x="hour", y="orders", title="Orders by Hour", markers=True)

def plot_weekday_orders(data):
    weekday_order = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    count = data["weekday"].value_counts().reindex(weekday_order).reset_index()
    count.columns = ["weekday", "orders"]
    return px.bar(count, x="weekday", y="orders", title="Orders by Day", color="weekday")

def plot_coffee_types(data):
    coffee_data = data[data["category"] == "Coffee"]
    coffee_count = coffee_data["product"].value_counts().reset_index()
    coffee_count.columns = ["product", "count"]
    return px.pie(coffee_count, names="product", values="count", title="Coffee Type Distribution", hole=0.4)

# --------------------- DISPLAY --------------------- #
st.title("\u2615 Coffee Shop Sales Dashboard")

show_kpis(df)

col1, col2 = st.columns(2)
col1.plotly_chart(plot_monthly_sales(df), use_container_width=True)
col2.plotly_chart(plot_location_sales(df), use_container_width=True)

col3, col4 = st.columns(2)
col3.plotly_chart(plot_top_products(df), use_container_width=True)
col4.plotly_chart(plot_category_aov(df), use_container_width=True)

col5, col6 = st.columns(2)
col5.plotly_chart(plot_category_popularity(df), use_container_width=True)
col6.plotly_chart(plot_hourly_orders(df), use_container_width=True)

col7, col8 = st.columns(2)
col7.plotly_chart(plot_weekday_orders(df), use_container_width=True)
col8.plotly_chart(plot_coffee_types(df), use_container_width=True)


