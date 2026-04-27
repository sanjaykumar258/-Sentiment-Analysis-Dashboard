import streamlit as st
import pandas as pd


def render_filters(df: pd.DataFrame) -> pd.DataFrame:
    if "Timestamp" in df.columns:
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
        min_date = df["Timestamp"].min().date() if not df["Timestamp"].empty and pd.notna(df["Timestamp"].min()) else None
        max_date = df["Timestamp"].max().date() if not df["Timestamp"].empty and pd.notna(df["Timestamp"].max()) else None
    else:
        min_date, max_date = None, None

    with st.expander("⚙️ Data Filters", expanded=False):
        c1, c2, c3, c4 = st.columns(4)

        with c1:
            if min_date and max_date:
                date_range = st.date_input("📅 Date range", value=(min_date, max_date),
                                            min_value=min_date, max_value=max_date)
                if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
                    start_date, end_date = date_range
                else:
                    start_date, end_date = min_date, max_date
            else:
                start_date, end_date = None, None

            sentiments = ["Positive", "Negative", "Neutral"]
            selected_sentiments = st.multiselect("🎯 Sentiment", sentiments, default=sentiments)

        with c2:
            platforms = sorted([str(x) for x in df["Platform"].dropna().unique()]) if "Platform" in df.columns else []
            selected_platforms = st.multiselect("📱 Platform", platforms, default=platforms)

            categories = sorted([str(x) for x in df["Category"].dropna().unique()]) if "Category" in df.columns else []
            selected_categories = st.multiselect("📂 Category", categories, default=categories)

        with c3:
            content_types = sorted([str(x) for x in df["Content_Type"].dropna().unique()]) if "Content_Type" in df.columns else []
            selected_content = st.multiselect("📝 Content type", content_types, default=content_types)

            tiers = sorted([str(x) for x in df["Influencer_Tier"].dropna().unique()]) if "Influencer_Tier" in df.columns else []
            selected_tiers = st.multiselect("👤 Influencer tier", tiers, default=tiers)


        with c4:
            if "Engagement_Rate" in df.columns:
                max_eng = float(df["Engagement_Rate"].quantile(0.99))
                eng_threshold = st.slider("📈 Min engagement", 0.0, max_eng, 0.0, step=0.1, format="%.1f%%")
            else:
                eng_threshold = 0.0

            st.markdown("<br>", unsafe_allow_html=True)
            st.button("✨ Apply filters", use_container_width=True, type="primary")

    # ── Count active filters ──
    active = 0
    if start_date and end_date and min_date and max_date:
        if start_date != min_date or end_date != max_date:
            active += 1
    if len(selected_sentiments) < 3:
        active += 1
    if len(selected_platforms) < len(platforms):
        active += 1
    if len(selected_categories) < len(categories):
        active += 1
    if len(selected_content) < len(content_types):
        active += 1
    if len(selected_tiers) < len(tiers):
        active += 1
    if eng_threshold > 0:
        active += 1

    if active > 0:
        st.markdown(f"""
<div style="display:inline-flex;align-items:center;gap:8px;padding:6px 14px;background:rgba(99,102,241,0.08);border:1px solid rgba(99,102,241,0.2);border-radius:100px;margin-bottom:1rem;">
<span style="font-size:12px;font-weight:600;color:#818CF8;font-family:var(--font-sans);">🔽 {active} filter{'s' if active > 1 else ''} active</span>
</div>
""", unsafe_allow_html=True)

    # Apply masks
    mask = pd.Series(True, index=df.index)
    if start_date and end_date:
        mask &= (df["Timestamp"].dt.date >= start_date) & (df["Timestamp"].dt.date <= end_date)
    if selected_platforms:
        mask &= df["Platform"].isin(selected_platforms)
    if selected_categories:
        mask &= df["Category"].isin(selected_categories)
    if selected_tiers:
        mask &= df["Influencer_Tier"].isin(selected_tiers)
    if selected_sentiments:
        mask &= df["Sentiment"].isin(selected_sentiments)
    if "Engagement_Rate" in df.columns:
        mask &= (df["Engagement_Rate"] >= eng_threshold)
    if selected_content:
        mask &= df["Content_Type"].isin(selected_content)

    return df[mask].copy()
