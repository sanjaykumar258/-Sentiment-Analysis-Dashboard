# components/metrics_cards.py — Premium KPI counter cards with sparkline & accent glow
import streamlit as st
import random


def animated_metric(label, value, delta="", delta_type="neutral",
                    accent_color="#6EE7B7", animate_to=None, suffix=""):
    delta_colors = {"up": "#10B981", "down": "#EF4444", "neutral": "#6B7280"}
    delta_color = delta_colors.get(delta_type, "#6B7280")
    card_id = f"kpi_{label.replace(' ','_').replace('.','').lower()}"

    ac = accent_color.lstrip('#')
    r, g, b = int(ac[0:2], 16), int(ac[2:4], 16), int(ac[4:6], 16)

    if value == "" and animate_to is not None:
        is_int_val = isinstance(animate_to, int) or (isinstance(animate_to, float) and animate_to == int(animate_to))
        value = f"{int(animate_to)}{suffix}" if is_int_val else f"{animate_to:.1f}{suffix}"

    val_len = len(str(value))
    if val_len > 22:
        val_size, val_lh = "1.1rem", "1.3"
    elif val_len > 14:
        val_size, val_lh = "1.5rem", "1.1"
    else:
        val_size, val_lh = "2.2rem", "1"

    delta_text = delta if delta else "&nbsp;"
    delta_html = f'<div style="font-size:12px;margin-top:8px;font-family:var(--font-sans);font-weight:600;color:{delta_color};letter-spacing:-0.01em;">{delta_text}</div>'

    # Generate a mini sparkline SVG (decorative trend indicator)
    random.seed(hash(label) % 2**32)
    pts = [random.uniform(8, 28) for _ in range(8)]
    # Smooth upward bias for positive accents
    if accent_color in ("#10B981", "#6EE7B7"):
        pts = sorted(pts)
    sparkline_points = " ".join([f"{i*14},{32-p}" for i, p in enumerate(pts)])
    spark_svg = f"""
<svg width="98" height="32" viewBox="0 0 98 32" style="position:absolute;bottom:12px;right:14px;opacity:0.15;">
<polyline points="{sparkline_points}" fill="none" stroke="{accent_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""

    # Counter animation script
    counter_js = ""
    if animate_to is not None and isinstance(animate_to, (int, float)):
        is_int = isinstance(animate_to, int) or (isinstance(animate_to, float) and animate_to == int(animate_to))
        counter_js = f"""
<script>
(function(){{
  const el = document.getElementById('{card_id}_val');
  if(!el || el.dataset.animated) return;
  el.dataset.animated = '1';
  const target = {animate_to};
  const isInt = {'true' if is_int else 'false'};
  const suffix = '{suffix}';
  const duration = 1200;
  const start = performance.now();
  function update(now) {{
    const t = Math.min((now - start) / duration, 1);
    const ease = 1 - Math.pow(1 - t, 4);
    const current = target * ease;
    el.textContent = (isInt ? Math.round(current).toLocaleString() : current.toFixed(1)) + suffix;
    if (t < 1) requestAnimationFrame(update);
  }}
  el.textContent = isInt ? '0' : '0.0';
  requestAnimationFrame(update);
}})();
</script>"""

    st.markdown(f"""
<div class="glass-card" style="height:155px;display:flex;flex-direction:column;justify-content:center;padding:1.5rem;position:relative;overflow:hidden;cursor:default;" onmouseover="this.style.borderColor='rgba({r},{g},{b},0.35)';this.style.transform='translateY(-3px)';this.style.boxShadow='0 0 24px rgba({r},{g},{b},0.12)'" onmouseout="this.style.borderColor='var(--border)';this.style.transform='translateY(0)';this.style.boxShadow='var(--shadow-soft)'">
<div style="font-size:11px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;color:var(--text-muted);font-family:var(--font-sans);margin-bottom:8px;">{label}</div>
<div id="{card_id}_val" style="font-family:var(--font-sans);font-size:{val_size};font-weight:800;color:var(--text-primary);line-height:{val_lh};letter-spacing:-0.04em;word-break:break-word;">{value}</div>
{delta_html}
{spark_svg}
</div>
{counter_js}
""", unsafe_allow_html=True)
