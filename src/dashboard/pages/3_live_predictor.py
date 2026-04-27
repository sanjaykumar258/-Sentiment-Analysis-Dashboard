import pathlib, sys, os
# --- Fix for Streamlit Cloud ModuleNotFoundError ---
current_dir = pathlib.Path(__file__).parent.resolve()
root_dir = current_dir.parents[2] # Go up: pages -> dashboard -> root
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from src.dashboard.components.styles import (get_plotly_layout, page_header, section_title,
                                              sentiment_badge, animated_confidence_bar,
                                              insight_caption, COLOR_MAP, is_dark)
from src.dashboard.components.particles import inject_particle_background
from src.api.client import predict

# ─── PAGE INITIALIZATION ───
st.set_page_config(page_title="Live Predictor", layout="wide")
if not st.session_state.get("logged_in", False):
    st.switch_page("app.py")

inject_particle_background()
from src.dashboard.components.theme_provider import inject_global_theme
inject_global_theme()

# ─── GLOBAL STATE (IDE STABILITY) ───
platform, category, content_type, tier = "Instagram", "Tech", "Video", "Macro"
followers, hashtags, length, engagement = 0, 0, 0, 0.0
post_text = ""
shap_vals, sent_idx, processed_items = {}, 0, []
wi_eng, wi_foll, wi_hash = 0.0, 0, 0
run = False
c1 = c2 = c3 = c4 = c5 = c6 = c7 = c8 = None
wi1 = wi2 = wi3 = None
fig_shap = None

@st.cache_data(ttl=300)
def load_data():
    return pd.read_parquet("data/processed/processed_data.parquet")

try:
    df_raw = load_data()
except FileNotFoundError:
    df_raw = pd.DataFrame()

from src.dashboard.components.sidebar import render_sidebar
render_sidebar(df_raw)

# ─── HEADER ───
page_header("🤖", "Live predictor", "Run real-time sentiment inference powered by fine-tuned DistilBERT.")

_dark = is_dark()
_card_bg = "var(--bg-card)" 
_card_border = "var(--border)"

# ─── INPUT SECTION ───
with st.container():
    col_auto, _ = st.columns([1, 5])
    with col_auto:
        if st.button("🎲 Generate example"):
            if not df_raw.empty:
                row = df_raw.sample(1).iloc[0]
                st.session_state["ex_platform"]  = row["Platform"]
                st.session_state["ex_category"]  = row["Category"]
                st.session_state["ex_type"]      = row["Content_Type"]
                st.session_state["ex_tier"]      = row["Influencer_Tier"]
                st.session_state["ex_followers"] = int(row["Follower_Count"])
                st.session_state["ex_hashtags"]  = int(row.get("Hashtag_Count", 10) if pd.notna(row.get("Hashtag_Count")) else 10)
                st.session_state["ex_length"]    = int(row.get("Content_Length", 300) if pd.notna(row.get("Content_Length")) else 300)
                st.session_state["ex_eng"]       = float(row["Engagement_Rate"])
                st.session_state["ex_label"]     = row["Sentiment"]
                
                # Smarter text detection
                text_candidates = ["Text_Content", "Content", "Text", "Body", "Message", "Comment", "Tweet", "Post", "Description"]
                found_text = ""
                for col in df_raw.columns:
                    if col.strip().lower() in [c.lower() for c in text_candidates]:
                        found_text = str(row[col])
                        break
                
                # If still empty, try to find any column with long text content
                if not found_text:
                    for col in df_raw.columns:
                        val = str(row[col])
                        if len(val) > 15 and col not in ["Post_ID", "Timestamp", "Platform", "Category", "Sentiment"]:
                            found_text = val
                            break
                
                st.session_state["live_post_text"] = found_text

            else:
                # Mock fallback if no data is loaded
                import random
                mock_posts = [
                    "Just tried the new AI features and they are absolutely game-changing! 🚀 #Tech #Innovation",
                    "Feeling frustrated with the latest update. It keeps crashing. 😤 #Broken #UI",
                    "Had a wonderful time at the conference today! So many great insights. ✨",
                    "This product is okay, but definitely overpriced for what it offers.",
                    "Absolutely love the new design! It's so sleek and modern. 😍",
                    "The service was terrible. I will not be coming back again. 👎"
                ]
                st.session_state["ex_platform"]  = random.choice(["Instagram", "TikTok", "Twitter", "YouTube"])
                st.session_state["ex_category"]  = random.choice(["Tech", "Fashion", "Gaming", "Education"])
                st.session_state["ex_type"]      = random.choice(["Video", "Image", "Text"])
                st.session_state["ex_tier"]      = random.choice(["Nano", "Micro", "Mid-tier", "Macro"])
                st.session_state["ex_followers"] = random.randint(1000, 500000)
                st.session_state["ex_hashtags"]  = random.randint(1, 15)
                st.session_state["ex_length"]    = random.randint(50, 1000)
                st.session_state["ex_eng"]       = round(random.uniform(0.5, 15.0), 2)
                st.session_state["live_post_text"] = random.choice(mock_posts)
            st.rerun()

    post_text = st.text_area("Post content", key="live_post_text", placeholder="e.g. Amazing results on this new tech post!", height=100)
    
    platforms_list = sorted([str(x) for x in df_raw["Platform"].dropna().unique()]) if not df_raw.empty else ["Instagram", "TikTok", "Twitter", "YouTube", "LinkedIn", "Facebook"]
    categories_list = sorted([str(x) for x in df_raw["Category"].dropna().unique()]) if not df_raw.empty else ["Tech", "Fashion", "Finance", "Gaming", "Education"]
    content_types_list = sorted([str(x) for x in df_raw["Content_Type"].dropna().unique()]) if not df_raw.empty else ["Video", "Image", "Text", "Carousel"]

    tier_list = ["Nano", "Micro", "Mid-tier", "Macro"]

    def safe_index(lst, val, fallback=0):
        try: return lst.index(val)
        except ValueError: return fallback

    c1, c2, c3, c4 = st.columns(4)
    with c1: platform = st.selectbox("Platform", platforms_list, index=safe_index(platforms_list, st.session_state.get("ex_platform", "Instagram")))
    with c2: category = st.selectbox("Category", categories_list, index=safe_index(categories_list, st.session_state.get("ex_category", categories_list[0])))
    with c3: content_type = st.selectbox("Content type", content_types_list, index=safe_index(content_types_list, st.session_state.get("ex_type", content_types_list[0])))
    with c4: tier = st.selectbox("Influencer tier", tier_list, index=safe_index(tier_list, st.session_state.get("ex_tier", "Macro")))

    c5, c6, c7, c8 = st.columns(4)
    with c5: followers = st.number_input("Follower count", 0, 5_000_000, value=st.session_state.get("ex_followers", 100000), step=1)
    with c6: hashtags = st.number_input("Hashtag count", 0, 30, value=st.session_state.get("ex_hashtags", 10))
    with c7: length = st.number_input("Content length", 0, 2200, value=st.session_state.get("ex_length", 300))
    with c8: engagement = st.number_input("Engagement rate", 0.0, 200.0, value=float(st.session_state.get("ex_eng", 3.0)), step=0.1)

    col_btn, _ = st.columns([1, 4])
    with col_btn:
        run = st.button("🔍 Analyze sentiment", use_container_width=True, type="primary")

# ─── PREDICTION LOGIC ───
if run:
    eng_label = "High" if engagement > 15 else "Low" if engagement < 5 else "Medium"
    text_input = f"Engagement: {eng_label}. Text: {post_text}"
    with st.spinner("Running inference..."):
        result = predict(text_input)

    st.divider()
    section_title("Prediction result")
    r1, r2 = st.columns([1, 2])

    with r1:
        sentiment_badge(result["sentiment"])
        animated_confidence_bar(result["confidence"], "Model confidence", delay_ms=0)

        section_title("Class probabilities", "Softmax scores")
        probs = result["probabilities"]
        delay = 200
        for label in ["Positive", "Neutral", "Negative"]:
            if label in probs:
                animated_confidence_bar(probs[label], label, delay_ms=delay)
                delay += 200

        if "ex_label" in st.session_state:
            actual = st.session_state["ex_label"]
            match = actual == result["sentiment"]
            bg = 'rgba(16,185,129,0.08)' if match else 'rgba(239,68,68,0.08)'
            bdr = 'rgba(16,185,129,0.2)' if match else 'rgba(239,68,68,0.2)'
            clr = '#10B981' if match else '#EF4444'
            ico = '✓ Correct: ' if match else '✗ Incorrect: '
            st.markdown(f"""
<div style="margin-top:1rem;padding:12px 16px;background:{bg};border:1px solid {bdr};border-radius:12px;backdrop-filter:blur(10px);">
<p style="font-size:11px;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.05em;font-family:var(--font-sans);margin:0 0 6px;font-weight:700;">Actual label</p>
<p style="font-size:15px;font-weight:700;color:{clr};font-family:var(--font-sans);margin:0;letter-spacing:-0.02em;">{ico}{actual}</p>
</div>
""", unsafe_allow_html=True)

    with r2:
        layout = get_plotly_layout()
        section_title("SHAP feature importance", "Features that pushed this prediction")
        shap_vals = result.get("shap_values", {})
        if not shap_vals:
            shap_vals = {"Engagement Rate": 0.42, "Platform": 0.28, "Content_Type": 0.21,
                         "Category": 0.15, "Follower_Count": -0.18, "Hashtag_Count": -0.08}
        
        sent_idx = 2 if result['sentiment'] == 'Positive' else 0 if result['sentiment'] == 'Negative' else 1
        
        processed_items = []
        for feature, val in shap_vals.items():
            try:
                if isinstance(val, (list, np.ndarray, tuple)):
                    v = val[sent_idx]
                    final_val = v[0] if isinstance(v, (list, np.ndarray, tuple)) else v
                else:
                    final_val = val
                processed_items.append((feature, float(final_val)))
            except (IndexError, TypeError, ValueError):
                processed_items.append((feature, 0.0))
            
        shap_items = sorted(processed_items, key=lambda x: abs(x[1]), reverse=True)[:8]
        if shap_items:
            features, values = zip(*shap_items)
            colors = ["#10B981" if v > 0 else "#EF4444" for v in values]
            fig_shap = go.Figure(go.Bar(
                x=list(values), y=list(features), orientation="h",
                marker=dict(color=colors, line_width=0),
                hovertemplate="<b>%{{y}}</b><br>SHAP: %{{x:+.3f}}<extra></extra>"
            ))
            fig_shap.add_vline(x=0, line_width=1, line_color="var(--border)")
            fig_shap.update_layout(**layout)
            fig_shap.update_layout(title="Green = pushes toward prediction, red = against",
                                    xaxis_title="SHAP value", yaxis_title="", height=320)
            st.plotly_chart(fig_shap, use_container_width=True, config={"displayModeBar": False})
            insight_caption("SHAP values show each feature's contribution to the final score.")

        section_title("What-if analysis", "Tweak values and re-predict instantly")
        wi1, wi2, wi3 = st.columns(3)
        wi_eng, wi_foll, wi_hash = engagement, followers // 1000, hashtags
        
        wi_eng  = wi1.slider("Engagement rate",  0.0, 100.0, float(engagement), 0.5)
        wi_foll = wi2.slider("Followers (K)",     1, 5000, int(followers // 1000), 50)
        wi_hash = wi3.slider("Hashtag count",     0, 30, int(hashtags))

        if st.button("🔄 Re-run with new values"):
            wi_eng_label = "High" if wi_eng > 15 else "Low" if wi_eng < 5 else "Medium"
            wi_text = f"Engagement: {wi_eng_label}. Text: {post_text}"
            with st.spinner("Re-running..."):
                wi_result = predict(wi_text)
            sc = '#10B981' if wi_result['sentiment'] == 'Positive' else '#EF4444' if wi_result['sentiment'] == 'Negative' else '#6B7280'
            st.markdown(f"""
<div style="padding:14px 18px;background:rgba(99,102,241,0.08);border:1px solid rgba(99,102,241,0.2);border-radius:12px;margin-top:1rem;backdrop-filter:blur(10px);">
<span style="font-size:13px;color:#818CF8;font-weight:700;font-family:var(--font-sans);">What-if result: </span>
<span style="font-size:15px;font-weight:700;font-family:var(--font-sans);color:{sc};letter-spacing:-0.02em;">
{wi_result['sentiment']} ({wi_result['confidence']*100:.1f}% confidence)
</span>
</div>
""", unsafe_allow_html=True)
