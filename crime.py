import streamlit as st
import pandas as pd
import plotly.express as px


st.set_page_config(page_title="Crime Data Dashboard", layout="wide")

st.title(" Crime Data Visualization Dashboard (India)")


@st.cache_data
def load_data():
    df = pd.read_csv("data/crime_data.csv")
    df.columns = df.columns.str.strip()

    #  State/District names
    df["STATE/UT"] = df["STATE/UT"].str.strip().str.title()
    df["DISTRICT"] = df["DISTRICT"].str.strip().str.title()

    # Convert numeric
    df["TOTAL IPC CRIMES"] = pd.to_numeric(df["TOTAL IPC CRIMES"], errors="coerce")

    return df

df = load_data()

st.sidebar.header(" Filter Options")

states = sorted(df["STATE/UT"].unique())
selected_state = st.sidebar.selectbox("Select State", states)

years = sorted(df["YEAR"].unique())
selected_year = st.sidebar.selectbox("Select Year", years)

filtered_df = df[
    (df["STATE/UT"].str.lower() == selected_state.lower()) &
    (df["YEAR"] == selected_year)
]

districts = sorted(filtered_df["DISTRICT"].unique())
selected_district = st.sidebar.selectbox("Select District", districts)

# FILTER FINAL DATA
district_df = filtered_df[
    filtered_df["DISTRICT"].str.lower() == selected_district.lower()
]

if district_df.empty:
    st.warning("No data found for selected filters.")
    st.stop()


tab1, tab2, tab3 = st.tabs([" Overview", " Trend Analysis", " Alerts & Recommendations"])

#  TAB 1: OVERVIEW
with tab1:
    st.subheader(f"Summary for {selected_district}, {selected_state} ({selected_year})")

    # Identify numeric crime columns
    crime_cols = [col for col in df.columns if col not in ["STATE/UT", "DISTRICT", "YEAR"]]

    total_crimes = int(district_df[crime_cols].sum(axis=1))
    top_3_crimes = district_df[crime_cols].T.sort_values(by=district_df.index[0], ascending=False).head(3)

    col1, col2 = st.columns(2)
    col1.metric("Total IPC Crimes", f"{total_crimes:,}")
    col2.write("**Top 3 Crime Categories:**")
    col2.dataframe(top_3_crimes.rename(columns={district_df.index[0]: "Cases"}))

    # Crime Distribution
    st.markdown("###  Crime Category Distribution")
    crime_data = district_df[crime_cols].T.reset_index()
    crime_data.columns = ["Crime Type", "Number of Cases"]

    fig_bar = px.bar(
        crime_data.sort_values(by="Number of Cases", ascending=False).head(10),
        x="Crime Type", y="Number of Cases", color="Crime Type",
        title=f"Top 10 Crimes in {selected_district}, {selected_year}"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # District comparison
    st.markdown("###  District-wise Comparison")
    fig_state = px.bar(
        filtered_df.sort_values(by="TOTAL IPC CRIMES", ascending=False),
        x="DISTRICT", y="TOTAL IPC CRIMES",
        title=f"District-Wise Total Crimes in {selected_state} ({selected_year})"
    )
    st.plotly_chart(fig_state, use_container_width=True)

#  TAB 2: TREND ANALYSIS
with tab2:
    st.subheader(f"Yearly Crime Trend for {selected_district}")

    trend_df = df[
        (df["STATE/UT"].str.lower() == selected_state.lower()) &
        (df["DISTRICT"].str.lower() == selected_district.lower())
    ].groupby("YEAR")[crime_cols].sum().reset_index()

    fig_trend = px.line(
        trend_df, x="YEAR", y="TOTAL IPC CRIMES",
        title=f"Total IPC Crimes Over Years in {selected_district}",
        markers=True
    )
    st.plotly_chart(fig_trend, use_container_width=True)

    # Percentage Change
    if len(trend_df) > 1:
        change = trend_df["TOTAL IPC CRIMES"].pct_change().iloc[-1] * 100
        if change > 0:
            st.warning(f"⚠️ Crimes have **increased by {change:.2f}%** compared to last year.")
        else:
            st.success(f" Crimes have **decreased by {abs(change):.2f}%** compared to last year.")

#  TAB 3: ALERTS & RECOMMENDATIONS
with tab3:
    st.subheader(" Automatic Alerts & Recommendations")

    top_crime = top_3_crimes.index[0].upper()

    # ALERT SYSTEM
    st.markdown("### ⚠️ Alerts")

    if trend_df["TOTAL IPC CRIMES"].iloc[-1] > trend_df["TOTAL IPC CRIMES"].iloc[-2]:
        st.error("🔴 ALERT: Total IPC crimes have risen this year — increase police surveillance.")
    else:
        st.success("🟢 Crimes have reduced compared to last year — maintain effective patrolling.")

    # Check if any single crime type dominates
    dominant_ratio = top_3_crimes.iloc[0, 0] / total_crimes
    if dominant_ratio > 0.3:
        st.warning(f"⚠️ High Concentration: **{top_3_crimes.index[0]}** forms more than 30% of all crimes!")

    # RECOMMENDATION ENGINE
    st.markdown("###  Recommended Measures")

    if "BURGLARY" in top_crime:
        st.info(" **Burglary Prevention:** Increase night patrolling and install CCTV in residential areas.")
    elif "THEFT" in top_crime:
        st.info(" **Theft Control:** Deploy teams in market areas and near transport hubs during peak hours.")
    elif "RIOT" in top_crime:
        st.info(" **Riot Control:** Strengthen intelligence network and promote community peace programs.")
    elif "ASSAULT" in top_crime or "HOMICIDE" in top_crime:
        st.info(" **Violent Crime Prevention:** Increase police visibility and install panic alert systems.")
    else:
        st.info(" Maintain regular patrolling and awareness campaigns to prevent petty crimes.")

    # Optional: Data-driven recommendation
    if change > 10:
        st.warning(" Major rise detected — Recommend immediate review of patrolling routes.")
    elif change < -10:
        st.success(" Crime decline trend detected — Continue current preventive strategies.")

    st.markdown("---")
    st.subheader(" View District Data")
    st.dataframe(district_df)

# -------------------------------------------
# END OF APP
# -------------------------------------------
st.markdown("---")