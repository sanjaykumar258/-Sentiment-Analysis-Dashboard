import pathlib, sys, os
# --- Fix for Streamlit Cloud ModuleNotFoundError ---
current_dir = pathlib.Path(__file__).parent.resolve()
root_dir = current_dir.parents[2] # Go up: pages -> dashboard -> root
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from src.dashboard.components.styles import (get_plotly_layout, COLOR_MAP, page_header,
                                              section_title, insight_caption, card, is_dark,
                                              get_heatmap_colorscale, get_heatmap_text_color,
                                              get_polar_grid_color, get_polar_line_color, get_polar_tick_color)
from src.dashboard.components.sidebar import render_sidebar
from src.dashboard.components.particles import inject_particle_background

st.set_page_config(page_title="Competitive Benchmarking", layout="wide")
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

        df = df_raw  # Already rendered sidebar above
        page_header("⚡", "Competitive benchmarking", "Side-by-side platform comparison across key performance dimensions.")

        layout = get_plotly_layout()

        # ── Radar chart ───────────────────────────────────────────────────────
        section_title("Platform radar", "Select 2–3 platforms to compare across 5 dimensions")
        platforms = sorted([str(x) for x in df["Platform"].dropna().unique()])

        selected = st.multiselect("Compare platforms", platforms,
                                   default=platforms[:min(3, len(platforms))], max_selections=4)

        if selected:
            axes = ["Avg engagement %", "Positive sentiment %", "Avg virality",
                    "Avg save rate", "Avg comments"]
            df["virality"]  = (df["Shares"] * 3 + df["Comments"] * 2 + df["Likes"]) / (df["Views"] + 1)
            df["save_rate"] = df["Saves"] / (df["Views"] + 1)

            fig_radar = go.Figure()
            colors_radar = ["#6EE7B7", "#818CF8", "#FBBF24", "#F87171"]

            all_vals = []
            for plat in selected:
                sub = df[df["Platform"] == plat]
                vals = [
                    sub["Engagement_Rate"].mean(),
                    len(sub[sub.Sentiment == "Positive"]) / max(len(sub), 1) * 100,
                    sub["virality"].mean() * 100,
                    sub["save_rate"].mean() * 100,
                    sub["Comments"].mean() / 100,
                ]
                all_vals.append(vals)

            max_per_axis = [max(v[i] for v in all_vals) for i in range(5)]
            max_per_axis = [m if m > 0 else 1 for m in max_per_axis]

            def hex_to_rgba(h, a):
                h = h.lstrip('#')
                return f"rgba({int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)},{a})"

            for i, plat in enumerate(selected):
                norm = [round(all_vals[i][j] / max_per_axis[j] * 10, 2) for j in range(5)]
                base_color = colors_radar[i % len(colors_radar)]
                fig_radar.add_trace(go.Scatterpolar(
                    r=norm + [norm[0]], theta=axes + [axes[0]],
                    fill="toself", name=plat,
                    line=dict(color=base_color, width=2),
                    fillcolor=hex_to_rgba(base_color, 0.1),
                    hovertemplate=f"<b>{plat}</b><br>%{{theta}}: %{{r:.1f}}/10<extra></extra>"
                ))

            fig_radar.update_layout(**layout)
            fig_radar.update_layout(
                polar=dict(
                    bgcolor="rgba(0,0,0,0)",
                    radialaxis=dict(visible=True, range=[0, 10], gridcolor=get_polar_grid_color(),
                                    tickfont=dict(size=9, color=get_polar_tick_color()), tickcolor="rgba(0,0,0,0)"),
                    angularaxis=dict(tickfont=dict(size=11, family="Inter", color=get_polar_tick_color()),
                                     gridcolor=get_polar_grid_color(),
                                     linecolor=get_polar_line_color())
                ),
                showlegend=True, height=420
            )
            st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar": False})
            insight_caption("All metrics normalized 0–10. A platform that wins on all 5 axes fills the whole pentagon.")

        st.divider()
        c1, c2 = st.columns(2)

        with c1:
            section_title("Sentiment by influencer tier")
            tier_sent = df.groupby(["Influencer_Tier", "Sentiment"]).size().reset_index(name="Count")
            tier_total = tier_sent.groupby("Influencer_Tier")["Count"].transform("sum")
            tier_sent["Pct"] = (tier_sent["Count"] / tier_total * 100).round(1)
            tier_order = ["Nano", "Micro", "Mid-tier", "Macro", "Mega"]
            tier_order = [t for t in tier_order if t in tier_sent["Influencer_Tier"].values]
            fig_tier = px.bar(tier_sent, x="Influencer_Tier", y="Pct", color="Sentiment",
                              color_discrete_map=COLOR_MAP, barmode="stack",
                              category_orders={"Influencer_Tier": tier_order},
                              labels={"Pct": "Share (%)", "Influencer_Tier": ""})
            fig_tier.update_traces(marker_line_width=0, opacity=0.9)
            fig_tier.update_layout(**layout)
            fig_tier.update_layout(title="Sentiment share by influencer tier", bargap=0.25)
            st.plotly_chart(fig_tier, use_container_width=True, config={"displayModeBar": False})
            insight_caption("Do micro-influencers generate more positive sentiment than macro accounts?")

        with c2:
            section_title("Category × platform positive sentiment %")
            cat_plat = df[df.Sentiment == "Positive"].groupby(
                ["Category", "Platform"]).size().unstack(fill_value=0)
            cat_total = df.groupby(["Category", "Platform"]).size().unstack(fill_value=1)
            cat_pct = (cat_plat / cat_total * 100).round(1)

            fig_cp = go.Figure(go.Heatmap(
                z=cat_pct.values, x=cat_pct.columns.tolist(), y=cat_pct.index.tolist(),
                colorscale=get_heatmap_colorscale(),
                text=cat_pct.values, texttemplate="%{text:.0f}%", textfont=dict(size=9, color=get_heatmap_text_color()),
                hovertemplate="<b>%{y} on %{x}</b><br>Positive: %{z:.1f}%<extra></extra>",
                colorbar=dict(title="Pos %", len=0.8, tickfont=dict(size=9))
            ))
            fig_cp.update_layout(**layout)
            fig_cp.update_layout(title="Positive sentiment % by category and platform",
                                  xaxis_title="", yaxis_title="", height=360)
            st.plotly_chart(fig_cp, use_container_width=True, config={"displayModeBar": False})
            insight_caption("Brighter cells = category performs best on that platform for positive sentiment.")

    main_page(df_raw)
