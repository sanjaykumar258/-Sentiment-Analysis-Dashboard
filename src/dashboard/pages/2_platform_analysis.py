import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from src.dashboard.components.styles import (get_plotly_layout, COLOR_MAP, PLATFORM_COLORS,
                                              DAY_MAP, page_header, section_title, insight_caption,
                                              get_heatmap_colorscale, is_dark)
from src.dashboard.components.sidebar import render_sidebar
from src.dashboard.components.particles import inject_particle_background

st.set_page_config(page_title="Platform Analysis", layout="wide")
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
        df = df_raw
        page_header("🔍", "Platform analysis", "Deep-dive into engagement patterns, content formats, and posting time.")
        df = render_filters(df)

        layout = get_plotly_layout()

        # Helper: convert hex #RRGGBB to rgba string
        def hex_to_rgba(hex_color, alpha=1.0):
            hex_color = hex_color.lstrip("#")
            r, g, b = int(hex_color[:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
            return f"rgba({r},{g},{b},{alpha})"

        tab1, tab2, tab3 = st.tabs(["📅  Best time to post", "📦  Content formats", "🔥  Top performers"])

        # ══════════════════════════════════════════════════════════════════════
        # TAB 1 — Best time to post
        # ══════════════════════════════════════════════════════════════════════
        with tab1:

            # ── 1. Engagement Heatmap ─────────────────────────────────────────
            section_title("Engagement heatmap", "Hour × day — hover any cell for the exact rate")

            if pd.api.types.is_numeric_dtype(df["Day_of_Week"]):
                df["Day_Name"] = df["Day_of_Week"].map(DAY_MAP)
            else:
                df["Day_Name"] = df["Day_of_Week"].astype(str).str.capitalize()

            if "Hour_of_Day" in df.columns:
                df["Hour_of_Day"] = df["Hour_of_Day"].clip(0, 23).astype(int)

            pivot = df.pivot_table(values="Engagement_Rate", index="Day_Name",
                                   columns="Hour_of_Day", aggfunc="mean")
            all_hours = list(range(24))
            pivot = pivot.reindex(columns=all_hours).fillna(0)
            day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            pivot = pivot.reindex([d for d in day_order if d in pivot.index])

            # Compact hour labels
            hour_labels = [f"{h}{'am' if h < 12 else 'pm'}" if h not in (0, 12)
                           else ("12am" if h == 0 else "12pm") for h in all_hours]
            # Fix: 0 -> 12am already handled, fix 1-11
            hour_labels = []
            for h in all_hours:
                if h == 0:
                    hour_labels.append("12am")
                elif h < 12:
                    hour_labels.append(f"{h}am")
                elif h == 12:
                    hour_labels.append("12pm")
                else:
                    hour_labels.append(f"{h-12}pm")

            z_vals = np.round(pivot.values, 2)

            # Rich colorscale
            if is_dark():
                cs = [[0, "#0F172A"], [0.2, "#164E63"], [0.4, "#0E7490"],
                      [0.6, "#06B6D4"], [0.8, "#34D399"], [1.0, "#A7F3D0"]]
            else:
                cs = [[0, "#F0FDFA"], [0.2, "#CCFBF1"], [0.4, "#99F6E4"],
                      [0.6, "#5EEAD4"], [0.8, "#2DD4BF"], [1.0, "#0D9488"]]

            fig_heat = go.Figure(go.Heatmap(
                z=z_vals,
                x=hour_labels,
                y=pivot.index.tolist(),
                colorscale=cs,
                hovertemplate="<b>%{y}</b> at <b>%{x}</b><br>Avg engagement: <b>%{z:.2f}%</b><extra></extra>",
                colorbar=dict(
                    title=dict(text="Engagement %", font=dict(size=11, family="Inter")),
                    tickfont=dict(size=10), ticksuffix="%",
                    len=0.9, thickness=12, outlinewidth=0,
                ),
                xgap=3, ygap=3, zsmooth=False,
            ))
            # Time-period labels below x-axis
            for mid_h, label in [(2, "🌙 Night"), (8, "🌅 Morning"), (14, "☀️ Afternoon"), (20, "🌆 Evening")]:
                fig_heat.add_annotation(
                    x=hour_labels[mid_h], y=-0.15, yref="paper",
                    text=f"<b>{label}</b>", showarrow=False,
                    font=dict(size=10, color="#94A3B8" if is_dark() else "#64748B", family="Inter"),
                )
            fig_heat.update_layout(**layout)
            fig_heat.update_layout(
                title="Average engagement rate by hour and day",
                xaxis=dict(title="", tickfont=dict(size=9)),
                yaxis=dict(title="", tickfont=dict(size=11)),
                height=460, margin=dict(l=0, r=0, t=40, b=55),
            )
            st.plotly_chart(fig_heat, use_container_width=True, config={"displayModeBar": False})
            insight_caption("Bright cells = best times to post. Hover for exact values. Look for consistent patterns across days.")

            st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

            # ── 2. Reach vs Engagement (two lollipop charts) ──────────────────
            section_title("Reach vs engagement", "Does a bigger audience mean more engagement?")

            col_left, col_right = st.columns(2)

            # --- Left: Lollipop by Influencer Tier ---
            with col_left:
                tier_order = ["Nano", "Micro", "Mid-tier", "Macro", "Mega"]
                tier_colors = {"Nano": "#6EE7B7", "Micro": "#34D399", "Mid-tier": "#818CF8", "Macro": "#FBBF24", "Mega": "#F87171"}

                if "Influencer_Tier" in df.columns:
                    tier_eng = df.groupby("Influencer_Tier")["Engagement_Rate"].agg(["mean", "count"]).reset_index()
                    tier_eng.columns = ["Tier", "Avg", "Posts"]
                    tier_eng["Tier"] = pd.Categorical(tier_eng["Tier"], categories=tier_order, ordered=True)
                    tier_eng = tier_eng.sort_values("Tier").dropna(subset=["Tier"])

                    fig_lol1 = go.Figure()
                    for _, row in tier_eng.iterrows():
                        c = tier_colors.get(row["Tier"], "#6EE7B7")
                        fig_lol1.add_trace(go.Scatter(
                            x=[0, row["Avg"]], y=[row["Tier"], row["Tier"]],
                            mode="lines", line=dict(color=c, width=3),
                            showlegend=False, hoverinfo="skip",
                        ))
                    fig_lol1.add_trace(go.Scatter(
                        x=tier_eng["Avg"], y=tier_eng["Tier"],
                        mode="markers+text",
                        marker=dict(size=14, color=[tier_colors.get(t, "#6EE7B7") for t in tier_eng["Tier"]],
                                    line=dict(width=2, color="rgba(255,255,255,0.15)")),
                        text=[f"  {v:.1f}%" for v in tier_eng["Avg"]],
                        textposition="middle right",
                        textfont=dict(size=11, family="Inter", color="#E2E8F0" if is_dark() else "#334155"),
                        hovertemplate="<b>%{y}</b><br>Avg: %{x:.2f}%<extra></extra>",
                        showlegend=False,
                    ))
                    fig_lol1.update_layout(**layout)
                    fig_lol1.update_layout(
                        title="Avg engagement by influencer tier",
                        xaxis=dict(title="Engagement Rate %", showgrid=True),
                        yaxis=dict(title="", categoryorder="array", categoryarray=list(reversed(tier_order))),
                        showlegend=False, height=370,
                    )
                    st.plotly_chart(fig_lol1, use_container_width=True, config={"displayModeBar": False})
                else:
                    st.info("Influencer_Tier column not found.")

            # --- Right: Lollipop by Platform ---
            with col_right:
                plat_eng = df.groupby("Platform")["Engagement_Rate"].mean().sort_values(ascending=True).reset_index()
                plat_eng.columns = ["Platform", "Avg"]

                fig_lol2 = go.Figure()
                for _, row in plat_eng.iterrows():
                    c = PLATFORM_COLORS.get(row["Platform"], "#6EE7B7")
                    fig_lol2.add_trace(go.Scatter(
                        x=[0, row["Avg"]], y=[row["Platform"], row["Platform"]],
                        mode="lines", line=dict(color=c, width=3),
                        showlegend=False, hoverinfo="skip",
                    ))
                fig_lol2.add_trace(go.Scatter(
                    x=plat_eng["Avg"], y=plat_eng["Platform"],
                    mode="markers+text",
                    marker=dict(size=14, color=[PLATFORM_COLORS.get(p, "#6EE7B7") for p in plat_eng["Platform"]],
                                line=dict(width=2, color="rgba(255,255,255,0.15)")),
                    text=[f"  {v:.2f}%" for v in plat_eng["Avg"]],
                    textposition="middle right",
                    textfont=dict(size=11, family="Inter", color="#E2E8F0" if is_dark() else "#334155"),
                    hovertemplate="<b>%{y}</b><br>Avg: %{x:.2f}%<extra></extra>",
                    showlegend=False,
                ))
                fig_lol2.update_layout(**layout)
                fig_lol2.update_layout(
                    title="Avg engagement by platform",
                    xaxis=dict(title="Engagement Rate %", showgrid=True),
                    yaxis=dict(title=""),
                    showlegend=False, height=370,
                )
                st.plotly_chart(fig_lol2, use_container_width=True, config={"displayModeBar": False})

            insight_caption("Nano/micro influencers often outperform macro accounts on engagement rate. Platform choice also matters significantly.")

            st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

            # ── 3. Engagement spread by influencer tier (Box plot) ─────────────
            section_title("Engagement spread by audience size", "Box plot shows median, quartiles, and outliers")

            tier_order_full = ["Nano", "Micro", "Mid-tier", "Macro", "Mega"]
            tier_palette = {"Nano": "#6EE7B7", "Micro": "#34D399", "Mid-tier": "#818CF8", "Macro": "#FBBF24", "Mega": "#F87171"}

            if "Influencer_Tier" in df.columns:
                p99 = df["Engagement_Rate"].quantile(0.99)
                df_box = df[df["Engagement_Rate"] <= p99].copy()
                df_box["Influencer_Tier"] = pd.Categorical(df_box["Influencer_Tier"], categories=tier_order_full, ordered=True)
                df_box = df_box.dropna(subset=["Influencer_Tier"])

                fig_box_tier = go.Figure()
                for tier in tier_order_full:
                    tier_data = df_box[df_box["Influencer_Tier"] == tier]["Engagement_Rate"]
                    if len(tier_data) == 0:
                        continue
                    c = tier_palette.get(tier, "#6EE7B7")
                    fig_box_tier.add_trace(go.Box(
                        y=tier_data,
                        name=tier,
                        marker_color=c,
                        line_color=c,
                        fillcolor=hex_to_rgba(c, 0.2),
                        boxmean="sd",
                        boxpoints="outliers",
                        marker=dict(size=3, opacity=0.5),
                        hoverinfo="y",
                    ))

                fig_box_tier.update_layout(**layout)
                fig_box_tier.update_layout(
                    title="Engagement rate distribution by influencer tier",
                    xaxis=dict(title=""),
                    yaxis=dict(title="Engagement Rate %"),
                    showlegend=False,
                    height=420,
                )
                st.plotly_chart(fig_box_tier, use_container_width=True, config={"displayModeBar": False})
                insight_caption("The box shows the interquartile range (25th–75th percentile). The line inside is the median. Diamond = mean. Dots are outliers.")
            else:
                st.info("Influencer_Tier column not found in dataset.")

        # ══════════════════════════════════════════════════════════════════════
        # TAB 2 — Content formats
        # ══════════════════════════════════════════════════════════════════════
        with tab2:
            c1, c2 = st.columns(2)
            with c1:
                section_title("Engagement by content type")

                content_colors = {
                    "Video": "#818CF8", "Image": "#6EE7B7", "Text": "#FBBF24",
                    "Carousel": "#F87171", "Link": "#06B6D4", "Story": "#EC4899",
                }

                fig_box = px.box(
                    df, x="Content_Type", y="Engagement_Rate", color="Content_Type",
                    color_discrete_map=content_colors,
                    labels={"Content_Type": "", "Engagement_Rate": "Engagement %"},
                )
                fig_box.update_traces(boxmean="sd", marker_size=3, line_width=1.5)
                fig_box.update_layout(**layout)
                fig_box.update_layout(showlegend=False, title="Distribution by content type", xaxis_tickangle=-30, height=400)
                st.plotly_chart(fig_box, use_container_width=True, config={"displayModeBar": False})
                insight_caption("Box = median + IQR. Taller boxes = more variance in that format.")

            with c2:
                section_title("Platform engagement breakdown")
                metrics = ["Likes", "Comments", "Shares", "Saves"]
                available = [m for m in metrics if m in df.columns]
                plat_m = df.groupby("Platform")[available].mean().reset_index()
                colors = ["#6EE7B7", "#818CF8", "#FBBF24", "#F87171"]
                fig_g = go.Figure()
                for i, m in enumerate(available):
                    fig_g.add_trace(go.Bar(
                        name=m, x=plat_m["Platform"], y=plat_m[m],
                        marker_color=colors[i], marker_line_width=0, opacity=0.9,
                        hovertemplate=f"<b>%{{x}}</b><br>Avg {m}: %{{y:,.0f}}<extra></extra>",
                    ))
                fig_g.update_layout(**layout)
                fig_g.update_layout(barmode="group", title="Average interactions per post", bargap=0.25, bargroupgap=0.08, height=400)
                st.plotly_chart(fig_g, use_container_width=True, config={"displayModeBar": False})
                insight_caption("Compare absolute interaction volumes across platforms.")

        # ══════════════════════════════════════════════════════════════════════
        # TAB 3 — Top performers
        # ══════════════════════════════════════════════════════════════════════
        with tab3:
            section_title("Top categories by virality", "Weighted: Shares×3 + Comments×2 + Likes")
            df["virality_score"] = (df["Shares"] * 3 + df["Comments"] * 2 + df["Likes"]) / (df["Views"] + 1)
            cat_vir = df.groupby("Category")["virality_score"].mean().sort_values(ascending=True).reset_index()
            fig_vir = px.bar(cat_vir, x="virality_score", y="Category", orientation="h",
                             color="virality_score",
                             color_continuous_scale=get_heatmap_colorscale(),
                             labels={"virality_score": "Avg virality", "Category": ""})
            fig_vir.update_traces(marker_line_width=0)
            fig_vir.update_layout(**layout)
            fig_vir.update_layout(title="Average virality score by category", coloraxis_showscale=False, height=400)
            st.plotly_chart(fig_vir, use_container_width=True, config={"displayModeBar": False})
            insight_caption("High virality = content that drives shares & comments proportional to views.")

    main_page(df_raw)
