# Legacy compatibility — re-exports from new design system location
from src.dashboard.components.styles import (
    PLOTLY_LAYOUT,
    PLOTLY_LAYOUT_LIGHT,
    COLOR_MAP,
    PLATFORM_COLORS,
    ACCENT,
    ACCENT2,
    DAY_MAP,
    page_header,
    card,
    sentiment_badge,
    confidence_bar,
    section_title,
    insight_caption,
    get_theme,
    is_dark,
    get_plotly_layout,
)

# Legacy names for backwards compatibility
PLOTLY_TEMPLATE = "plotly_dark"


def get_custom_css():
    """Legacy CSS function — global CSS is now injected in app.py."""
    return ""
