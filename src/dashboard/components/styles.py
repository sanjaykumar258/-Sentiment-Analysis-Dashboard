# components/styles.py — Premium design system with dark / light theme support
import streamlit as st

# ─── Theme helpers ────────────────────────────────────────────────────

def get_theme() -> str:
    """Return the active theme name ('dark' or 'light')."""
    return st.session_state.get("theme", "dark")


def is_dark() -> bool:
    return get_theme() == "dark"


# ─── Plotly layouts ───────────────────────────────────────────────────

_PLOTLY_BASE = dict(
    margin=dict(l=0, r=0, t=36, b=0),
    transition=dict(duration=600, easing="cubic-in-out"),
)

PLOTLY_LAYOUT = dict(
    **_PLOTLY_BASE,
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#A1A1AA", size=12),
    title_font=dict(family="Inter, sans-serif", color="#FFFFFF", size=15),
    xaxis=dict(gridcolor="rgba(255,255,255,0.04)", linecolor="rgba(255,255,255,0.06)", tickfont=dict(size=11)),
    yaxis=dict(gridcolor="rgba(255,255,255,0.04)", linecolor="rgba(255,255,255,0.06)", tickfont=dict(size=11)),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(255,255,255,0.06)", borderwidth=1, font=dict(size=11)),
    hoverlabel=dict(bgcolor="#0D0F16", bordercolor="rgba(255,255,255,0.12)", font=dict(family="Inter", size=12)),
)

PLOTLY_LAYOUT_LIGHT = dict(
    **_PLOTLY_BASE,
    template="plotly_white",
    paper_bgcolor="rgba(255,255,255,0)",
    plot_bgcolor="rgba(255,255,255,0)",
    font=dict(family="Inter, sans-serif", color="#64748B", size=12),
    title_font=dict(family="Inter, sans-serif", color="#1E293B", size=15),
    xaxis=dict(gridcolor="rgba(0,0,0,0.06)", linecolor="rgba(0,0,0,0.08)", tickfont=dict(size=11, color="#64748B")),
    yaxis=dict(gridcolor="rgba(0,0,0,0.06)", linecolor="rgba(0,0,0,0.08)", tickfont=dict(size=11, color="#64748B")),
    legend=dict(bgcolor="rgba(255,255,255,0)", bordercolor="rgba(0,0,0,0.08)", borderwidth=1, font=dict(size=11, color="#475569")),
    hoverlabel=dict(bgcolor="#FFFFFF", bordercolor="rgba(0,0,0,0.1)", font=dict(family="Inter", size=12, color="#1E293B")),
)


def get_plotly_layout() -> dict:
    """Return the Plotly layout dict for the active theme."""
    return PLOTLY_LAYOUT if is_dark() else PLOTLY_LAYOUT_LIGHT


# ─── Color tokens ─────────────────────────────────────────────────────

COLOR_MAP = {"Positive": "#10B981", "Negative": "#EF4444", "Neutral": "#6B7280"}
PLATFORM_COLORS = {
    "Instagram": "#E1306C", "TikTok": "#69C9D0", "Twitter": "#1DA1F2",
    "YouTube":   "#FF0000", "LinkedIn": "#0077B5", "Facebook": "#1877F2",
}
ACCENT  = "#00E6F0"
ACCENT2 = "#6366F1"

DAY_MAP = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday",
           4: "Friday", 5: "Saturday", 6: "Sunday"}


# ─── Component helpers ────────────────────────────────────────────────

def page_header(icon: str, title: str, subtitle: str):
    st.markdown(f"""
<div style="padding:1.8rem 0 1.2rem;border-bottom:1px solid var(--border);margin-bottom:1.8rem;">
<div style="display:flex;align-items:center;gap:14px;margin-bottom:8px;">
<div style="width:42px;height:42px;background:var(--accent-gradient);border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:1.3rem;box-shadow:var(--shadow-accent);">{icon}</div>
<h1 style="margin:0;font-family:var(--font-sans);font-size:1.65rem;font-weight:700;color:var(--text-primary);letter-spacing:-0.03em;">{title}</h1>
</div>
<p style="margin:0;font-size:13.5px;color:var(--text-muted);font-family:var(--font-sans);padding-left:56px;">{subtitle}</p>
</div>
""", unsafe_allow_html=True)


def card(content_html: str, padding: str = "1.5rem"):
    st.markdown(f"""
<div class="glass-card" style="padding:{padding};margin-bottom:1rem;">
{content_html}
</div>
""", unsafe_allow_html=True)


def sentiment_badge(label: str):
    config = {
        "Positive": ("#10B981", "rgba(16,185,129,0.12)", "▲ Positive"),
        "Negative": ("#EF4444", "rgba(239,68,68,0.12)", "▼ Negative"),
        "Neutral":  ("#6B7280", "rgba(107,114,128,0.12)", "● Neutral"),
    }
    color, bg, text = config.get(label, ("#6B7280", "rgba(107,114,128,0.1)", label))
    st.markdown(f"""
<div class="floating-badge" style="display:inline-flex;align-items:center;gap:10px;background:{bg};border:1px solid {color}40;border-radius:100px;padding:12px 28px;margin:1rem 0;backdrop-filter:blur(8px);">
<span style="font-family:var(--font-sans);font-size:1.25rem;font-weight:700;color:{color};letter-spacing:-0.02em;">{text}</span>
</div>
""", unsafe_allow_html=True)


def confidence_bar(value: float, label: str = "Confidence"):
    pct = round(value * 100, 1)
    color = "#10B981" if value > 0.7 else "#FBBF24" if value > 0.4 else "#EF4444"
    st.markdown(f"""
<div style="margin:0.75rem 0;">
<div style="display:flex;justify-content:space-between;margin-bottom:6px;">
<span style="font-size:12px;color:var(--text-muted);font-weight:600;text-transform:uppercase;letter-spacing:0.05em;font-family:var(--font-sans);">{label}</span>
<span style="font-family:var(--font-sans);font-size:1rem;font-weight:700;color:{color};">{pct}%</span>
</div>
<div style="height:8px;background:var(--bg-bar-track);border-radius:100px;overflow:hidden;">
<div style="height:100%;width:{pct}%;background:linear-gradient(90deg, {color}80, {color});border-radius:100px;transition:width 0.6s ease;"></div>
</div>
</div>
""", unsafe_allow_html=True)


def animated_confidence_bar(value: float, label: str = "Confidence", delay_ms: int = 0):
    pct = round(value * 100, 1)
    color = "#10B981" if value > 0.7 else "#FBBF24" if value > 0.4 else "#EF4444"
    bar_id = f"bar_{label.replace(' ','_').lower()}_{delay_ms}"
    st.markdown(f"""
<div style="margin:0.75rem 0;">
<div style="display:flex;justify-content:space-between;margin-bottom:5px">
<span style="font-size:11px;color:var(--text-muted);font-weight:600;text-transform:uppercase;letter-spacing:0.05em;font-family:var(--font-sans)">{label}</span>
<span style="font-family:var(--font-sans);font-size:0.95rem;font-weight:700;color:{color}">{pct}%</span>
</div>
<div style="height:8px;background:var(--bg-bar-track);border-radius:100px;overflow:hidden">
<div id="{bar_id}" style="height:100%;width:{pct}%;background:linear-gradient(90deg,{color}80,{color});border-radius:100px;transition:width 1.1s cubic-bezier(0.34,1.56,0.64,1)"></div>
</div>
</div>
""", unsafe_allow_html=True)


def section_title(text: str, sub: str = ""):
    sub_html = f"<p style='font-size:12px;color:var(--text-muted);margin:4px 0 0 14px;font-family:var(--font-sans);'>{sub}</p>" if sub else ""
    st.markdown(f"""
<div style="margin:1.8rem 0 1rem;">
<div style="display:flex;align-items:center;gap:10px;">
<div style="width:4px;height:20px;background:var(--accent-gradient);border-radius:3px;flex-shrink:0;"></div>
<span style="font-family:var(--font-sans);font-size:1.05rem;font-weight:600;color:var(--text-primary);">{text}</span>
</div>
{sub_html}
</div>
""", unsafe_allow_html=True)


def insight_caption(text: str):
    st.markdown(f"""
<div style="display:flex;align-items:flex-start;gap:8px;margin-top:8px;padding:10px 14px;background:var(--bg-insight);border-radius:10px;border:1px solid var(--border);">
<span style="font-size:14px;flex-shrink:0;margin-top:1px;">💡</span>
<p style="font-size:12.5px;color:var(--text-secondary);font-family:var(--font-sans);margin:0;line-height:1.5;">
{text}
</p>
</div>
""", unsafe_allow_html=True)


# ─── Theme-aware chart helpers ────────────────────────────────────────

def get_heatmap_colorscale():
    """Return a colorscale tuple appropriate for the active theme."""
    if is_dark():
        return [[0, "#0F172A"], [0.3, "#064E3B"], [0.6, "#065F46"], [1.0, "#6EE7B7"]]
    else:
        return [[0, "#F0FDF4"], [0.3, "#A7F3D0"], [0.6, "#34D399"], [1.0, "#059669"]]


def get_heatmap_text_color():
    """Return text color for heatmap cells."""
    return "#F1F5F9" if is_dark() else "#1E293B"


def get_confusion_colorscale():
    """Return a colorscale for confusion matrices."""
    if is_dark():
        return [[0, "#0F172A"], [0.3, "#1E1B4B"], [0.6, "#3730A3"], [1.0, "#818CF8"]]
    else:
        return [[0, "#EEF2FF"], [0.3, "#C7D2FE"], [0.6, "#818CF8"], [1.0, "#4F46E5"]]


def get_missing_colorscale():
    """Return a colorscale for missing-values bar charts."""
    if is_dark():
        return ["#0F172A", "#EF4444"]
    else:
        return ["#FEE2E2", "#EF4444"]


def get_polar_grid_color():
    """Return grid color for polar/radar charts."""
    return "rgba(255,255,255,0.06)" if is_dark() else "rgba(0,0,0,0.08)"


def get_polar_line_color():
    """Return angular axis line color for polar/radar charts."""
    return "rgba(255,255,255,0.1)" if is_dark() else "rgba(0,0,0,0.1)"


def get_polar_tick_color():
    """Return tick font color for polar/radar charts."""
    return "#64748B" if is_dark() else "#94A3B8"

