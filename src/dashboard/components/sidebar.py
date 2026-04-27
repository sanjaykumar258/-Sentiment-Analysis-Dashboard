# components/sidebar.py — Premium sidebar with theme toggle + navigation
import streamlit as st
import pandas as pd


def render_sidebar(df: pd.DataFrame) -> pd.DataFrame:
    if "Timestamp" in df.columns:
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")


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

    # ── Sidebar Content ──
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

        # --- Push to bottom ---
        st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
        st.divider()


        # ── Theme Toggle (Custom UI) ──
        st.markdown(f'<p style="font-size:10px; color:{_nav_label_color}; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:8px; padding-left:4px;">Appearance</p>', unsafe_allow_html=True)
        
        t1, t2 = st.columns(2)
        with t1:
            if st.button("☀️ Light", key="theme_light", use_container_width=True, type="secondary" if is_dark else "primary"):
                st.session_state["theme"] = "light"
                st.rerun()
        with t2:
            if st.button("🌙 Dark", key="theme_dark", use_container_width=True, type="primary" if is_dark else "secondary"):
                st.session_state["theme"] = "dark"
                st.rerun()

        # ── User Profile & Sign Out ──
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        _user_name = st.session_state.get("user_name", "User")
        
        with st.container():
            st.markdown(f"""
            <div style="padding:10px; background:{_profile_bg}; border:1px solid {_profile_border}; border-radius:12px; margin-bottom:10px;">
                <div style="font-size:13px; font-weight:700; color:{_profile_name};">{_user_name}</div>
                <div style="font-size:10px; color:{_profile_role}; text-transform:uppercase;">Active Session</div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🚪 Sign Out", key="sign_out_btn", use_container_width=True):
                st.session_state["logged_in"] = False
                st.session_state["user_name"] = ""
                st.session_state["user_email"] = ""
                st.session_state["_last_auth_val"] = ""
                st.rerun()

    from src.dashboard.components.chatbot import render_floating_chatbot
    render_floating_chatbot(df)

    return df


