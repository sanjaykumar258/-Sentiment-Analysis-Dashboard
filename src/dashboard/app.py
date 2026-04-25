import streamlit as st
import base64, pathlib, sys, os

# --- Fix for Streamlit Cloud ModuleNotFoundError ---
current_dir = pathlib.Path(__file__).parent.resolve()
root_dir = current_dir.parents[1] # Go up to the project root
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from dotenv import load_dotenv
load_dotenv()

st.set_page_config(
    page_title="Sentiment Intel v4.0",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─── Theme initialisation ─────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state["theme"] = "dark"
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# Intercept successful login from the HTML component iframe
if "logged_in" in st.query_params and st.query_params["logged_in"] == "true":
    st.session_state["logged_in"] = True
    # Clean the URL by removing the query param
    st.query_params.clear()
    st.rerun()

THEME = st.session_state["theme"]
IS_DARK = THEME == "dark"

# ─── Load hero image ──────────────────────────────────────────────────
hero_path = pathlib.Path(__file__).parent / "assets" / "hero.png"
hero_b64 = ""
if hero_path.exists():
    hero_b64 = base64.b64encode(hero_path.read_bytes()).decode()

import pandas as pd
from src.dashboard.components.sidebar import render_sidebar

@st.cache_data(ttl=300)
def load_data():
    return pd.read_parquet("data/processed/processed_data.parquet")


# ─── GLOBAL CSS — Dual theme design system ────────────────────────────
from src.dashboard.components.theme_provider import inject_global_theme
inject_global_theme()

# ─── Particle background ─────────────────────────────────────────────
from src.dashboard.components.particles import inject_particle_background
inject_particle_background()

if not st.session_state["logged_in"]:
    st.markdown("""
    <style>
    /* Hide all Streamlit chrome */
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    [data-testid="stHeader"] { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    
    /* Force 0 padding everywhere and disable scrolling */
    html, body, .stApp, .block-container, [data-testid="stAppViewContainer"], [data-testid="stMain"] { 
        margin: 0 !important; 
        padding: 0 !important; 
        overflow: hidden !important; 
        width: 100vw !important; 
        height: 100vh !important; 
        max-width: 100% !important;
    }
    
    /* Make iframe fill exactly 100% of screen */
    iframe { 
        position: fixed !important; 
        top: 0 !important; 
        left: 0 !important; 
        width: 100vw !important; 
        height: 100vh !important; 
        z-index: 999999 !important; 
        border: none !important; 
    }
    </style>
    """, unsafe_allow_html=True)

    from src.dashboard.components.auth import signin, signup
    import streamlit.components.v1 as components
    import json as _json

    login_ui_component = components.declare_component(
        "login_ui",
        path=str(pathlib.Path(__file__).parent / "components" / "login_ui")
    )
    
    # Pass any pending auth state to the component
    auth_error = st.session_state.get("_auth_error", "")
    auth_success = st.session_state.get("_auth_success", False)
    val = login_ui_component(auth_error=auth_error, auth_success=auth_success, key="login_iframe")

    # Clear state after sending to component
    if auth_error:
        st.session_state["_auth_error"] = ""
    if auth_success:
        st.session_state["_auth_success"] = False

    # Only process NEW values
    last_processed = st.session_state.get("_last_auth_val", "")
    
    if val and isinstance(val, str) and val != last_processed:
        st.session_state["_last_auth_val"] = val
        
        if val == "logged_in":
            st.session_state["logged_in"] = True
            st.rerun()
        else:
            try:
                data = _json.loads(val)
                action = data.get("action", "")
                
                if action == "signin":
                    result = signin(data["email"], data["password"], prehashed=True)
                    if result["ok"]:
                        st.session_state["user_name"] = result.get("name", "")
                        st.session_state["user_email"] = data["email"]
                        st.session_state["_auth_success"] = True
                        st.rerun()
                    else:
                        st.session_state["_auth_error"] = result["msg"]
                        st.rerun()

                elif action == "signup":
                    result = signup(data["email"], data["password"], data.get("name", ""), prehashed=True)
                    if result["ok"]:
                        st.session_state["user_name"] = result.get("name", "")
                        st.session_state["user_email"] = data["email"]
                        st.session_state["_auth_success"] = True
                        st.rerun()
                    else:
                        st.session_state["_auth_error"] = result["msg"]
                        st.rerun()
            except (_json.JSONDecodeError, KeyError):
                pass

else:
    # ─── Load data and sidebar ─────────────────────────────────────────
    total_posts = 5000
    pos_pct, neu_pct, neg_pct = 62, 23, 15
    try:
        df_raw = load_data()
        render_sidebar(df_raw)
        total_posts = len(df_raw)
        if total_posts > 0 and "Sentiment" in df_raw.columns:
            sent_counts = df_raw["Sentiment"].value_counts()
            pos_pct = round(sent_counts.get("Positive", 0) / total_posts * 100)
            neu_pct = round(sent_counts.get("Neutral", 0) / total_posts * 100)
            neg_pct = round(sent_counts.get("Negative", 0) / total_posts * 100)
            # If none of the standard labels match, use top-3 values
            if pos_pct == 0 and neu_pct == 0 and neg_pct == 0 and len(sent_counts) > 0:
                top_vals = sent_counts.head(3)
                pcts = (top_vals / total_posts * 100).round().astype(int).tolist()
                pos_pct = pcts[0] if len(pcts) > 0 else 0
                neu_pct = pcts[1] if len(pcts) > 1 else 0
                neg_pct = pcts[2] if len(pcts) > 2 else 0
    except FileNotFoundError:
        render_sidebar(pd.DataFrame())

    # ─── HERO ─────────────────────────────────────────────────────────
    st.markdown(f"""
<div style="display:flex;flex-direction:column;align-items:center;text-align:center;padding:4rem 2rem 1.5rem;position:relative;z-index:1;">
<div class="hero-animate" style="display:inline-flex;align-items:center;gap:8px;padding:7px 20px;border:1px solid var(--border);border-radius:100px;margin-bottom:2rem;background:var(--bg-card);box-shadow:var(--shadow-soft);backdrop-filter:blur(12px);">
<span class="pulse-dot"></span>
<span style="font-size:11px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:var(--brand-primary-text);font-family:var(--font-sans);">Live · {total_posts:,} posts · 6 platforms</span>
</div>
<h1 class="hero-animate-d1 hero-title" style="font-family:var(--font-sans);font-weight:800;color:var(--text-primary);">
Sentiment<br><span class="gradient-text">Intelligence</span>
</h1>
<p class="hero-animate-d2" style="font-family:var(--font-sans);font-size:1.1rem;color:var(--text-muted);max-width:540px;line-height:1.65;margin-bottom:2rem;font-weight:400;">
Real-time sentiment analysis across Instagram, TikTok, Twitter, YouTube, LinkedIn &amp; Facebook — powered by fine-tuned DistilBERT.
</p>
<div class="hero-animate-d3" style="display:flex;gap:12px;flex-wrap:wrap;justify-content:center;margin-bottom:1.5rem;">
<div style="padding:10px 24px;background:var(--bg-card);border:1px solid var(--border);border-radius:12px;font-size:13px;color:var(--text-secondary);font-family:var(--font-sans);font-weight:600;transition:all 0.25s;box-shadow:var(--shadow-soft);" onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform=''">📊 6 analytics pages</div>
<div style="padding:10px 24px;background:rgba(99,102,241,0.08);border:1px solid rgba(99,102,241,0.25);border-radius:12px;font-size:13px;color:var(--badge-indigo-text);font-family:var(--font-sans);font-weight:600;transition:all 0.25s;" onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform=''">🤖 Live ML predictions</div>
<div style="padding:10px 24px;background:rgba(251,191,36,0.05);border:1px solid rgba(251,191,36,0.2);border-radius:12px;font-size:13px;color:var(--badge-amber-text);font-family:var(--font-sans);font-weight:600;transition:all 0.25s;" onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform=''">⚡ SHAP explainability</div>
</div>
</div>
    """, unsafe_allow_html=True)

    # ─── UPLOAD SECTION ──────────────────────────────────────────────
    st.markdown("""
<div style="max-width:640px;margin:0 auto 1rem;padding:0 1rem;">
<div class="glass-card" style="padding:2rem 2.5rem;">
<div style="text-align:center;margin-bottom:1.5rem;">
<div style="font-family:var(--font-sans);color:var(--text-primary);font-size:1.05rem;font-weight:700;margin-bottom:4px;">🗂️ Upload Custom Dataset</div>
<div style="font-family:var(--font-sans);color:var(--text-muted);font-size:12.5px;">Analyze any sentiment dataset instantly</div>
</div>
<div style="display:flex;justify-content:center;align-items:center;gap:24px;font-family:var(--font-sans);">
<div style="text-align:center;">
<div style="width:40px;height:40px;background:rgba(99,102,241,0.1);color:var(--badge-indigo-text);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:15px;font-weight:700;margin:0 auto 6px;border:1px solid rgba(99,102,241,0.2);">1</div>
<div style="font-size:11px;font-weight:600;color:var(--text-primary);">Upload</div>
<div style="font-size:10px;color:var(--text-muted);">.csv only</div>
</div>
<div style="color:var(--text-faint);font-size:18px;margin-top:-12px;">→</div>
<div style="text-align:center;">
<div style="width:40px;height:40px;background:rgba(16,185,129,0.1);color:#10B981;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:15px;font-weight:700;margin:0 auto 6px;border:1px solid rgba(16,185,129,0.2);">2</div>
<div style="font-size:11px;font-weight:600;color:var(--text-primary);">Validate</div>
<div style="font-size:10px;color:var(--text-muted);">Sentiment col</div>
</div>
<div style="color:var(--text-faint);font-size:18px;margin-top:-12px;">→</div>
<div style="text-align:center;">
<div style="width:40px;height:40px;background:rgba(251,191,36,0.1);color:var(--badge-amber-text);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:15px;font-weight:700;margin:0 auto 6px;border:1px solid rgba(251,191,36,0.2);">3</div>
<div style="font-size:11px;font-weight:600;color:var(--text-primary);">Go Live</div>
<div style="font-size:10px;color:var(--text-muted);">Instant insights</div>
</div>
</div>
</div>
</div>
    """, unsafe_allow_html=True)

    # ─── FILE UPLOADER & CUSTOM POPUP ───────────────────────────
    col1, col2, col3 = st.columns([1.2, 2, 1.2])
    with col2:
        uploaded_file = st.file_uploader("Choose a dataset file", type=["csv"], label_visibility="collapsed")
        
        if uploaded_file is not None:
            if st.session_state.get("processed_file") != uploaded_file.name:
                # ── RENDER CUSTOM POPUP OVERLAY ──
                modal_placeholder = st.empty()
                with modal_placeholder.container():
                    st.markdown("""
                        <style>
                        .custom-modal-backdrop {
                            position: fixed !important;
                            top: 0 !important; left: 0 !important;
                            width: 100vw !important; height: 100vh !important;
                            background: rgba(0,0,0,0.4) !important;
                            backdrop-filter: blur(12px) saturate(160%) !important;
                            z-index: 9999999 !important;
                            display: flex !important;
                            align-items: center !important;
                            justify-content: center !important;
                        }
                        .custom-modal-container {
                            width: 100% !important;
                            max-width: 500px !important;
                            animation: modalPop 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) both !important;
                        }
                        @keyframes modalPop {
                            from { transform: scale(0.9) translateY(20px); opacity: 0; }
                            to   { transform: scale(1) translateY(0); opacity: 1; }
                        }
                        </style>
                        <div class="custom-modal-backdrop">
                            <div class="custom-modal-container">
                                <div class="glass-card" style="padding:2.5rem; width:100%; border-color:var(--brand-primary); box-shadow: 0 30px 60px rgba(0,0,0,0.6);">
                                    <h2 style="margin:0 0 1rem; font-family:var(--font-sans); color:var(--text-primary); text-align:center;">⚙️ Processing Dataset</h2>
                    """, unsafe_allow_html=True)
                    
                    import time, numpy as np
                    st.markdown(f"<p style='text-align:center; color:var(--text-muted);'>File: <code>{uploaded_file.name}</code></p>", unsafe_allow_html=True)
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    try:
                        # ── Step 1: Read CSV ──
                        status_text.caption("Reading file...")
                        progress_bar.progress(10)
                        time.sleep(0.4)
                        uploaded_file.seek(0)
                        new_df = pd.read_csv(uploaded_file)

                        # ── Step 2: Detect col ──
                        status_text.caption("Validating structure...")
                        progress_bar.progress(40)
                        col_lower_map = {c.lower().strip(): c for c in new_df.columns}
                        sentiment_col = None
                        for alias in ["sentiment", "label", "class", "target"]:
                            if alias in col_lower_map:
                                sentiment_col = col_lower_map[alias]
                                break

                        if sentiment_col:
                            if sentiment_col != "Sentiment":
                                new_df = new_df.rename(columns={sentiment_col: "Sentiment"})
                            new_df["Sentiment"] = new_df["Sentiment"].astype(str).str.strip().apply(lambda x: x.title())
                            
                            # ── Step 3: Save ──
                            status_text.caption("Saving to backend...")
                            progress_bar.progress(80)
                            import os
                            save_dir = "data/processed"
                            os.makedirs(save_dir, exist_ok=True)
                            new_df.to_parquet(os.path.join(save_dir, "processed_data.parquet"), index=False)
                            
                            progress_bar.progress(100)
                            status_text.caption("✅ Processing complete!")
                            st.success("Dataset successfully prepared.")
                            
                            if st.button("🚀 Load Dashboard", type="primary", use_container_width=True):
                                st.session_state["processed_file"] = uploaded_file.name
                                st.cache_data.clear()
                                st.rerun()
                        else:
                            st.error("❌ Sentiment column not found.")
                            if st.button("Cancel"): modal_placeholder.empty()
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
                        if st.button("Close"): modal_placeholder.empty()
                    
                    # Close HTML tags
                    st.markdown("</div></div></div>", unsafe_allow_html=True)


    # ─── METRICS GRID ────────────────────────────────────────────────
    st.markdown(f"""
<div style="display:flex;flex-direction:column;align-items:center;text-align:center;padding:1.5rem 2rem 2.5rem;position:relative;z-index:1;">
<div class="hero-animate-d5" style="display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:var(--border);border:1px solid var(--border);border-radius:20px;overflow:hidden;max-width:520px;width:100%;box-shadow:var(--shadow-soft);">
<div style="background:var(--bg-card-solid);padding:1.3rem;text-align:center;">
<div style="font-family:var(--font-sans);font-size:1.8rem;font-weight:800;color:#10B981;letter-spacing:-0.04em;">{pos_pct}%</div>
<div style="font-size:10px;color:var(--text-muted);font-weight:600;text-transform:uppercase;letter-spacing:0.06em;font-family:var(--font-sans);margin-top:5px;">Positive</div>
</div>
<div style="background:var(--bg-card-solid);padding:1.3rem;text-align:center;">
<div style="font-family:var(--font-sans);font-size:1.8rem;font-weight:800;color:var(--text-muted);letter-spacing:-0.04em;">{neu_pct}%</div>
<div style="font-size:10px;color:var(--text-muted);font-weight:600;text-transform:uppercase;letter-spacing:0.06em;font-family:var(--font-sans);margin-top:5px;">Neutral</div>
</div>
<div style="background:var(--bg-card-solid);padding:1.3rem;text-align:center;">
<div style="font-family:var(--font-sans);font-size:1.8rem;font-weight:800;color:#EF4444;letter-spacing:-0.04em;">{neg_pct}%</div>
<div style="font-size:10px;color:var(--text-muted);font-weight:600;text-transform:uppercase;letter-spacing:0.06em;font-family:var(--font-sans);margin-top:5px;">Negative</div>
</div>
</div>
<p style="margin-top:2rem;font-size:13px;color:var(--text-faint);font-family:var(--font-sans);font-weight:500;">← Select a page from the sidebar to begin</p>
</div>
    """, unsafe_allow_html=True)
