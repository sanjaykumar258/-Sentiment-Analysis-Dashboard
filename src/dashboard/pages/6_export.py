import pathlib, sys, os
# --- Fix for Streamlit Cloud ModuleNotFoundError ---
current_dir = pathlib.Path(__file__).parent.resolve()
root_dir = current_dir.parents[2] # Go up: pages -> dashboard -> root
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import streamlit as st
import pandas as pd
import json
import os
import base64
from io import BytesIO
import matplotlib.pyplot as plt
from fpdf import FPDF
import datetime
from src.dashboard.components.styles import page_header, section_title, card, is_dark
from src.dashboard.components.sidebar import render_sidebar
from src.dashboard.components.particles import inject_particle_background

st.set_page_config(page_title="Export & Reporting", layout="wide")
if not st.session_state.get("logged_in", False):
    st.switch_page("app.py")
inject_particle_background()
from src.dashboard.components.theme_provider import inject_global_theme
inject_global_theme()


@st.cache_data(ttl=300)
def load_data():
    return pd.read_parquet("data/processed/processed_data.parquet")


df_raw = None
try:
    df_raw = load_data()
except FileNotFoundError:
    pass

# Always render sidebar first so chatbot persists
render_sidebar(df_raw if df_raw is not None else pd.DataFrame())

if df_raw is None:
    st.error("⚠️ Processed data not found. Please go to the Home page to upload a dataset.")
else:
    def main_page(df_raw):

        from src.dashboard.components.filters import render_filters
        df = df_raw  # Already rendered sidebar above
        page_header("📁", "Export & Reporting", "Download filtered datasets or generate automated PDF reports.")
        df = render_filters(df)

        # ── CSV Export ────────────────────────────────────────────────────────
        section_title("Data export", "Download the currently filtered dataset")

        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown(f"""
        <div class="glass-card" style="padding:1.5rem;">
        <p style="font-size:14px;color:var(--text-secondary);font-family:var(--font-sans);margin:0 0 10px;">
        Ready to export <b style="color:var(--text-primary);">{len(df):,}</b> rows based on your current sidebar filters.
        </p>
        <p style="font-size:12px;color:var(--text-muted);font-family:var(--font-sans);margin:0;">
        Format: CSV (Comma-separated values)<br>
        Includes: All 18 feature columns + Sentiment label
        </p>
        </div>
        """, unsafe_allow_html=True)

        with c2:
            @st.cache_data(ttl=60)
            def convert_df(dataframe):
                return dataframe.to_csv(index=False).encode('utf-8')

            csv = convert_df(df)
            st.markdown("<br>", unsafe_allow_html=True)
            st.download_button(
                label="⬇️ Download CSV",
                data=csv,
                file_name="sentiment_data_export.csv",
                mime="text/csv",
                use_container_width=True,
                type="primary"
            )

        st.divider()

        # ── PDF Report Generation ─────────────────────────────────────────────
        section_title("Automated reporting", "Generate a PDF summary of the current view")

        report_title = st.text_input("Report title", "Sentiment Analysis Summary Report")
        report_notes = st.text_area("Executive summary / Notes",
                                     "The overall sentiment remains strongly positive. "
                                     "Key drivers include the recent product launch campaign on Instagram and TikTok.",
                                     height=100)

        if st.button("📄 Generate PDF report", type="primary"):
            with st.spinner("Compiling charts and generating PDF..."):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 18)
                pdf.cell(0, 15, report_title, 0, 1, 'C')

                pdf.set_font("Arial", '', 10)
                pdf.cell(0, 10, f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1, 'C')
                pdf.ln(5)

                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 10, "Executive Summary", 0, 1)
                pdf.set_font("Arial", '', 11)
                pdf.multi_cell(0, 8, report_notes)
                pdf.ln(10)

                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 10, "Key Metrics (Filtered Data)", 0, 1)
                pdf.set_font("Arial", '', 11)

                total = len(df)
                pos_pct = round(len(df[df.Sentiment == "Positive"]) / total * 100, 1) if total else 0
                avg_eng = round(df["Engagement_Rate"].mean(), 2) if total else 0

                pdf.cell(0, 8, f"Total Posts Analyzed: {total:,}", 0, 1)
                pdf.cell(0, 8, f"Positive Sentiment: {pos_pct}%", 0, 1)
                pdf.cell(0, 8, f"Average Engagement Rate: {avg_eng}%", 0, 1)
                pdf.ln(10)

                fig, ax = plt.subplots(figsize=(6, 4))
                sent_counts = df["Sentiment"].value_counts()
                colors = ['#10B981' if x == 'Positive' else '#EF4444' if x == 'Negative' else '#6B7280' for x in sent_counts.index]
                ax.pie(sent_counts, labels=sent_counts.index, autopct='%1.1f%%', colors=colors, startangle=90)
                ax.axis('equal')
                plt.title("Sentiment Distribution")

                img_buf = BytesIO()
                plt.savefig(img_buf, format='png', bbox_inches='tight')
                plt.close(fig)

                # Write to a temporary file
                temp_img_path = "temp_chart.png"
                with open(temp_img_path, "wb") as f:
                    f.write(img_buf.getvalue())

                pdf.image(temp_img_path, w=120)
                os.remove(temp_img_path)

                pdf_bytes = bytes(pdf.output())

            st.success("Report generated successfully!")
            st.download_button(
                label="⬇️ Download PDF",
                data=pdf_bytes,
                file_name="sentiment_report.pdf",
                mime="application/pdf",
                use_container_width=True
            )

    main_page(df_raw)
