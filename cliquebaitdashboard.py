# Clique Bait Streamlit Dashboard

import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session

# ------------------------------------------------------------------
# SETUP
# ------------------------------------------------------------------
session = get_active_session()
st.set_page_config(page_title="Clique Bait Analytics", layout="wide")
st.title("Clique Bait Analytics Dashboard")
st.caption("Created by TheDataMagician🪄")


# ------------------------------------------------------------------
# IMPORTANT FUNCTIONS
# ------------------------------------------------------------------
@st.cache_data(ttl=300)
def run_query(sql: str) -> pd.DataFrame:
    """
    Execute a SQL query with the active Snowflake session.

    Parameters
    ----------
    sql(str) : The SQL query to be executed.

    Returns
    -------
    pd.DataFrame
    A pandas DataFrame containing the query results.
    """
    return session.sql(sql).to_pandas()


def download_csv_button(df: pd.DataFrame, label: str, filename: str):
    """
    Generate a Streamlit download button for a DataFrame in CSV format.

    Parameters
    ----------
    df (pd.DataFrame): The DataFrame to be exported.
    label (str): The label to display on the download button.
    filename (str): The name of the downloaded CSV file.

    Returns
    -------
    Outputs a download button on the Streamlit page.
    """
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(label=label, data=csv, file_name=filename, mime="text/csv")


# ------------------------------------------------------------------
# FILTERS
# ------------------------------------------------------------------
def sidebar_filters():
    """
    Sidebar filters for product and campaign selections.

    Returns
    -------
    selected_products(list): A list of selected product names from the multiselect widget.
    selected_campaign(str): The campaign selected from the dropdown. Defaults to "(All)".
    """
    products_df = run_query("""
        SELECT PRODUCT_NAME
        FROM PRODUCT_FUNNEL_SUMMARY
        WHERE PRODUCT_NAME IS NOT NULL
        ORDER BY PRODUCT_NAME
    """)
    campaigns_df = run_query("""
        SELECT DISTINCT CAMPAIGN_NAME
        FROM CAMPAIGN_IDENTIFIER
        WHERE CAMPAIGN_NAME IS NOT NULL
        ORDER BY CAMPAIGN_NAME
    """)

    st.sidebar.header("Filters")
    selected_products = st.sidebar.multiselect(
        "Products", options=products_df["PRODUCT_NAME"].tolist(), default=[]
    )
    selected_campaign = st.sidebar.selectbox(
        "Campaign", options=["(All)"] + campaigns_df["CAMPAIGN_NAME"].tolist(), index=0
    )
    return selected_products, selected_campaign


# ------------------------------------------------------------------
# TAB 1: PRODUCT FUNNEL
# ------------------------------------------------------------------
def product_funnel_tab(selected_products):
    """
    Display product funnel analytics (Views → Adds → Abandonment).

    Parameters
    ----------
    selected_products(list): List of product names selected from the sidebar filter.

    Returns
    -------
    Renders KPIs, bar charts, detailed table, and download button in Streamlit.
    """
    st.subheader("Product Funnel (Views → Adds → Abandonment Analysis)")

    pf = run_query("""
        SELECT PRODUCT_NAME, PRODUCT_CATEGORY, VIEWS, ADDED_TO_CART, ABANDONED_CARTS
        FROM PRODUCT_FUNNEL_SUMMARY
    """)
    if selected_products:
        pf = pf[pf["PRODUCT_NAME"].isin(selected_products)]

    # Metrics
    pf["VIEW_TO_CART_%"] = (pf["ADDED_TO_CART"] / pf["VIEWS"].replace({0: pd.NA})) * 100
    pf["ABANDONMENT_%"] = (pf["ABANDONED_CARTS"] / pf["ADDED_TO_CART"].replace({0: pd.NA})) * 100

    total_views = int(pf["VIEWS"].sum())
    total_adds = int(pf["ADDED_TO_CART"].sum())
    total_abandoned = int(pf["ABANDONED_CARTS"].sum())
    view_to_cart = (total_adds / total_views * 100) if total_views else 0
    abandonment_rate = pf["ABANDONMENT_%"].mean()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Views", f"{total_views:,}")
    c2.metric("Total Adds", f"{total_adds:,}")
    c3.metric("Total Abandoned", f"{total_abandoned:,}")
    c4.metric("Abandonment Rate", f"{abandonment_rate:.1f}%")

    # Charts
    st.markdown("**Top Products by Add-to-Cart**")
    st.bar_chart(pf.sort_values("ADDED_TO_CART", ascending=False).head(10).set_index("PRODUCT_NAME")["ADDED_TO_CART"])

    st.markdown("**Most Abandoned (by rate)**")
    st.bar_chart(pf.sort_values("ABANDONMENT_%", ascending=False).head(10).set_index("PRODUCT_NAME")["ABANDONMENT_%"])

    st.markdown("**Details**")
    st.dataframe(pf.sort_values(["ADDED_TO_CART", "VIEWS"], ascending=[False, False]), use_container_width=True)

    # Download
    download_csv_button(pf, "📥 Download Product Funnel Data", "product_funnel.csv")


# ------------------------------------------------------------------
# TAB 2: CAMPAIGN PERFORMANCE
# ------------------------------------------------------------------
def campaign_performance_tab(selected_campaign):
    """
    Display campaign performance metrics and trends.

    Parameters
    ----------
    selected_campaign (str): The campaign name selected from the sidebar filter.
    If "(All)", all campaigns are included.

    Returns
    -------
    Renders KPIs, line charts, raw visit records, and download button in Streamlit.
    """
    st.subheader("Campaign Performance")

    camp = run_query("""
        SELECT V.VISIT_ID, V.USER_ID, CAST(V.VISIT_START_TIME AS DATE) AS VISIT_DATE,
               V.PAGE_VIEWS, V.CART_ADDS, V.PURCHASE, C.CAMPAIGN_NAME
        FROM VISIT_SUMMARY V
        LEFT JOIN CAMPAIGN_IDENTIFIER C
        ON V.VISIT_START_TIME BETWEEN C.START_DATE AND C.END_DATE
    """)

    if selected_campaign != "(All)":
        camp = camp[camp["CAMPAIGN_NAME"] == selected_campaign]

    # Metrics
    daily = (camp.groupby("VISIT_DATE", as_index=False)
             .agg(VISITS=("VISIT_ID", "nunique"),
                  PURCHASES=("PURCHASE", "sum"),
                  PAGE_VIEWS=("PAGE_VIEWS", "sum"),
                  CART_ADDS=("CART_ADDS", "sum")))

    total_visits = int(camp["VISIT_ID"].nunique())
    total_purchases = int(camp["PURCHASE"].sum())
    total_page_views = int(camp["PAGE_VIEWS"].sum())
    total_cart_adds = int(camp["CART_ADDS"].sum())
    conv_rate = (total_purchases / total_visits * 100) if total_visits else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Visits", f"{total_visits:,}")
    c2.metric("Purchases", f"{total_purchases:,}")
    c3.metric("Conv. Rate", f"{conv_rate:.1f}%")
    c4.metric("Page Views", f"{total_page_views:,}")
    c5.metric("Cart Adds", f"{total_cart_adds:,}")

    # Charts
    st.markdown("**Purchases over Time**")
    st.line_chart(daily.set_index("VISIT_DATE")["PURCHASES"])
    st.markdown("**Visits over Time**")
    st.line_chart(daily.set_index("VISIT_DATE")["VISITS"])

    st.markdown("**Raw Visit Records**")
    st.dataframe(camp.sort_values("VISIT_DATE").head(500), use_container_width=True)

    # Download
    download_csv_button(camp, "📥 Download Campaign Data", "campaign_performance.csv")


# ------------------------------------------------------------------
# TAB 3: CHECKOUT & CONVERSION
# ------------------------------------------------------------------
def checkout_conversion_tab():
    """
    Display checkout and conversion analysis across visits and categories.

    Returns
    -------
    Renders KPIs, bar chart, detailed table, and download button in Streamlit.
    """
    st.subheader("Checkout & Conversion Analysis")

    visits = run_query("""
        SELECT VISIT_ID, USER_ID, CAST(VISIT_START_TIME AS DATE) AS VISIT_DATE,
               PAGE_VIEWS, CART_ADDS, PURCHASE, IMPRESSION, CLICK
        FROM VISIT_SUMMARY
    """)

    # KPI calculations
    visits["VIEW_TO_CART"] = visits.apply(lambda r: (r["CART_ADDS"]/r["PAGE_VIEWS"]) if r["PAGE_VIEWS"] else 0, axis=1)
    visits["CART_TO_PURCHASE"] = visits.apply(lambda r: (r["PURCHASE"]/r["CART_ADDS"]) if r["CART_ADDS"] else 0, axis=1)
    visits["ABANDONED"] = (visits["CART_ADDS"] > 0) & (visits["PURCHASE"] == 0)

    avg_view_to_cart = visits["VIEW_TO_CART"].mean() * 100 if len(visits) else 0
    avg_cart_to_purchase = visits["CART_TO_PURCHASE"].mean() * 100 if len(visits) else 0
    total_abandoned = int(visits["ABANDONED"].sum())

    c1, c2, c3 = st.columns(3)
    c1.metric("Avg View → Cart", f"{avg_view_to_cart:.1f}%")
    c2.metric("Avg Cart → Purchase", f"{avg_cart_to_purchase:.1f}%")
    c3.metric("Abandoned Visits", f"{total_abandoned:,}")

    # Category-level
    cats = run_query("""
        SELECT PRODUCT_CATEGORY, TIMES_VIEWED, TIMES_ADDED_TO_CART, ABANDONED_CARTS, TIMES_PURCHASED
        FROM CATEGORY_FUNNEL_SUMMARY
        WHERE PRODUCT_CATEGORY IS NOT NULL
    """)
    cats["ABANDONMENT_%"] = (cats["ABANDONED_CARTS"] / cats["TIMES_ADDED_TO_CART"].replace({0: pd.NA})) * 100

    st.markdown("**Abandonment by Category**")
    st.bar_chart(cats.set_index("PRODUCT_CATEGORY")["ABANDONMENT_%"])

    st.markdown("**Category Details**")
    st.dataframe(cats.sort_values("ABANDONMENT_%", ascending=False), use_container_width=True)

    # Download
    download_csv_button(visits, "📥 Download Checkout Data", "checkout_conversion.csv")


# ------------------------------------------------------------------
# MAIN APP
# ------------------------------------------------------------------
def main():
    """
    Main entry point of the Streamlit app.

    Returns
    -------
    Renders the sidebar filters and all three dashboard tabs.
    """
    selected_products, selected_campaign = sidebar_filters()

    tab1, tab2, tab3 = st.tabs(["🧯 Product Funnel", "🎯 Campaign Performance", "🛒 Checkout & Conversion"])
    with tab1:
        product_funnel_tab(selected_products)
    with tab2:
        campaign_performance_tab(selected_campaign)
    with tab3:
        checkout_conversion_tab()


if __name__ == "__main__":
    main()
