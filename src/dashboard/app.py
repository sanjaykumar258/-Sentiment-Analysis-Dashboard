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
    page_title="Sentiment Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
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

    # ─── FILE UPLOADER ───────────────────────────────────────────────
    col1, col2, col3 = st.columns([1.2, 2, 1.2])
    with col2:
        @st.dialog("⚙️ Processing Dataset")
        def process_dataset(file):
            import time, numpy as np
            st.markdown(f"**File:** `{file.name}`")
            progress_bar = st.progress(0)
            status_text = st.empty()

            try:
                # ── Step 1: Read CSV ──
                status_text.caption("Reading file...")
                progress_bar.progress(10)
                time.sleep(0.3)

                file.seek(0)
                new_df = pd.read_csv(file)

                # ── Step 2: Auto-detect sentiment column (case-insensitive) ──
                status_text.caption("Detecting sentiment column...")
                progress_bar.progress(25)
                time.sleep(0.3)

                col_lower_map = {c.lower().strip(): c for c in new_df.columns}
                sentiment_col = None
                for alias in ["sentiment", "label", "class", "target", "emotion", "polarity"]:
                    if alias in col_lower_map:
                        sentiment_col = col_lower_map[alias]
                        break

                if sentiment_col is None:
                    st.error("⚠️ Could not find a sentiment column. Expected one of: "
                             "`Sentiment`, `Label`, `Class`, `Target`, `Emotion`, `Polarity`.")
                    return

                # Rename to standard "Sentiment" if needed
                if sentiment_col != "Sentiment":
                    new_df = new_df.rename(columns={sentiment_col: "Sentiment"})

                # ── Step 3: Normalize sentiment values ──
                status_text.caption("Normalizing sentiment labels...")
                progress_bar.progress(40)
                time.sleep(0.3)

                new_df["Sentiment"] = new_df["Sentiment"].astype(str).str.strip()
                positive_aliases = {"positive", "pos", "1", "1.0", "good", "happy", "joy", "love"}
                negative_aliases = {"negative", "neg", "-1", "-1.0", "bad", "sad", "anger", "hate", "fear"}
                neutral_aliases  = {"neutral", "neu", "0", "0.0", "mixed", "none", "other", "surprise"}

                def normalize_sentiment(val):
                    v = str(val).lower().strip()
                    if v in positive_aliases:
                        return "Positive"
                    elif v in negative_aliases:
                        return "Negative"
                    elif v in neutral_aliases:
                        return "Neutral"
                    else:
                        return val.title()  # Keep original but title-case

                new_df["Sentiment"] = new_df["Sentiment"].apply(normalize_sentiment)

                # ── Step 4: Ensure required columns exist ──
                status_text.caption("Preparing dataset structure...")
                progress_bar.progress(55)
                time.sleep(0.3)

                required_cols = {
                    "Post_ID":         lambda: [f"POST_{i:05d}" for i in range(len(new_df))],
                    "Timestamp":       lambda: pd.date_range("2024-01-01", periods=len(new_df), freq="h").astype(str).tolist(),
                    "Platform":        lambda: np.random.choice(["Instagram", "TikTok", "Twitter", "YouTube", "LinkedIn", "Facebook"], len(new_df)).tolist(),
                    "Content_Type":    lambda: np.random.choice(["Video", "Image", "Text", "Carousel", "Link"], len(new_df)).tolist(),
                    "Category":        lambda: np.random.choice(["Tech", "Fashion", "Finance", "Gaming", "Education", "Entertainment", "Health"], len(new_df)).tolist(),
                    "Likes":           lambda: np.random.randint(10, 5000, len(new_df)).tolist(),
                    "Comments":        lambda: np.random.randint(0, 500, len(new_df)).tolist(),
                    "Shares":          lambda: np.random.randint(0, 300, len(new_df)).tolist(),
                    "Views":           lambda: np.random.randint(100, 100000, len(new_df)).tolist(),
                    "Saves":           lambda: np.random.randint(0, 200, len(new_df)).tolist(),
                    "Follower_Count":  lambda: np.random.randint(1000, 500000, len(new_df)).tolist(),
                    "Hashtag_Count":   lambda: np.random.randint(0, 30, len(new_df)).tolist(),
                    "Content_Length":  lambda: np.random.randint(10, 2200, len(new_df)).tolist(),
                    "Influencer_Tier": lambda: np.random.choice(["Nano", "Micro", "Mid-tier", "Macro"], len(new_df)).tolist(),
                    "Has_Media":       lambda: np.random.choice([True, False], len(new_df)).tolist(),
                    "Is_Verified":     lambda: np.random.choice([True, False], len(new_df)).tolist(),
                }

                generated_cols = []
                for col_name, gen_fn in required_cols.items():
                    if col_name not in new_df.columns:
                        # Try case-insensitive match first
                        match = col_lower_map.get(col_name.lower().strip())
                        if match and match in new_df.columns:
                            new_df = new_df.rename(columns={match: col_name})
                        else:
                            new_df[col_name] = gen_fn()
                            generated_cols.append(col_name)

                # Ensure numeric engagement columns exist
                if "Engagement_Rate" not in new_df.columns:
                    views_safe = new_df["Views"].replace(0, 1)
                    new_df["Engagement_Rate"] = (
                        (new_df["Likes"] + new_df["Comments"] + new_df["Shares"] + new_df["Saves"]) / views_safe * 100
                    ).round(2)
                    generated_cols.append("Engagement_Rate")

                if "Hour_of_Day" not in new_df.columns:
                    new_df["Hour_of_Day"] = pd.to_datetime(new_df["Timestamp"], errors="coerce").dt.hour.fillna(12).astype(int)
                    generated_cols.append("Hour_of_Day")

                if "Day_of_Week" not in new_df.columns:
                    new_df["Day_of_Week"] = pd.to_datetime(new_df["Timestamp"], errors="coerce").dt.dayofweek.fillna(0).astype(int)
                    generated_cols.append("Day_of_Week")

                # ── Step 5: Save to Parquet ──
                status_text.caption("Saving dataset to backend...")
                progress_bar.progress(80)

                import os
                save_dir = "data/processed"
                os.makedirs(save_dir, exist_ok=True)
                new_df.to_parquet(os.path.join(save_dir, "processed_data.parquet"), index=False)



                progress_bar.progress(100)
                status_text.caption("✅ Processing complete!")
                time.sleep(0.4)

                st.divider()
                st.success("Dataset successfully validated and ready.")

                # Show dataset details
                st.markdown(f"**Total Rows:** `{len(new_df):,}`")
                st.markdown(f"**Total Features:** `{len(new_df.columns)}`")

                if generated_cols:
                    st.caption(f"ℹ️ Auto-generated missing columns: {', '.join(generated_cols)}")

                # Show sentiment distribution (max 5 columns to avoid overflow)
                dist = new_df["Sentiment"].value_counts().head(5)
                n_cols = min(len(dist), 4)
                cols = st.columns(n_cols)
                for i, (k, v) in enumerate(dist.items()):
                    if i >= n_cols:
                        break
                    cols[i].metric(label=str(k), value=f"{v:,}")

                st.write("")
                if st.button("Load Dashboard", type="primary", use_container_width=True):
                    st.session_state["processed_file"] = file.name
                    st.cache_data.clear()
                    st.rerun()

            except Exception as e:
                st.error(f"❌ Error processing file: {e}")

        uploaded_file = st.file_uploader("Choose a dataset file", type=["csv"], label_visibility="collapsed")

        if uploaded_file is not None:
            if st.session_state.get("processed_file") != uploaded_file.name:
                import os
                if os.path.exists("saved_model/model_card.json"):
                    try:
                        os.remove("saved_model/model_card.json")
                    except:
                        pass
                process_dataset(uploaded_file)
        else:
            # Do NOT delete data automatically on every rerun. 
            pass

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
