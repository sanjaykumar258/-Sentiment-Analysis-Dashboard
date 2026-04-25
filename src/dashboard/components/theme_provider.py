# components/theme_provider.py — Centralized global theme injection
# Call inject_global_theme() at the top of EVERY page to guarantee
# consistent Light / Dark mode across the entire dashboard.
import streamlit as st


def inject_global_theme():
    """Inject the complete CSS design system for the active theme."""
    # ── Load Material Icons ───────────────────────────────────────────
    st.markdown('<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">', unsafe_allow_html=True)

    theme = st.session_state.get("theme", "dark")
    is_dark = theme == "dark"

    # ── Decide which palette block to activate ──────────────────────────
    if is_dark:
        palette_css = """
  --bg-main: #0F172A;
  --bg-secondary: #1E293B;
  --bg-card: rgba(255,255,255,0.03);
  --bg-card-hover: rgba(255,255,255,0.06);
  --bg-card-solid: #1E293B;
  --bg-input: #0F172A;
  --bg-input-focus: #1E293B;
  --bg-bar-track: rgba(255,255,255,0.07);
  --bg-insight: rgba(255,255,255,0.02);
  --border: rgba(51,65,85,0.8);
  --border-hover: rgba(148,163,184,0.4);
  --text-primary: #FFFFFF;
  --text-secondary: #E2E8F0;
  --text-muted: #94A3B8;
  --text-faint: #64748B;
  --shadow-soft: 0 4px 24px rgba(0,0,0,0.35);
  --shadow-glow: 0 0 24px rgba(99,102,241,0.15);
  --sidebar-bg: rgba(15,23,42,0.85);
  --sidebar-border: rgba(51,65,85,0.5);
  --nav-link-color: #CBD5E1;
  --nav-link-hover-bg: rgba(255,255,255,0.08);
  --nav-link-hover-color: #F1F5F9;
  --nav-divider-color: rgba(255,255,255,0.08);
  --popover-bg: #1E293B;
  --popover-border: rgba(51,65,85,0.6);
  --btn-action-bg: #1E293B;
  --btn-action-border: rgba(51,65,85,0.5);
  --btn-action-color: #F1F5F9;
  --btn-action-hover-bg: #334155;
  --dataframe-bg: #1E293B;
  --dataframe-header: #334155;
  --dataframe-text: #CBD5E1;
  --brand-primary-text: #00E6F0;
  --badge-indigo-text: #818CF8;
  --badge-amber-text: #FBBF24;
"""
    else:
        palette_css = """
  --bg-main: #F9FAFB;
  --bg-secondary: #FFFFFF;
  --bg-card: rgba(255,255,255,0.9);
  --bg-card-hover: rgba(255,255,255,1);
  --bg-card-solid: #FFFFFF;
  --bg-input: rgba(0,0,0,0.03);
  --bg-bar-track: rgba(0,0,0,0.08);
  --bg-insight: rgba(99,102,241,0.04);
  --border: #E5E7EB;
  --border-hover: #D1D5DB;
  --text-primary: #111827;
  --text-secondary: #374151;
  --text-muted: #4B5563;
  --text-faint: #6B7280;
  --shadow-soft: 0 4px 24px rgba(0,0,0,0.06);
  --shadow-glow: 0 0 24px rgba(99,102,241,0.08);
  --sidebar-bg: rgba(255,255,255,0.92);
  --sidebar-border: #E5E7EB;
  --nav-link-color: #1E293B;
  --nav-link-hover-bg: rgba(99,102,241,0.06);
  --nav-link-hover-color: #111827;
  --nav-divider-color: #E5E7EB;
  --popover-bg: #FFFFFF;
  --popover-border: #E5E7EB;
  --btn-action-bg: #FFFFFF;
  --btn-action-border: #E5E7EB;
  --btn-action-color: #111827;
  --btn-action-hover-bg: #F3F4F6;
  --dataframe-bg: #FFFFFF;
  --dataframe-header: #F3F4F6;
  --dataframe-text: #374151;
  --brand-primary-text: #0284C7;
  --badge-indigo-text: #4F46E5;
  --badge-amber-text: #D97706;
"""

    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap');

/* ═══════════════════════════════════════════════════════════════
   DESIGN TOKENS — injected per-theme for reliability
   ═══════════════════════════════════════════════════════════════ */
:root {{
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --brand-primary: #00E6F0;
  --brand-secondary: #6366F1;
  --positive: #10B981;
  --negative: #EF4444;
  --neutral-sent: #6B7280;
  --accent-gradient: linear-gradient(135deg, #00E6F0, #6366F1);
  --shadow-accent: 0 4px 14px rgba(99,102,241,0.25);
  --radius: 16px;
  --radius-sm: 10px;
{palette_css}
}}

/* ═══════════════════════════════════════════════════════════════
   SMOOTH TRANSITION
   ═══════════════════════════════════════════════════════════════ */
.stApp, .stApp *, [data-testid="stSidebar"], [data-testid="stSidebar"] * {{
  transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease !important;
}}

/* ═══════════════════════════════════════════════════════════════
   BASE
   ═══════════════════════════════════════════════════════════════ */
html, body, [class*="css"] {{
  font-family: var(--font-sans) !important;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
  letter-spacing: -0.01em;
}}
.stApp {{
  background: var(--bg-main) !important;
  color: var(--text-secondary) !important;
}}

/* ═══════════════════════════════════════════════════════════════
   SIDEBAR
   ═══════════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {{
  background: var(--sidebar-bg) !important;
  backdrop-filter: blur(24px) saturate(180%) !important;
  -webkit-backdrop-filter: blur(24px) saturate(180%) !important;
  border-right: 1px solid var(--sidebar-border) !important;
  padding-top: 2.5rem !important;
}}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label, [data-testid="stSidebar"] div {{
  font-family: var(--font-sans) !important;
  color: var(--text-secondary) !important;
}}

/* ── Sidebar Collapse / Expand Button — FINAL FIX ── */

/* Step 1: Only hide the raw text span inside collapse buttons */
[data-testid="stSidebarCollapseControl"] [data-testid="stIconMaterial"],
[data-testid="collapsedControl"] [data-testid="stIconMaterial"] {{
  visibility: hidden !important;
  font-size: 0 !important;
  width: 0 !important;
  height: 0 !important;
  display: block !important;
}}

/* Step 2: Make the button itself position:relative for ::before */
[data-testid="stSidebarCollapseControl"] button,
[data-testid="collapsedControl"] button {{
  position: relative !important;
  overflow: visible !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
}}

/* Step 3: Inject « on the BUTTON (not container) when sidebar is open */
[data-testid="stSidebarCollapseControl"] button::before {{
  content: "«" !important;
  font-size: 22px !important;
  font-weight: 800 !important;
  font-family: Arial, sans-serif !important;
  color: #334155 !important;
  visibility: visible !important;
  display: block !important;
  position: absolute !important;
  top: 50% !important;
  left: 50% !important;
  transform: translate(-50%, -50%) !important;
  line-height: 1 !important;
  z-index: 9999 !important;
  pointer-events: none !important;
}}

/* Step 4: Inject » on the BUTTON when sidebar is closed */
[data-testid="collapsedControl"] button::before {{
  content: "»" !important;
  font-size: 22px !important;
  font-weight: 800 !important;
  font-family: Arial, sans-serif !important;
  color: #334155 !important;
  visibility: visible !important;
  position: absolute !important;
  top: 50% !important;
  left: 50% !important;
  transform: translate(-50%, -50%) !important;
  line-height: 1 !important;
  z-index: 9999 !important;
  pointer-events: none !important;
}}

/* Step 5: Hover effect */
[data-testid="stSidebarCollapseControl"] button:hover::before,
[data-testid="collapsedControl"] button:hover::before {{
  color: #6366F1 !important;
  text-shadow: 0 0 10px rgba(99, 102, 241, 0.4) !important;
  transform: translate(-50%, -50%) scale(1.2) !important;
}}

/* Hide Streamlit Tooltips */
[data-testid="stTooltipContent"] {{
  display: none !important;
}}

/* ═══════════════════════════════════════════════════════════════
   TYPOGRAPHY — Global text resets
   ═══════════════════════════════════════════════════════════════ */
html, body, [data-testid="stAppViewContainer"] {{
  font-family: 'Inter', sans-serif !important;
  color: var(--text-primary) !important;
}}

/* Force visibility for common text elements - essential for Light Mode */
h1, h2, h3, h4, h5, h6, p, span, label, li, strong, b {{
  color: var(--text-primary) !important;
}}

/* Explicitly target Light Mode backgrounds to ensure dark text */
{"" if is_dark else """
[data-testid="stHeader"], 
[data-testid="stSidebar"], 
[data-testid="stAppViewContainer"], 
[data-testid="stVerticalBlock"] span,
[data-testid="stMarkdownContainer"] p,
[data-testid="stWidgetLabel"] label {
    color: #111827 !important;
}
"""}
h1 {{ font-family: var(--font-sans) !important; font-weight: 800 !important; color: var(--text-primary) !important; letter-spacing: -0.04em !important; }}
.block-container h1 {{ font-size: 2.2rem !important; }}
.hero-title,
.stApp .hero-title,
[data-testid="stMarkdown"] .hero-title {{
  font-size: clamp(2rem, 4.5vw, 3.8rem) !important;
  letter-spacing: -0.03em !important;
  line-height: 1.08 !important;
  text-align: center !important;
  margin: 0 auto 1.2rem !important;
  max-width: 800px !important;
  width: 100% !important;
  color: var(--text-primary) !important;
}}
h2 {{ font-family: var(--font-sans) !important; font-size: 1.25rem !important; font-weight: 600 !important; color: var(--text-primary) !important; letter-spacing: -0.02em !important; }}
h3 {{ font-family: var(--font-sans) !important; font-size: 1rem !important; font-weight: 500 !important; color: var(--text-secondary) !important; }}
p, span, li {{ color: var(--text-secondary); }}
label {{ color: var(--text-secondary) !important; }}

/* ═══════════════════════════════════════════════════════════════
   METRIC CARDS
   ═══════════════════════════════════════════════════════════════ */
[data-testid="stMetricValue"] {{
  font-family: var(--font-sans) !important; font-size: 2.2rem !important; font-weight: 800 !important;
  color: var(--text-primary) !important; letter-spacing: -0.04em !important;
  transition: transform 0.3s cubic-bezier(0.34,1.56,0.64,1) !important;
}}
[data-testid="stMetricLabel"] {{
  font-size: 11.5px !important; font-weight: 600 !important; letter-spacing: 0.06em !important;
  text-transform: uppercase !important; color: var(--text-muted) !important;
}}
[data-testid="stMetricDelta"] {{ font-size: 13px !important; font-weight: 600 !important; }}
[data-testid="metric-container"] {{
  background: var(--bg-card) !important; border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important; padding: 1.5rem !important;
  backdrop-filter: blur(16px); box-shadow: var(--shadow-soft) !important;
  transition: all 0.35s cubic-bezier(0.25,0.8,0.25,1) !important;
  position: relative; overflow: hidden;
}}
[data-testid="metric-container"]::before {{
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: var(--accent-gradient); opacity: 0; transition: opacity 0.35s ease;
}}
[data-testid="metric-container"]:hover {{
  background: var(--bg-card-hover) !important; border-color: var(--border-hover) !important;
  transform: translateY(-3px); box-shadow: var(--shadow-glow) !important;
}}
[data-testid="metric-container"]:hover::before {{ opacity: 1; }}
[data-testid="metric-container"]:hover [data-testid="stMetricValue"] {{ transform: scale(1.03); }}

/* ═══════════════════════════════════════════════════════════════
   GLASS CARD
   ═══════════════════════════════════════════════════════════════ */
.glass-card {{
  background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius);
  backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
  box-shadow: var(--shadow-soft); transition: all 0.35s cubic-bezier(0.25,0.8,0.25,1);
  position: relative; overflow: hidden;
}}
.glass-card::before {{
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: var(--accent-gradient); opacity: 0; transition: opacity 0.35s ease;
}}
.glass-card:hover {{ border-color: var(--border-hover); box-shadow: var(--shadow-glow); }}
.glass-card:hover::before {{ opacity: 1; }}

/* ═══════════════════════════════════════════════════════════════
   TABS
   ═══════════════════════════════════════════════════════════════ */
[data-baseweb="tab-list"] {{ background: transparent !important; border-bottom: 1px solid var(--border) !important; gap: 1rem !important; }}
[data-baseweb="tab"] {{
  font-family: var(--font-sans) !important; font-size: 13.5px !important; font-weight: 500 !important;
  color: var(--text-muted) !important; padding: 12px 6px !important;
  border-bottom: 2px solid transparent !important; background: transparent !important;
  transition: color 0.25s ease !important;
}}
[data-baseweb="tab"]:hover {{ color: var(--text-secondary) !important; }}
[aria-selected="true"][data-baseweb="tab"] {{ color: var(--text-primary) !important; border-bottom: 2px solid var(--brand-primary) !important; font-weight: 600 !important; }}

/* ═══════════════════════════════════════════════════════════════
   BUTTONS
   ═══════════════════════════════════════════════════════════════ */
.stButton button {{
  font-family: var(--font-sans) !important; font-weight: 600 !important; font-size: 13.5px !important;
  border-radius: 12px !important; padding: 0.55rem 1.6rem !important;
  border: 1px solid var(--border) !important; background: var(--bg-card) !important;
  color: var(--text-secondary) !important;
  transition: all 0.25s cubic-bezier(0.25,0.8,0.25,1) !important;
  box-shadow: 0 2px 10px rgba(0,0,0,0.12) !important;
}}
.stButton button:hover {{
  background: var(--bg-card-hover) !important; border-color: var(--border-hover) !important;
  color: var(--text-primary) !important; transform: translateY(-1px); box-shadow: var(--shadow-soft) !important;
}}
.stButton button[kind="primary"] {{
  background: transparent !important;
  color: var(--brand-secondary) !important;
  border: 1px solid var(--brand-secondary) !important;
  font-weight: 700 !important;
  box-shadow: none !important;
}}
.stButton button[kind="primary"]:hover {{
  background: rgba(99,102,241,0.08) !important;
  box-shadow: 0 4px 12px rgba(99,102,241,0.2) !important;
}}
.stButton button[kind="primary"] * {{
  color: var(--brand-secondary) !important;
  fill: var(--brand-secondary) !important;
}}

/* ═══════════════════════════════════════════════════════════════
   INPUTS / SELECTS / SLIDERS
   ═══════════════════════════════════════════════════════════════ */
/* Safe Input Colors (No structural overrides) */
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea,
[data-baseweb="base-input"] input,
[data-baseweb="base-input"] textarea {{
  color: var(--text-primary) !important;
  font-family: var(--font-sans) !important;
  -webkit-text-fill-color: var(--text-primary) !important;
}}

/* Target the wrapper divs to override the dark mode bleeding */
div[data-baseweb="base-input"],
div[data-baseweb="input"],
div[data-baseweb="textarea"],
div[data-baseweb="select"] > div {{
  background-color: var(--bg-input) !important;
  border-color: var(--border) !important;
}}
[data-baseweb="select"] span,
[data-baseweb="select"] div,
[data-baseweb="select"] input {{
  color: var(--text-primary) !important;
  -webkit-text-fill-color: var(--text-primary) !important;
}}
[data-baseweb="select"] svg {{
  fill: var(--text-primary) !important;
  color: var(--text-primary) !important;
}}
[data-baseweb="select"] [data-baseweb="tag"] {{
  background: var(--bg-card-hover) !important;
  color: var(--text-primary) !important;
  border: 1px solid var(--border) !important;
}}
/* Aggressive Popover Override for Selectboxes */
[data-baseweb="popover"], 
[data-baseweb="popover"] *, 
div[role="listbox"],
div[role="listbox"] * {{
  background-color: var(--bg-card-solid) !important;
  color: var(--text-primary) !important;
}}
[data-baseweb="popover"] li:hover,
div[role="listbox"] li:hover {{
  background-color: var(--bg-card-hover) !important;
}}
[data-baseweb="popover"] [data-baseweb="menu"] {{
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  box-shadow: var(--shadow-soft) !important;
}}

/* Number Input Step Buttons (+ / -) */
[data-testid="stNumberInputStepUp"], [data-testid="stNumberInputStepDown"],
.stNumberInput button {{
  background-color: var(--bg-card-hover) !important;
  background: var(--bg-card-hover) !important;
  color: var(--text-primary) !important;
}}
.stNumberInput button svg {{
  fill: var(--text-primary) !important;
  color: var(--text-primary) !important;
}}
[data-baseweb="input"] input, [data-baseweb="textarea"] textarea {{
  background-color: var(--bg-input) !important;
  color: var(--text-primary) !important;
}}
[data-baseweb="input"] input:focus, [data-baseweb="textarea"] textarea:focus {{
  border-color: var(--brand-secondary) !important; box-shadow: 0 0 0 2px rgba(99,102,241,0.1) !important;
}}
[data-baseweb="select"] [data-baseweb="tag"] {{
  background: transparent !important;
  color: var(--text-primary) !important;
  border: 1px solid var(--border) !important;
}}
[data-baseweb="popover"] [data-baseweb="menu"] {{
  background: var(--popover-bg) !important; border: 1px solid var(--popover-border) !important;
  border-radius: 12px !important;
}}
[data-baseweb="popover"] [data-baseweb="menu"] li {{
  color: var(--text-primary) !important;
}}
[data-baseweb="popover"] [data-baseweb="menu"] li:hover {{
  background: var(--bg-card-hover) !important;
}}
.stSlider [data-baseweb="slider"] div[role="slider"] {{
  background: var(--text-primary) !important;
  box-shadow: 0 2px 8px rgba(0,0,0,0.4) !important;
}}
.stSlider [data-baseweb="slider"] > div {{
  background: var(--bg-bar-track) !important;
}}
.stSlider [data-baseweb="slider"] > div > div {{
  background: var(--brand-secondary) !important;
}}
.stSlider p {{ color: var(--text-secondary) !important; }}

/* ═══════════════════════════════════════════════════════════════
   DATA ELEMENTS
   ═══════════════════════════════════════════════════════════════ */
[data-testid="stDataFrame"] {{ border: 1px solid var(--border) !important; border-radius: var(--radius) !important; overflow: hidden; box-shadow: var(--shadow-soft) !important; }}

/* ── HTML Tables (st.table) ── */
.stTable {{
  background: var(--dataframe-bg) !important;
  border-radius: var(--radius) !important;
  overflow: hidden !important;
  border: 1px solid var(--border) !important;
  box-shadow: var(--shadow-soft) !important;
}}
.stTable table {{
  color: var(--dataframe-text) !important;
  width: 100% !important;
}}
.stTable th {{
  background-color: var(--dataframe-header) !important;
  color: var(--dataframe-text) !important;
  border-bottom: 1px solid var(--border) !important;
  border-right: 1px solid var(--border) !important;
  font-family: var(--font-sans) !important;
}}
.stTable td {{
  border-bottom: 1px solid var(--border) !important;
  border-right: 1px solid var(--border) !important;
  font-family: var(--font-sans) !important;
}}
.stTable th:last-child, .stTable td:last-child {{
  border-right: none !important;
}}
[data-testid="stExpander"] {{
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  background: var(--bg-card) !important;
  box-shadow: var(--shadow-soft) !important;
  overflow: hidden !important;
}}
[data-testid="stExpander"] summary {{
  background-color: var(--bg-secondary) !important;
  color: var(--text-primary) !important;
  padding: 0.5rem 1rem !important;
}}
[data-testid="stExpander"] summary:hover {{
  color: var(--brand-secondary) !important;
  background-color: var(--bg-card-hover) !important;
}}
[data-testid="stAlert"] {{ border-radius: 12px !important; border: 1px solid var(--border) !important; font-size: 13px !important; background: var(--bg-card) !important; }}
.stSelectbox label, .stMultiSelect label, .stDateInput label,
.stNumberInput label, .stTextInput label, .stTextArea label,
.stSlider label, .stRadio label, .stCheckbox label {{
  color: var(--text-secondary) !important; font-family: var(--font-sans) !important;
}}
[data-testid="stFileUploader"] {{ background: transparent !important; border: none !important; }}
[data-testid="stFileUploader"] label {{ color: var(--text-secondary) !important; }}
[data-testid="stFileUploader"] section {{ color: var(--text-muted) !important; padding: 0 !important; }}

/* ── Dropzone — no border box, just centered ── */
[data-testid="stFileUploaderDropzone"] {{
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 8px 0 !important;
  min-height: unset !important;
  height: auto !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
}}

/* ── Hide all instruction text ── */
[data-testid="stFileUploaderDropzoneInstructions"] {{
  display: none !important;
}}

/* ── Solid Blue Upload button — centered ── */
[data-testid="stFileUploaderDropzone"] button {{
  background: #3b82f6 !important;
  color: #ffffff !important;
  border: 1px solid #3b82f6 !important;
  border-radius: 10px !important;
  font-weight: 700 !important;
  font-family: var(--font-sans) !important;
  font-size: 14px !important;
  padding: 10px 32px !important;
  box-shadow: 0 4px 14px rgba(59, 130, 246, 0.3) !important;
  transition: all 0.2s ease !important;
  white-space: nowrap !important;
  margin: 0 auto !important;
}}
[data-testid="stFileUploaderDropzone"] button:hover {{
  background: #2563eb !important;
  border-color: #2563eb !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4) !important;
}}
[data-testid="stFileUploaderDropzone"] button * {{
  color: #ffffff !important;
  fill: #ffffff !important;
}}
[data-testid="stProgress"] > div > div > div > div {{
  background: var(--brand-secondary) !important;
}}

/* Toast & Snackbar */
[data-testid="stToast"] {{ background: var(--bg-card-solid) !important; border: 1px solid var(--border) !important; color: var(--text-primary) !important; }}
[data-testid="stToast"] p {{ color: var(--text-primary) !important; }}

/* Markdown elements */
[data-testid="stMarkdown"] p, [data-testid="stMarkdown"] span,
[data-testid="stMarkdown"] li, [data-testid="stMarkdown"] h1,
[data-testid="stMarkdown"] h2, [data-testid="stMarkdown"] h3 {{
  font-family: var(--font-sans) !important;
}}

/* Success/Error/Warning alerts */
[data-testid="stAlert"] p {{ color: inherit !important; }}

/* Download button */
.stDownloadButton button {{
  font-family: var(--font-sans) !important; font-weight: 600 !important;
  border-radius: 12px !important; border: 1px solid var(--border) !important;
  background: var(--bg-card) !important; color: var(--text-secondary) !important;
}}
.stDownloadButton button:hover {{
  background: var(--bg-card-hover) !important; border-color: var(--border-hover) !important;
  color: var(--text-primary) !important;
}}

/* ── MODALS / DIALOGS — Stable Visibility Fix ── */
div[role="dialog"] {{
  backdrop-filter: blur(8px) saturate(140%) !important;
  background-color: rgba(0,0,0,0.25) !important;
  z-index: 9999 !important;
}}


/* MODALS / DIALOGS — Keep existing for other parts */
div[role="dialog"] {{
  backdrop-filter: blur(10px) saturate(160%) !important;
  background-color: rgba(0,0,0,0.4) !important;
  z-index: 9999 !important;
}}

/* Ensure the main container doesn't shift */
.main .block-container {{
    max-width: 100% !important;
    padding-top: 5rem !important;
}}

[data-testid="stDialog"] > div:first-child > div:first-child {{
  background-color: var(--bg-secondary) !important;
  color: var(--text-primary) !important;
  border: 1px solid var(--border) !important;
  box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5) !important;
  border-radius: 28px !important;
  padding: 2rem !important;
  max-width: 550px !important;
  margin: 0 auto !important;
  animation: modalPop 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) both !important;
}}

@keyframes modalPop {{
  from {{ transform: scale(0.9) translateY(20px); opacity: 0; }}
  to   {{ transform: scale(1) translateY(0); opacity: 1; }}
}}

[data-testid="stDialog"] * {{
  color: var(--text-primary) !important;
}}

[data-testid="stDialog"] > div:first-child > div:first-child {{
  background-color: var(--bg-secondary) !important;
  color: var(--text-primary) !important;
  border: 1px solid var(--border) !important;
  box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5) !important;
  border-radius: 28px !important;
  padding: 2rem !important;
  max-width: 550px !important;
  margin: 0 auto !important;
  animation: modalPop 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) both !important;
}}

@keyframes modalPop {{
  from {{ transform: scale(0.9) translateY(20px); opacity: 0; }}
  to   {{ transform: scale(1) translateY(0); opacity: 1; }}
}}

[data-testid="stDialog"] * {{
  color: var(--text-primary) !important;
}}

/* ── CODE & KBD — Force readability in Light Mode ── */
code, kbd, tt, pre {{
  background-color: {"rgba(255,255,255,0.15)" if is_dark else "#F3F4F6"} !important;
  color: {"#00E6F0" if is_dark else "#111827"} !important;
  padding: 2px 8px !important;
  border-radius: 6px !important;
  font-family: 'Source Code Pro', monospace !important;
  border: 1px solid {"rgba(255,255,255,0.1)" if is_dark else "#E5E7EB"} !important;
  font-weight: 600 !important;
}}

/* Force dark text for metrics inside modals in Light Mode */
{"" if is_dark else """
[data-testid="stDialog"] [data-testid="metric-container"] *,
[data-testid="stDialog"] [data-testid="stMarkdownContainer"] *,
[data-testid="stDialog"] button p,
[data-testid="stDialog"] code,
[data-testid="stDialog"] kbd {
    color: #111827 !important;
}
"""}

/* ═══════════════════════════════════════════════════════════════
   SIDEBAR NAV
   ═══════════════════════════════════════════════════════════════ */
[data-testid="stSidebarNav"] {{ display: none !important; }}
[data-testid="stPageLink-NavLink"] {{
  display: flex !important; align-items: center !important; gap: 14px !important;
  padding: 11px 16px !important; border-radius: 12px !important; text-decoration: none !important;
  color: var(--nav-link-color) !important; font-family: var(--font-sans) !important;
  font-size: 14.5px !important; font-weight: 500 !important;
  transition: all 0.3s cubic-bezier(0.25,0.8,0.25,1) !important;
  margin-bottom: 5px !important; border: 1px solid transparent !important;
  background: transparent !important; width: 100% !important;
}}
[data-testid="stPageLink-NavLink"] p {{
  color: inherit !important; margin: 0 !important; padding: 0 !important;
  font-size: 14.5px !important; font-weight: 500 !important;
}}
[data-testid="stPageLink-NavLink"]:hover {{
  background: var(--nav-link-hover-bg) !important; color: var(--nav-link-hover-color) !important;
  transform: translateX(4px) !important; border-color: var(--nav-divider-color) !important;
}}
[data-testid="stPageLink-NavLink"][data-active="true"],
[data-testid="stPageLink-NavLink"][aria-current="page"] {{
  background: var(--nav-link-hover-bg) !important; color: var(--nav-link-hover-color) !important;
  border-color: var(--nav-divider-color) !important; font-weight: 700 !important;
}}
[data-testid="stPageLink-NavLink"][data-active="true"] p,
[data-testid="stPageLink-NavLink"][aria-current="page"] p {{
  font-weight: 700 !important; color: var(--nav-link-hover-color) !important;
}}

/* ═══════════════════════════════════════════════════════════════
   SCROLLBAR & DIVIDER
   ═══════════════════════════════════════════════════════════════ */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: var(--border-hover); border-radius: 6px; }}
::-webkit-scrollbar-thumb:hover {{ background: var(--text-muted); }}
hr {{ border-color: var(--border) !important; }}
[data-testid="stSpinner"] > div {{ border-top-color: var(--brand-secondary) !important; }}

/* ═══════════════════════════════════════════════════════════════
   SHIMMER
   ═══════════════════════════════════════════════════════════════ */
@keyframes shimmer {{
  0% {{ background-position: -200% 0; }}
  100% {{ background-position: 200% 0; }}
}}
.shimmer {{
  background: linear-gradient(90deg, var(--bg-card) 25%, var(--bg-card-hover) 50%, var(--bg-card) 75%);
  background-size: 200% 100%; animation: shimmer 1.8s ease-in-out infinite;
}}

/* ═══════════════════════════════════════════════════════════════
   MODALS / DIALOGS — Force theme awareness
   ═══════════════════════════════════════════════════════════════ */
[data-testid="stDialog"],
[data-testid="stModal"],
[role="dialog"],
.st-emotion-cache-12w0436 {{
  background-color: var(--bg-secondary) !important;
  color: var(--text-primary) !important;
  border: 1px solid var(--border) !important;
  box-shadow: var(--shadow-soft) !important;
}}

[data-testid="stDialog"] *,
[data-testid="stModal"] * {{
  color: var(--text-primary) !important;
}}

/* ── CODE & KBD — Force readability in Light Mode ── */
code, kbd, tt, pre {{
  background-color: {"rgba(255,255,255,0.1)" if is_dark else "rgba(0,0,0,0.05)"} !important;
  color: {"#00E6F0" if is_dark else "#111827"} !important;
  padding: 2px 6px !important;
  border-radius: 4px !important;
  font-family: 'Source Code Pro', monospace !important;
  border: 1px solid {"rgba(255,255,255,0.1)" if is_dark else "rgba(0,0,0,0.1)"} !important;
}}

/* Force dark text for metrics inside modals in Light Mode */
{"" if is_dark else """
[data-testid="stDialog"] [data-testid="metric-container"] *,
[data-testid="stDialog"] [data-testid="stMarkdownContainer"] *,
[data-testid="stDialog"] button p,
[data-testid="stDialog"] code,
[data-testid="stDialog"] kbd {
    color: #111827 !important;
    background-color: #F3F4F6 !important;
}
"""}

/* ═══════════════════════════════════════════════════════════════
   ANIMATIONS
   ═══════════════════════════════════════════════════════════════ */
section[data-testid="stMain"] > div:first-child {{
  animation: pageIn 0.65s cubic-bezier(0.16,1,0.3,1) both;
}}
@keyframes pageIn {{
  from {{ opacity: 0; transform: translateY(18px) scale(0.995); }}
  to   {{ opacity: 1; transform: translateY(0) scale(1); }}
}}
[data-testid="column"]:nth-child(1) [data-testid="metric-container"] {{ animation: fadeUp 0.6s 0.05s cubic-bezier(0.16,1,0.3,1) both; }}
[data-testid="column"]:nth-child(2) [data-testid="metric-container"] {{ animation: fadeUp 0.6s 0.12s cubic-bezier(0.16,1,0.3,1) both; }}
[data-testid="column"]:nth-child(3) [data-testid="metric-container"] {{ animation: fadeUp 0.6s 0.19s cubic-bezier(0.16,1,0.3,1) both; }}
[data-testid="column"]:nth-child(4) [data-testid="metric-container"] {{ animation: fadeUp 0.6s 0.26s cubic-bezier(0.16,1,0.3,1) both; }}
@keyframes fadeUp {{
  from {{ opacity: 0; transform: translateY(22px); }}
  to   {{ opacity: 1; transform: translateY(0); }}
}}
.glass-card {{ animation: cardIn 0.5s cubic-bezier(0.16,1,0.3,1) both; }}
@keyframes cardIn {{
  from {{ opacity: 0; transform: translateY(14px); }}
  to   {{ opacity: 1; transform: translateY(0); }}
}}
.pulse-dot {{
  display: inline-block; width: 8px; height: 8px; background: var(--brand-primary);
  border-radius: 50%; margin-right: 8px; animation: pulse 2s ease-in-out infinite;
}}
@keyframes pulse {{
  0%, 100% {{ box-shadow: 0 0 0 0 rgba(0,230,240,0.45); }}
  50%      {{ box-shadow: 0 0 0 8px rgba(0,230,240,0); }}
}}
.floating-badge {{ animation: float 4s ease-in-out infinite; }}
@keyframes float {{
  0%, 100% {{ transform: translateY(0); }}
  50%      {{ transform: translateY(-5px); }}
}}
@keyframes fadeInUp {{
  from {{ opacity: 0; transform: translateY(28px); }}
  to   {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes gradientShift {{
  0%   {{ background-position: 0% 50%; }}
  50%  {{ background-position: 100% 50%; }}
  100% {{ background-position: 0% 50%; }}
}}
.hero-animate    {{ animation: fadeInUp 0.8s cubic-bezier(0.16,1,0.3,1) both; }}
.hero-animate-d1 {{ animation: fadeInUp 0.8s cubic-bezier(0.16,1,0.3,1) 0.1s both; }}
.hero-animate-d2 {{ animation: fadeInUp 0.8s cubic-bezier(0.16,1,0.3,1) 0.2s both; }}
.hero-animate-d3 {{ animation: fadeInUp 0.8s cubic-bezier(0.16,1,0.3,1) 0.3s both; }}
.hero-animate-d4 {{ animation: fadeInUp 0.8s cubic-bezier(0.16,1,0.3,1) 0.4s both; }}
.hero-animate-d5 {{ animation: fadeInUp 0.8s cubic-bezier(0.16,1,0.3,1) 0.5s both; }}
.gradient-text {{
  display: inline-block;
  transform: translateX(15px);
  background: linear-gradient(135deg, var(--brand-primary-text) 0%, var(--badge-indigo-text) 50%, var(--brand-primary-text) 100%);
  background-size: 200% 200%; animation: gradientShift 4s ease infinite;
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}}

/* ═══════════════════════════════════════════════════════════════
   PLOTLY CHART CONTAINERS
   ═══════════════════════════════════════════════════════════════ */
[data-testid="stPlotlyChart"] {{
  border-radius: var(--radius) !important;
  overflow: hidden;
}}

/* ═══════════════════════════════════════════════════════════════
   RADIO / CHECKBOX (for theme toggle in popover)
   ═══════════════════════════════════════════════════════════════ */
[data-testid="stRadio"] label {{
  color: var(--text-primary) !important;
}}
/* ── THE FULLY FUNCTIONAL HIGH-CONTRAST FIX ── */

/* 1. Reset buttons to be solid, visible, AND clickable */
[data-testid="stSidebarHeader"] button,
[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"] {{
    background-repeat: no-repeat !important;
    background-position: center !important;
    background-size: 20px !important;
    opacity: 1 !important;
    visibility: visible !important;
    background-color: {"rgba(255,255,255,0.1)" if is_dark else "rgba(0,0,0,0.05)"} !important;
    border: 1px solid {"%2300E6F0" if is_dark else "%23000000"} !important;
    border-radius: 8px !important;
    min-width: 32px !important;
    min-height: 32px !important;
    pointer-events: auto !important; /* IMPORTANT: Let the button catch clicks */
    cursor: pointer !important;
    z-index: 999999 !important;
    overflow: hidden !important;
}}

/* 2. Make internal children invisible BUT don't use display:none (which breaks React events) */
[data-testid="stSidebarHeader"] button *,
[data-testid="stSidebarCollapseButton"] *,
[data-testid="collapsedControl"] * {{
    opacity: 0 !important;
    visibility: hidden !important;
    pointer-events: none !important; /* Clicks will 'fall through' to the button */
    width: 0 !important;
    height: 0 !important;
}}

/* 3. Inject the LEFT arrow (Collapse) */
[data-testid="stSidebarHeader"] button,
[data-testid="stSidebarCollapseButton"] {{
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='{("%2300E6F0" if is_dark else "%23000000")}'%3E%3Cpath d='M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z'/%3E%3C/svg%3E") !important;
}}

/* 4. Inject the RIGHT arrow (Expand) */
[data-testid="collapsedControl"] {{
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/xml' viewBox='0 0 24 24' fill='{("%2300E6F0" if is_dark else "%23000000")}'%3E%3Cpath d='M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z'/%3E%3C/svg%3E") !important;
}}

/* Hover effect */
[data-testid="stSidebarHeader"] button:hover,
[data-testid="stSidebarCollapseButton"]:hover,
[data-testid="collapsedControl"]:hover {{
    background-color: {"rgba(0,230,240,0.1)" if is_dark else "rgba(0,0,0,0.1)"} !important;
    background-size: 22px !important;
    transition: all 0.2s ease !important;
}}
</style>
""", unsafe_allow_html=True)



