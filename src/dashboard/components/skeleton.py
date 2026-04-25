# components/skeleton.py — Theme-adaptive shimmer loading skeletons
import streamlit as st


def skeleton_cards(n=4):
    cols = st.columns(n)
    for col in cols:
        col.markdown("""
<div class="shimmer" style="height:100px;border-radius:16px;border:1px solid var(--border)"></div>
""", unsafe_allow_html=True)


def skeleton_chart(height=220):
    st.markdown(f"""
<div class="shimmer" style="height:{height}px;border-radius:16px;border:1px solid var(--border);margin-bottom:12px"></div>
""", unsafe_allow_html=True)
