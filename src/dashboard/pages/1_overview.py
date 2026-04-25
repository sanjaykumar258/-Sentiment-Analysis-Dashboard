import pathlib, sys, os
# --- Fix for Streamlit Cloud ModuleNotFoundError ---
current_dir = pathlib.Path(__file__).parent.resolve()
root_dir = current_dir.parents[2] # Go up: pages -> dashboard -> root
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from src.dashboard.components.styles import (get_plotly_layout, COLOR_MAP, page_header,
                                              section_title, insight_caption, ACCENT)
from src.dashboard.components.sidebar import render_sidebar
from src.dashboard.components.particles import inject_particle_background
from src.dashboard.components.metrics_cards import animated_metric

st.set_page_config(page_title="Overview & KPIs", layout="wide")
if not st.session_state.get("logged_in", False):
    st.switch_page("app.py")
inject_particle_background()
from src.dashboard.components.theme_provider import inject_global_theme
inject_global_theme()


@st.cache_data(ttl=300)
def load_data():
    return pd.read_parquet("data/processed/processed_data.parquet")


df_raw = None
try:
    df_raw = load_data()
except FileNotFoundError:
    pass

# Always render sidebar first so chatbot persists
render_sidebar(df_raw if df_raw is not None else pd.DataFrame())

if df_raw is None:
    st.error("⚠️ Processed data not found. Please go to the Home page to upload a dataset.")
else:
    def main_page(df_raw):
        from src.dashboard.components.filters import render_filters
        df = df_raw  # Already rendered sidebar above
        
        page_header("📊", "Dashboard & KPIs", "High-level analytics overview and key performance indicators.")
        
        df = render_filters(df)
        
        
        # ── Animated KPI row ─────────────────────────────────────────────────
        total    = len(df)
        pos_pct  = round(len(df[df.Sentiment == "Positive"]) / total * 100, 1) if total and "Sentiment" in df.columns else 0
        avg_eng  = round(df["Engagement_Rate"].mean(), 2) if total and "Engagement_Rate" in df.columns else 0
        avg_view = int(df["Views"].mean()) if total and "Views" in df.columns else 0
        pos_pct_all = round(len(df_raw[df_raw.Sentiment == "Positive"]) / max(len(df_raw), 1) * 100, 1) if "Sentiment" in df_raw.columns else 0
        avg_eng_all = round(df_raw["Engagement_Rate"].mean(), 2) if "Engagement_Rate" in df_raw.columns else 0
        
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            animated_metric("Total posts", f"{total:,}", f"↑ {total - len(df_raw):+,} vs all",
                            "neutral", "#6EE7B7", total, "")
        with k2:
            animated_metric("Positive sentiment", f"{pos_pct}%", f"↑ {pos_pct - pos_pct_all:+.1f}pp",
                            "up" if pos_pct > pos_pct_all else "down", "#10B981", pos_pct, "%")
        with k3:
            animated_metric("Avg engagement", f"{avg_eng}%", f"↑ {avg_eng - avg_eng_all:+.2f}pp",
                            "up" if avg_eng > avg_eng_all else "down", "#818CF8", avg_eng, "%")
        with k4:
            animated_metric("Avg views/post", f"{avg_view:,}", "", "neutral", "#FBBF24",
                            avg_view if avg_view < 999999 else None, "")
        
        st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
        
        # ── Donut + Stacked bar ──────────────────────────────────────────────
        layout = get_plotly_layout()
        section_title("Sentiment distribution", "Breakdown by count and by platform")
        c1, c2 = st.columns([1, 2])
        
        with c1:
            sent_counts = df["Sentiment"].value_counts().reset_index()
            sent_counts.columns = ["Sentiment", "Count"]
            fig_donut = go.Figure(go.Pie(
                labels=sent_counts["Sentiment"],
                values=sent_counts["Count"],
                hole=0.62,
                marker=dict(colors=[COLOR_MAP[s] for s in sent_counts["Sentiment"]],
                            line=dict(color="rgba(0,0,0,0.15)", width=2)),
                textinfo="percent",
                textfont=dict(size=12, family="Inter"),
                hovertemplate="<b>%{label}</b><br>%{value:,} posts (%{percent})<extra></extra>",
            ))
            fig_donut.add_annotation(text=f"<b>{total:,}</b>", x=0.5, y=0.55,
                                      font=dict(size=24, family="Inter", color=layout.get("title_font", {}).get("color", "#FFF")),
                                      showarrow=False)
            fig_donut.add_annotation(text="posts", x=0.5, y=0.42,
                                      font=dict(size=12, family="Inter", color=layout.get("font", {}).get("color", "#64748B")),
                                      showarrow=False)
            fig_donut.update_layout(**layout)
            fig_donut.update_layout(showlegend=True,
                                     legend=dict(orientation="h", y=-0.1, x=0.5, xanchor="center"))
            st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})
            insight_caption(f"{pos_pct}% of all posts carry positive sentiment — {'above' if pos_pct > 50 else 'below'} the majority threshold.")
        
        with c2:
            plat_sent = df.groupby(["Platform", "Sentiment"]).size().reset_index(name="Count")
            plat_total = plat_sent.groupby("Platform")["Count"].transform("sum")
            plat_sent["Pct"] = (plat_sent["Count"] / plat_total * 100).round(1)
            fig_bar = px.bar(plat_sent, x="Platform", y="Pct", color="Sentiment",
                             color_discrete_map=COLOR_MAP, barmode="stack",
                             labels={"Pct": "Share (%)", "Platform": ""},
                             custom_data=["Count"])
            fig_bar.update_traces(
                hovertemplate="<b>%{x} — %{fullData.name}</b><br>%{y:.1f}% (%{customdata[0]:,} posts)<extra></extra>",
                marker_line_width=0, opacity=0.9
            )
            fig_bar.update_layout(**layout)
            fig_bar.update_layout(title="Sentiment share by platform (%)", bargap=0.25)
            st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})
            insight_caption("Each bar = 100%. Compare which platforms skew most positive or negative.")
            
        # ── Trend line ────────────────────────────────────────────────────────
        section_title("Sentiment over time", "7-day rolling average of positive sentiment %")
        df["Date"] = pd.to_datetime(df["Timestamp"]).dt.date
        daily = df.groupby(["Date", "Sentiment"]).size().unstack(fill_value=0)
        daily["total"] = daily.sum(axis=1)
        daily["pos_pct"] = (daily.get("Positive", 0) / daily["total"] * 100).round(2)
        daily["rolling7"] = daily["pos_pct"].rolling(7, min_periods=1).mean().round(2)
        daily = daily.reset_index()
        
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=daily["Date"], y=daily["pos_pct"],
            mode="lines", name="Daily positive %",
            line=dict(color=ACCENT, width=1, dash="dot"), opacity=0.4,
            hovertemplate="%{x}: %{y:.1f}%<extra></extra>"
        ))
        fig_trend.add_trace(go.Scatter(
            x=daily["Date"], y=daily["rolling7"],
            mode="lines", name="7-day rolling avg",
            line=dict(color=ACCENT, width=2.5),
            hovertemplate="7-day avg %{x}: <b>%{y:.1f}%</b><extra></extra>"
        ))
        fig_trend.update_layout(**layout)
        fig_trend.update_layout(yaxis_title="Positive %", yaxis_range=[0, 100], hovermode="x unified",
                                legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"))
        st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})
        insight_caption("Monitor the rolling average to detect macro shifts in public perception.")

    main_page(df_raw)
