# components/sidebar.py — Premium sidebar with theme toggle + navigation
import streamlit as st
import pandas as pd


def render_sidebar(df: pd.DataFrame) -> pd.DataFrame:
    if "Timestamp" in df.columns:
        df["Timestamp"] = pd.to_datetime(df["Timestamp"])

    if "theme" not in st.session_state:
        st.session_state["theme"] = "dark"

    is_dark = st.session_state["theme"] == "dark"

    # ── Shared Color Variables ──
    _toggle_icon = "☀️" if is_dark else "🌙"
    _brand_text_color = "#FFFFFF" if is_dark else "#1E293B"
    _version_color = "#00E6F0" if is_dark else "#6366F1"
    _nav_label_color = "#9CA3AF" if is_dark else "#64748B"
    _nav_link_color = "#D1D5DB" if is_dark else "#475569"
    _nav_link_hover_bg = "rgba(255,255,255,0.08)" if is_dark else "rgba(99,102,241,0.06)"
    _nav_link_hover_color = "#FFFFFF" if is_dark else "#1E293B"
    _profile_bg = "rgba(139,92,246,0.1)" if is_dark else "rgba(99,102,241,0.06)"
    _profile_border = "rgba(139,92,246,0.2)" if is_dark else "rgba(99,102,241,0.12)"
    _profile_name = "#FFF" if is_dark else "#1E293B"
    _profile_role = "#9CA3AF" if is_dark else "#64748B"
    _divider_color = "rgba(255,255,255,0.08)" if is_dark else "rgba(0,0,0,0.06)"
    _toggle_bg = "rgba(255,255,255,0.06)" if is_dark else "rgba(0,0,0,0.04)"
    _toggle_border = "rgba(255,255,255,0.1)" if is_dark else "rgba(0,0,0,0.08)"

    # ── Top Right Action Bar (Foolproof Fixed Layout) ──
    # Hardcode colors per theme — popover portals live outside :root scope
    _popover_bg     = "#1E293B"   if is_dark else "#FFFFFF"
    _popover_border = "rgba(51,65,85,0.6)" if is_dark else "#E5E7EB"
    _popover_text   = "#F1F5F9"   if is_dark else "#111827"
    _popover_muted  = "#94A3B8"   if is_dark else "#9CA3AF"
    _btn_bg         = "#1E293B"   if is_dark else "#FFFFFF"
    _btn_border     = "rgba(51,65,85,0.5)" if is_dark else "#E5E7EB"
    _btn_color      = "#F1F5F9"   if is_dark else "#374151"
    _btn_hover_bg   = "#334155"   if is_dark else "#F3F4F6"
    _radio_color    = "#CBD5E1"   if is_dark else "#374151"

    st.markdown(f"""
        <style>
        /* Target ONLY the column block containing our unique marker */
        div[data-testid="stHorizontalBlock"]:has(#action-bar-marker) {{
            position: fixed !important;
            top: 65px !important;
            right: 24px !important;
            z-index: 99999 !important;
            width: fit-content !important;
            display: flex !important;
            align-items: center !important;
            gap: 12px !important;
            background: transparent !important;
        }}
        
        /* Force all columns to same height & center vertically */
        div[data-testid="stHorizontalBlock"]:has(#action-bar-marker) > div[data-testid="column"] {{
            width: fit-content !important;
            flex: 0 0 auto !important;
            min-width: 0 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            padding: 0 !important;
            margin: 0 !important;
            gap: 0 !important;
            height: 42px !important;
        }}

        /* Completely collapse the FIRST column (marker-only) */
        div[data-testid="stHorizontalBlock"]:has(#action-bar-marker) > div[data-testid="column"]:first-child {{
            width: 0 !important;
            height: 0 !important;
            min-width: 0 !important;
            max-width: 0 !important;
            overflow: hidden !important;
            padding: 0 !important;
            margin: 0 !important;
            flex: 0 0 0px !important;
        }}

        /* Zero out ALL nested wrapper divs so nothing adds extra spacing */
        div[data-testid="stHorizontalBlock"]:has(#action-bar-marker) > div[data-testid="column"] > div,
        div[data-testid="stHorizontalBlock"]:has(#action-bar-marker) > div[data-testid="column"] > div > div,
        div[data-testid="stHorizontalBlock"]:has(#action-bar-marker) > div[data-testid="column"] > div > div > div {{
            display: flex !important;
            align-items: center !important;
            padding: 0 !important;
            margin: 0 !important;
            gap: 0 !important;
            width: fit-content !important;
            min-height: 0 !important;
        }}

        /* Zero out the marker span */
        #action-bar-marker {{
            display: block !important;
            width: 0 !important;
            height: 0 !important;
            line-height: 0 !important;
            font-size: 0 !important;
            overflow: hidden !important;
            position: absolute !important;
            pointer-events: none !important;
            margin: 0 !important;
            padding: 0 !important;
        }}

        /* Target ALL buttons inside the action bar */
        div[data-testid="stHorizontalBlock"]:has(#action-bar-marker) button,
        div[data-testid="stHorizontalBlock"]:has(#action-bar-marker) button[data-testid="baseButton-secondary"] {{
            border-radius: 12px !important;
            background-color: {_btn_bg} !important;
            background: {_btn_bg} !important;
            border: 1px solid {_btn_border} !important;
            color: {_btn_color} !important;
            font-size: 16px !important;
            font-weight: 600 !important;
            height: 42px !important;
            min-height: 42px !important;
            max-height: 42px !important;
            padding: 0 12px 0 16px !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.12) !important;
            transition: all 0.2s ease !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            gap: 6px !important;
            margin: 0 !important;
        }}
        div[data-testid="stHorizontalBlock"]:has(#action-bar-marker) button:hover {{
            background-color: {_btn_hover_bg} !important;
            background: {_btn_hover_bg} !important;
            transform: translateY(-1px) !important;
        }}
        /* Icon alignment inside buttons */
        div[data-testid="stHorizontalBlock"]:has(#action-bar-marker) button span,
        div[data-testid="stHorizontalBlock"]:has(#action-bar-marker) button svg {{
            color: {_btn_color} !important;
            fill: {_btn_color} !important;
            vertical-align: middle !important;
            line-height: 1 !important;
            display: flex !important;
            align-items: center !important;
            margin: 0 !important;
            padding: 0 !important;
        }}
        
        /* Popover dropdown — hardcoded per theme */
        div[data-testid="stPopoverBody"] {{
            width: 220px !important;
            padding: 16px !important;
            border-radius: 16px !important;
            background-color: {_popover_bg} !important;
            border: 1px solid {_popover_border} !important;
            box-shadow: 0 8px 32px rgba(0,0,0,0.18) !important;
        }}
        div[data-testid="stPopoverBody"] p,
        div[data-testid="stPopoverBody"] span,
        div[data-testid="stPopoverBody"] label,
        div[data-testid="stPopoverBody"] div {{
            color: {_popover_text} !important;
            background-color: transparent !important;
        }}
        div[data-testid="stPopoverBody"] [data-testid="stRadio"] label {{
            color: {_radio_color} !important;
        }}
        /* Radio container background */
        div[data-testid="stPopoverBody"] > div,
        div[data-testid="stPopoverBody"] [data-testid="stVerticalBlock"],
        div[data-testid="stPopoverBody"] [data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: {_popover_bg} !important;
        }}
        </style>
    """, unsafe_allow_html=True)

    
    # Render the action bar: marker in a hidden column, buttons in equal columns
    _c_marker, _c_theme, _c_user = st.columns([1, 1, 1])
    
    with _c_marker:
        st.markdown("<span id='action-bar-marker' style='display:block;width:0;height:0;overflow:hidden;position:absolute;'></span>", unsafe_allow_html=True)

    with _c_theme:
        theme_icon = ":material/dark_mode:" if is_dark else ":material/light_mode:"
        with st.popover(" ", icon=theme_icon):
            st.markdown("<p style='font-size:12.5px; font-weight:700; margin-bottom:8px; color:var(--text-muted); margin-top:0;'>Theme Preference</p>", unsafe_allow_html=True)
            theme_modes = ["dark", "light", "system"]
            current_theme = st.session_state.get("theme", "dark")
            if current_theme not in theme_modes:
                current_theme = "dark"
                
            theme_choice = st.radio(
                "Theme", 
                ["Dark", "Light", "System"], 
                index=theme_modes.index(current_theme),
                label_visibility="collapsed"
            )
            
            if theme_choice.lower() != current_theme:
                st.session_state["theme"] = theme_choice.lower()
                st.rerun()

    with _c_user:
        _user_name = st.session_state.get("user_name", "User")
        _user_email = st.session_state.get("user_email", "")
        with st.popover(" ", icon=":material/account_circle:"):
            st.markdown(f"""
            <div style="text-align:center; padding-bottom:14px; border-bottom:1px solid {_divider_color}; margin-bottom:14px; margin-top:0;">
                <div style="font-size:15px; font-weight:700; color:{_profile_name};">{_user_name}</div>
                <div style="font-size:11px; color:{_profile_role}; text-transform:uppercase; letter-spacing:0.04em; margin-top:4px;">{_user_email}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🚪 Sign out", use_container_width=True):
                st.session_state["logged_in"] = False
                st.session_state["user_name"] = ""
                st.session_state["user_email"] = ""
                st.session_state["_last_auth_val"] = ""
                st.rerun()

    with st.sidebar:
        # ── Brand row ──

        st.markdown(f"""
<div style="padding:0.5rem 0.5rem 1.2rem;border-bottom:1px solid {_divider_color};margin-bottom:1.2rem;">
<div style="display:flex;align-items:center;justify-content:space-between;">
<div style="display:flex;align-items:center;gap:14px;">
<div style="width:40px;height:40px;background:linear-gradient(135deg,#00E6F0,#6366F1);border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:18px;box-shadow:0 4px 15px rgba(99,102,241,0.35), inset 0 1px 2px rgba(255,255,255,0.2);">📊</div>
<div>
<span style="font-family:var(--font-sans);font-weight:800;font-size:17px;color:{_brand_text_color};letter-spacing:-0.03em;display:block;">SentiIntel</span>
<span style="font-size:10.5px;color:{_version_color};font-family:var(--font-sans);font-weight:700;text-transform:uppercase;letter-spacing:0.1em;">v4.0 Pro</span>
</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)


        # ── Navigation section ──
        st.markdown(
            f'<p style="font-size:10.5px;color:{_nav_label_color};font-weight:700;letter-spacing:0.12em;text-transform:uppercase;font-family:var(--font-sans);margin:0.75rem 0 0.5rem;padding-left:8px;">Navigation</p>',
            unsafe_allow_html=True,
        )

        nav_items = [
            ("🏠", "Home", "src/dashboard/app.py"),
            ("📊", "Dashboard", "pages/1_overview.py"),
            ("🔍", "Platform Analysis", "pages/2_platform_analysis.py"),
            ("🤖", "Live Predictor", "pages/3_live_predictor.py"),
            ("⚡", "Benchmarking", "pages/4_benchmarking.py"),
            ("🧠", "Model Insights", "pages/5_model_insights.py"),
            ("📁", "Export Reports", "pages/6_export.py"),
        ]

        import inspect
        import os
        try:
            caller_file = inspect.stack()[1].filename
            caller_basename = os.path.basename(caller_file)
        except:
            caller_basename = ""

        active_label = None

        for icon, label, page_path in nav_items:
            page_basename = os.path.basename(page_path)
            if page_basename == caller_basename:
                active_label = label

            try:
                st.page_link(page_path, label=label, icon=icon)
            except Exception as e:
                # Fallback if src/dashboard/app.py fails for home
                if label == "Home":
                    try:
                        st.page_link("app.py", label=label, icon=icon)
                    except Exception as e2:
                        st.error(f"Error loading {label}: {e2}")
                else:
                    st.error(f"Error loading {label}: {e}")

        if active_label:
            import streamlit.components.v1 as components
            components.html(f"""
            <script>
                const doc = window.parent.document;
                const links = doc.querySelectorAll('a[data-testid="stPageLink-NavLink"]');
                links.forEach(link => {{
                    const p = link.querySelector('p');
                    if(p && p.innerText.trim() === "{active_label}") {{
                        link.setAttribute('data-active', 'true');
                    }} else {{
                        link.removeAttribute('data-active');
                    }}
                }});
            </script>
            """, height=0)

    from src.dashboard.components.chatbot import render_floating_chatbot
    render_floating_chatbot(df)

    return df

