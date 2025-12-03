
    import streamlit as st
    import pandas as pd
    import plotly.express as px

    @st.cache_data
    def load_data():
        df = pd.read_csv("ICE_Chicago_REAL_dataset.csv")
        # Parse dates
        df["Publication Date"] = pd.to_datetime(df["Publication Date"], errors="coerce")
        return df

    df = load_data()

    st.set_page_config(
        page_title="Witness Emotion Dashboard – Real Data",
        layout="wide",
    )

    st.title("Witness Archive: Emotion & Theme Dashboard (Real Data)")
    st.markdown(
        "This dashboard explores **real news and testimony data** about ICE-related events "
        "in Chicago. Use the filters in the sidebar to focus on specific dates, emotions, "
        "themes, or sources."
    )

    # --- Sidebar filters ---
    st.sidebar.header("Filters")

    # Date filter
    min_date = df["Publication Date"].min()
    max_date = df["Publication Date"].max()

    if pd.isna(min_date) or pd.isna(max_date):
        date_range = None
    else:
        date_range = st.sidebar.date_input(
            "Publication date range",
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

    # Apply filters
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

    st.markdown(f"**Total Articles after filter:** {len(filtered)}")

    # --- Summary metrics ---
    if not filtered.empty:
        min_d = filtered["Publication Date"].min()
        max_d = filtered["Publication Date"].max()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Articles", len(filtered))
        with col2:
            st.metric("Sources", filtered["Source"].nunique())
        with col3:
            if pd.notna(min_d) and pd.notna(max_d):
                st.metric("Date Range", f"{min_d.date()} → {max_d.date()}")
            else:
                st.metric("Date Range", "N/A")

        st.markdown("---")

        # --- Charts ---
        c1, c2 = st.columns(2)

        with c1:
            st.subheader("Emotion Distribution")
            emo_counts = (
                filtered["Emotion Label"]
                .value_counts()
                .reset_index()
                .rename(columns={"index": "Emotion Label", "Emotion Label": "Count"})
            )
            if not emo_counts.empty:
                fig_emo = px.pie(
                    emo_counts,
                    names="Emotion Label",
                    values="Count",
                    hole=0.3,
                )
                st.plotly_chart(fig_emo, use_container_width=True)
            else:
                st.info("No emotion data available for the current filter.")

        with c2:
            st.subheader("Theme Distribution")
            theme_counts = (
                filtered["Thematic Label"]
                .value_counts()
                .reset_index()
                .rename(columns={"index": "Thematic Label", "Thematic Label": "Count"})
            )
            if not theme_counts.empty:
                fig_theme = px.bar(
                    theme_counts,
                    x="Thematic Label",
                    y="Count",
                )
                fig_theme.update_layout(xaxis_title="Thematic Label", yaxis_title="Count")
                st.plotly_chart(fig_theme, use_container_width=True)
            else:
                st.info("No theme data available for the current filter.")

        st.markdown("---")
        st.subheader("Articles (Top 50)")

        # Show a list of articles with clickable URLs
        for _, row in filtered.head(50).iterrows():
            title = row.get("Title", "")
            source = row.get("Source", "")
            pub_date = row.get("Publication Date", pd.NaT)
            summary = row.get("Summary", "")
            url = row.get("URL", "")

            date_str = pub_date.date().isoformat() if pd.notna(pub_date) else "N/A"

            st.markdown(
                f"**{title}**  
"
                f"*{source} · {date_str}*  
"
                f"{summary}  
"
                f"[Open article]({url})"
            )
            st.markdown("---")
    else:
        st.warning("No articles match the selected filters. Try widening your filters.")
