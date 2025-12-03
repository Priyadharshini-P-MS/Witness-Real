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

# ---------------- Sidebar Filters ----------------
st.sidebar.header("Filters")

min_date = df["Publication Date"].min()
max_date = df["Publication Date"].max()

# Handle case where dates might be missing
if pd.isna(min_date) or pd.isna(max_date):
    date_range = None
else:
    date_range = st.sidebar.date_input(
        "Publication Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

# Emotion filter
emotions = sorted(df["Emotion Label"].dropna().unique().tolist())
selected_emotions = st.sidebar.multiselect(
    "Emotion Label",
    options=emotions,
    default=emotions,
)

# Theme filter
themes = sorted(df["Thematic Label"].dropna().unique().tolist())
selected_themes = st.sidebar.multiselect(
    "Thematic Label",
    options=themes,
    default=themes,
)

# Source filter
sources = sorted(df["Source"].dropna().unique().tolist())
selected_sources = st.sidebar.multiselect(
    "Source",
    options=sources,
    default=sources,
)

# ---------------- Apply Filters ----------------
filtered = df.copy()

if date_range is not None and isinstance(date_range, (list, tuple)) and len(date_range) == 2:
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

# ---------------- Metrics & Charts ----------------
if not filtered.empty:
    col1, col2, col3 = st.columns(3)
    col1.metric("Articles", len(filtered))
    col2.metric("Sources", filtered["Source"].nunique())

    min_d = filtered["Publication Date"].min()
    max_d = filtered["Publication Date"].max()
    if pd.notna(min_d) and pd.notna(max_d):
        col3.metric("Date Range", f"{min_d.date()} → {max_d.date()}")
    else:
        col3.metric("Date Range", "N/A")

    st.markdown("---")

    c1, c2 = st.columns(2)

    # ----- Emotion Distribution Pie -----
    with c1:
        st.subheader("Emotion Distribution")
        emo_counts = filtered["Emotion Label"].value_counts().reset_index()
        # emo_counts columns: ['Emotion Label', 'Count']
        emo_counts.columns = ["Emotion Label", "Count"]

        if not emo_counts.empty:
            fig1 = px.pie(
                emo_counts,
                names="Emotion Label",
                values="Count",
                hole=0.3,
            )
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("No emotion data available for the current filter.")

    # ----- Theme Distribution Bar -----
    with c2:
        st.subheader("Theme Distribution")
        theme_counts = filtered["Thematic Label"].value_counts().reset_index()
        # theme_counts columns: ['Thematic Label', 'Count']
        theme_counts.columns = ["Thematic Label", "Count"]

        if not theme_counts.empty:
            fig2 = px.bar(
                theme_counts,
                x="Thematic Label",
                y="Count",
            )
            fig2.update_layout(
                xaxis_title="Thematic Label",
                yaxis_title="Count",
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No theme data available for the current filter.")

    st.markdown("---")

    # ---------------- Article List ----------------
    st.subheader("Articles (Top 50)")

    for _, row in filtered.head(50).iterrows():
        title = row.get("Title", "")
        source = row.get("Source", "")
        pub_date = row.get("Publication Date", pd.NaT)
        summary = row.get("Summary", "")
        url = row.get("URL", "")

        date_str = pub_date.date().isoformat() if pd.notna(pub_date) else "N/A"

        st.markdown(
            f"**{title}**  \n"
            f"*{source} · {date_str}*  \n"
            f"{summary}  \n"
            f"[Open article]({url})"
        )
        st.markdown("---")

else:
    st.warning("No articles match your filters. Try widening your filters.")
