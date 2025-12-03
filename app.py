import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data
def load_data():
    df = pd.read_csv("ICE_Chicago_REAL_dataset.csv")
    df["Publication Date"] = pd.to_datetime(df["Publication Date"], errors="coerce")
    return df

df = load_data()

st.set_page_config(
    page_title="Witness Emotion Dashboard – REAL Data",
    layout="wide",
)

st.title("Witness Archive: Emotion & Theme Dashboard (REAL Data)")
st.markdown(
    "This dashboard visualizes real Chicago ICE-related testimony and news data. "
    "Use the sidebar to filter by emotions, themes, dates, and publication sources."
)

# Sidebar Filters
st.sidebar.header("Filters")

min_date = df["Publication Date"].min()
max_date = df["Publication Date"].max()

date_range = st.sidebar.date_input(
    "Publication Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

emotions = sorted(df["Emotion Label"].dropna().unique().tolist())
selected_emotions = st.sidebar.multiselect("Emotion Label", emotions, emotions)

themes = sorted(df["Thematic Label"].dropna().unique().tolist())
selected_themes = st.sidebar.multiselect("Thematic Label", themes, themes)

sources = sorted(df["Source"].dropna().unique().tolist())
selected_sources = st.sidebar.multiselect("Source", sources, sources)

# Filter Data
filtered = df.copy()

if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered = filtered[
        (filtered["Publication Date"] >= pd.to_datetime(start_date))
        & (filtered["Publication Date"] <= pd.to_datetime(end_date))
    ]

if selected_emotions:
    filtered = filtered[filtered["Emotion Label"].isin(selected_emotions)]

if selected_themes:
    filtered = filtered[filtered["Thematic Label"].isin(selected_themes)]

if selected_sources:
    filtered = filtered[filtered["Source"].isin(selected_sources)]

st.markdown(f"### Total Articles After Filter: **{len(filtered)}**")

# Metrics
if not filtered.empty:
    col1, col2, col3 = st.columns(3)
    col1.metric("Articles", len(filtered))
    col2.metric("Sources", filtered["Source"].nunique())
    col3.metric(
        "Date Range",
        f"{filtered['Publication Date'].min().date()} → {filtered['Publication Date'].max().date()}",
    )

    st.markdown("---")

    # Charts
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Emotion Distribution")
        emo_counts = (
            filtered["Emotion Label"]
            .value_counts()
            .reset_index()
            .rename(columns={"index": "Emotion", "Emotion Label": "Count"})
        )
        fig1 = px.pie(emo_counts, names="Emotion", values="Count", hole=0.3)
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        st.subheader("Theme Distribution")
        theme_counts = (
            filtered["Thematic Label"]
            .value_counts()
            .reset_index()
            .rename(columns={"index": "Theme", "Thematic Label": "Count"})
        )
        fig2 = px.bar(theme_counts, x="Theme", y="Count")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # Articles
    st.subheader("Articles (Top 50)")
    for _, row in filtered.head(50).iterrows():
        pub_date = (
            row["Publication Date"].date().isoformat()
            if pd.notna(row["Publication Date"])
            else "N/A"
        )

        st.markdown(
            f"**{row['Title']}**  \n"
            f"*{row['Source']} · {pub_date}*  \n"
            f"{row['Summary']}  \n"
            f"[Read Article]({row['URL']})"
        )
        st.markdown("---")

else:
    st.warning("No articles match your filters. Try adjusting filters.")
