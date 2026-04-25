"""Generate project documentation PDF with embedded screenshots."""
import os
from fpdf import FPDF

class DocPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "Sentiment Intelligence Dashboard - Project Documentation", 0, 1, "C")
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", 0, 0, "C")

    def chapter_title(self, title):
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(30, 30, 80)
        self.cell(0, 12, title, 0, 1)
        self.set_draw_color(99, 102, 241)
        self.set_line_width(0.8)
        self.line(10, self.get_y(), 80, self.get_y())
        self.ln(6)

    def section_title(self, title):
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(50, 50, 100)
        self.cell(0, 10, title, 0, 1)
        self.ln(2)

    def body_text(self, text):
        self.set_font("Helvetica", "", 11)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 7, text)
        self.ln(3)

    def bullet(self, text):
        self.set_font("Helvetica", "", 11)
        self.set_text_color(40, 40, 40)
        self.cell(6, 7, "-", 0, 0)
        self.multi_cell(180, 7, text)

    def add_image_safe(self, path, w=170):
        if os.path.exists(path):
            self.image(path, x=20, w=w)
            self.ln(6)
        else:
            self.body_text(f"[Image not found: {path}]")

    def table_row(self, cols, widths, bold=False):
        self.set_font("Helvetica", "B" if bold else "", 10)
        h = 8
        for i, col in enumerate(cols):
            self.cell(widths[i], h, str(col), 1, 0, "C" if bold else "L")
        self.ln(h)


def generate():
    img = "docs/images"
    pdf = DocPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)

    # ── Cover Page ──
    pdf.add_page()
    pdf.ln(40)
    pdf.set_font("Helvetica", "B", 28)
    pdf.set_text_color(30, 30, 80)
    pdf.cell(0, 15, "Sentiment Intelligence", 0, 1, "C")
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(99, 102, 241)
    pdf.cell(0, 12, "Dashboard", 0, 1, "C")
    pdf.ln(8)
    pdf.set_font("Helvetica", "", 13)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, "Complete Project Documentation", 0, 1, "C")
    pdf.cell(0, 8, "Version 4.0 Pro", 0, 1, "C")
    pdf.ln(15)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 7, "Tech Stack: Python | Streamlit | FastAPI | DistilBERT | Redis | Docker", 0, 1, "C")
    pdf.cell(0, 7, "Author: Sanjay Kumar", 0, 1, "C")
    pdf.ln(20)
    pdf.add_image_safe(f"{img}/02_home.png", 160)

    # ── Table of Contents ──
    pdf.add_page()
    pdf.chapter_title("Table of Contents")
    toc = [
        "1. Project Overview",
        "2. Architecture & Tech Stack",
        "3. Project Structure",
        "4. Installation & Setup",
        "5. Dashboard Pages",
        "   5.1 Login & Authentication",
        "   5.2 Home Page",
        "   5.3 Overview & KPIs",
        "   5.4 Platform Analysis",
        "   5.5 Live Predictor",
        "   5.6 Competitive Benchmarking",
        "   5.7 Model Insights",
        "   5.8 Export & Reporting",
        "6. Data Pipeline",
        "7. ML Model Details",
        "8. API Service",
        "9. Monitoring & Drift Detection",
        "10. Theming System",
        "11. Configuration Reference",
    ]
    for item in toc:
        pdf.body_text(item)

    # ── 1. Overview ──
    pdf.add_page()
    pdf.chapter_title("1. Project Overview")
    pdf.body_text(
        "Sentiment Intelligence is a production-grade, end-to-end sentiment analysis platform "
        "that combines a fine-tuned DistilBERT NLP model with an interactive Streamlit dashboard. "
        "It analyzes social media engagement data across 6 major platforms (Instagram, TikTok, "
        "Twitter, YouTube, LinkedIn, Facebook) and provides deep insights through interactive "
        "charts, real-time ML predictions, SHAP-based explainability, and automated PDF reporting."
    )
    pdf.section_title("Key Capabilities")
    for feat in [
        "6 interactive analytics pages with Plotly visualizations",
        "Real-time DistilBERT inference with SHAP explainability",
        "Dual theme system (Dark/Light) with animated particle backgrounds",
        "Dataset upload with modal progress tracking and validation",
        "Automated PDF report generation with embedded charts",
        "FastAPI backend with Redis caching and rate limiting",
        "Docker-ready multi-service deployment",
        "Data drift detection and automatic retraining triggers",
        "MLflow experiment tracking and model versioning",
        "Custom login UI with session-based authentication",
    ]:
        pdf.bullet(feat)

    # ── 2. Architecture ──
    pdf.add_page()
    pdf.chapter_title("2. Architecture & Tech Stack")
    pdf.body_text(
        "The system follows a layered architecture: Data Ingestion -> Feature Engineering -> "
        "ML Training -> FastAPI Inference -> Streamlit Dashboard. Each layer is independently "
        "deployable via Docker containers."
    )
    pdf.section_title("Tech Stack")
    w = [60, 130]
    pdf.table_row(["Layer", "Technology"], w, bold=True)
    for row in [
        ["Frontend", "Streamlit 1.40+, Plotly, Custom HTML/CSS/JS"],
        ["Backend API", "FastAPI, Uvicorn, Pydantic"],
        ["ML Model", "HuggingFace Transformers (DistilBERT), PyTorch"],
        ["Explainability", "SHAP"],
        ["Tracking", "MLflow"],
        ["Caching", "Redis 7"],
        ["Data", "Pandas, PyArrow (Parquet)"],
        ["PDF", "FPDF2, Matplotlib"],
        ["Monitoring", "Evidently AI, Prometheus"],
        ["Containers", "Docker, Docker Compose"],
    ]:
        pdf.table_row(row, w)

    # ── 3. Project Structure ──
    pdf.add_page()
    pdf.chapter_title("3. Project Structure")
    pdf.set_font("Courier", "", 9)
    pdf.set_text_color(40, 40, 40)
    struct = """Sentiment Analysis Dashboard/
|-- config.yaml              (central config)
|-- docker-compose.yml       (multi-service orchestration)
|-- generate_data.py         (synthetic dataset generator)
|-- requirements.txt         (Python dependencies)
|-- .env.example             (environment template)
|-- data/
|   |-- raw/                 (CSV datasets)
|   |-- processed/           (cleaned Parquet)
|   |-- artifacts/           (quality reports)
|-- saved_model/
|   |-- model_card.json      (model metadata)
|-- src/
|   |-- api/
|   |   |-- main.py          (FastAPI endpoints)
|   |   |-- client.py        (HTTP client)
|   |   |-- middleware.py    (rate limit, CORS)
|   |   |-- schemas.py      (Pydantic models)
|   |-- data/
|   |   |-- loader.py        (CSV->Parquet)
|   |   |-- cleaner.py       (dedup, missing)
|   |   |-- feature_engineer.py
|   |-- models/
|   |   |-- trainer.py       (DistilBERT fine-tuning)
|   |-- monitoring/
|   |   |-- drift_detector.py
|   |   |-- retrain_trigger.py
|   |-- dashboard/
|       |-- app.py           (main entry)
|       |-- components/      (10 UI components)
|       |-- pages/           (6 analytics pages)"""
    pdf.multi_cell(0, 5, struct)
    pdf.ln(5)

    # ── 4. Installation ──
    pdf.add_page()
    pdf.chapter_title("4. Installation & Setup")
    pdf.section_title("Prerequisites")
    for p in ["Python 3.10+", "pip (or conda)", "Docker & Docker Compose (optional)", "Redis (optional, for API caching)"]:
        pdf.bullet(p)
    pdf.ln(4)
    pdf.section_title("Quick Start")
    pdf.set_font("Courier", "", 10)
    pdf.set_text_color(40, 40, 40)
    steps = """1. git clone <repo-url>
2. cd "Sentiment Analysis Dashboard"
3. python -m venv venv
4. venv\\Scripts\\activate        (Windows)
5. pip install -r requirements.txt
6. cp .env.example .env
7. python generate_data.py
8. python -m src.data.loader
9. streamlit run src/dashboard/app.py"""
    pdf.multi_cell(0, 6, steps)
    pdf.ln(4)
    pdf.set_font("Helvetica", "", 11)
    pdf.body_text("The dashboard will be available at http://localhost:8501")
    pdf.section_title("Docker Deployment")
    pdf.set_font("Courier", "", 10)
    pdf.multi_cell(0, 6, "docker-compose up --build\n\nDashboard: http://localhost:8501\nAPI:       http://localhost:8000\nMLflow:    http://localhost:5000\nRedis:     localhost:6379")

    # ── 5. Dashboard Pages ──
    pdf.add_page()
    pdf.chapter_title("5. Dashboard Pages")

    # 5.1 Login
    pdf.section_title("5.1 Login & Authentication")
    pdf.body_text("Custom SentiScope branded login with email/password. Session persistence via st.session_state.")
    pdf.add_image_safe(f"{img}/01_login.png", 160)

    # 5.2 Home
    pdf.add_page()
    pdf.section_title("5.2 Home Page")
    pdf.body_text(
        "Landing page with animated hero section, live statistics badge, feature highlights, "
        "dataset upload with modal progress popup, and sentiment metrics grid."
    )
    pdf.add_image_safe(f"{img}/02_home.png", 160)

    # 5.3 Overview
    pdf.add_page()
    pdf.section_title("5.3 Overview & KPIs")
    for feat in [
        "4 animated KPI cards with delta indicators",
        "Sentiment donut chart with hover tooltips",
        "Stacked bar: sentiment share by platform",
        "7-day rolling trend line for positive sentiment",
        "Advanced data filters (date, platform, sentiment, category, etc.)",
    ]:
        pdf.bullet(feat)
    pdf.ln(3)
    pdf.add_image_safe(f"{img}/03_overview.png", 160)

    # 5.4 Platform Analysis
    pdf.add_page()
    pdf.section_title("5.4 Platform Analysis")
    for feat in [
        "Engagement heatmap (hour x day) for optimal posting",
        "Reach vs engagement scatter plot (log scale)",
        "Content format box plot comparison",
        "Platform interaction grouped bar chart",
        "Virality score ranking by category",
    ]:
        pdf.bullet(feat)
    pdf.ln(3)
    pdf.add_image_safe(f"{img}/04_platform_analysis.png", 160)

    # 5.5 Live Predictor
    pdf.add_page()
    pdf.section_title("5.5 Live Predictor")
    for feat in [
        "8-field input form for real-time inference",
        "Generate Example button (auto-fill from dataset)",
        "Sentiment badge + animated confidence bar",
        "Softmax class probabilities",
        "SHAP feature importance bar chart",
        "What-if analysis with interactive sliders",
    ]:
        pdf.bullet(feat)
    pdf.ln(3)
    pdf.add_image_safe(f"{img}/05_live_predictor.png", 160)

    # 5.6 Benchmarking
    pdf.add_page()
    pdf.section_title("5.6 Competitive Benchmarking")
    for feat in [
        "5-axis radar chart comparing 2-4 platforms",
        "Sentiment by influencer tier (stacked bar)",
        "Category x platform positive sentiment heatmap",
    ]:
        pdf.bullet(feat)
    pdf.ln(3)
    pdf.add_image_safe(f"{img}/06_benchmarking.png", 160)

    # 5.7 Model Insights
    pdf.add_page()
    pdf.section_title("5.7 Model Insights")
    for feat in [
        "Model card (name, date, F1, accuracy)",
        "Classification report with color-coded F1 scores",
        "Confusion matrix heatmap",
        "Calibration curve (reliability diagram)",
        "Data quality report (duplicates, outliers, missing values)",
        "Feature distribution explorer (histogram + box plot)",
    ]:
        pdf.bullet(feat)
    pdf.ln(3)
    pdf.add_image_safe(f"{img}/07_model_insights.png", 160)

    # 5.8 Export
    pdf.add_page()
    pdf.section_title("5.8 Export & Reporting")
    for feat in [
        "CSV download of filtered dataset (18 columns + label)",
        "Automated PDF report with title, summary, metrics, chart",
        "One-click download buttons",
    ]:
        pdf.bullet(feat)
    pdf.ln(3)
    pdf.add_image_safe(f"{img}/08_export.png", 160)

    # ── 6. Data Pipeline ──
    pdf.add_page()
    pdf.chapter_title("6. Data Pipeline")
    pdf.body_text("Three-stage pipeline: Ingestion -> Cleaning -> Feature Engineering")
    w2 = [30, 50, 110]
    pdf.table_row(["Stage", "Module", "Description"], w2, bold=True)
    pdf.table_row(["1", "loader.py", "CSV read, schema validation, Parquet conversion"], w2)
    pdf.table_row(["2", "cleaner.py", "Dedup by Post_ID, handle missing values, flag outliers"], w2)
    pdf.table_row(["3", "feature_engineer.py", "Virality score, save rate, time features, buckets"], w2)
    pdf.ln(5)
    pdf.body_text("Dataset: 20 columns, 5000+ rows covering 6 platforms, 7 categories, 5 content types, 5 influencer tiers, 3 sentiment classes.")

    # ── 7. ML Model ──
    pdf.add_page()
    pdf.chapter_title("7. ML Model Details")
    pdf.body_text("Fine-tuned DistilBERT (distilbert-base-uncased) for 3-class sentiment classification.")
    pdf.section_title("Training Config")
    w3 = [70, 80]
    pdf.table_row(["Parameter", "Value"], w3, bold=True)
    for r in [["Epochs", "5"], ["Batch (train)", "16"], ["Batch (eval)", "32"],
              ["Learning rate", "2e-5"], ["LR scheduler", "Cosine"], ["Warmup", "0.1"],
              ["Weight decay", "0.01"], ["Best metric", "F1 macro"]]:
        pdf.table_row(r, w3)
    pdf.ln(5)
    pdf.section_title("Performance")
    w4 = [50, 30, 30, 30, 30]
    pdf.table_row(["Class", "Prec", "Recall", "F1", "Support"], w4, bold=True)
    pdf.table_row(["Positive", "0.85", "0.89", "0.87", "3150"], w4)
    pdf.table_row(["Neutral", "0.73", "0.70", "0.71", "1150"], w4)
    pdf.table_row(["Negative", "0.81", "0.77", "0.79", "750"], w4)
    pdf.table_row(["Accuracy", "", "", "82.4%", "5050"], w4)

    # ── 8. API ──
    pdf.add_page()
    pdf.chapter_title("8. API Service")
    pdf.body_text("FastAPI backend at port 8000 with /predict and /health endpoints.")
    pdf.section_title("Features")
    for f in ["Redis caching (TTL 1hr)", "Rate limiting (100/min)", "SHAP explainability",
              "Fallback mock predictor", "Prometheus metrics", "JWT-ready auth"]:
        pdf.bullet(f)

    # ── 9. Monitoring ──
    pdf.ln(8)
    pdf.chapter_title("9. Monitoring & Drift Detection")
    pdf.body_text("PSI-based data drift detection with configurable thresholds. Auto-retraining when F1 < 0.75.")
    w5 = [60, 130]
    pdf.table_row(["Module", "Purpose"], w5, bold=True)
    pdf.table_row(["drift_detector.py", "PSI computation between reference and production data"], w5)
    pdf.table_row(["retrain_trigger.py", "Auto-retrain when F1 macro drops below threshold"], w5)

    # ── 10. Theming ──
    pdf.add_page()
    pdf.chapter_title("10. Theming System")
    pdf.body_text("600+ lines of CSS in theme_provider.py. Dual Dark/Light mode with seamless switching.")
    w6 = [50, 60, 60]
    pdf.table_row(["Token", "Dark", "Light"], w6, bold=True)
    for r in [["--bg-main", "#0F172A", "#F9FAFB"], ["--bg-secondary", "#1E293B", "#FFFFFF"],
              ["--text-primary", "#F1F5F9", "#111827"], ["--brand-primary", "#00E6F0", "#00E6F0"],
              ["--brand-secondary", "#6366F1", "#6366F1"]]:
        pdf.table_row(r, w6)
    pdf.ln(5)
    pdf.body_text("Font: Inter (Google Fonts). Components styled: sidebar, inputs, tabs, expanders, buttons, tables, charts, scrollbar, popover menus, progress bars, metrics cards.")

    # ── 11. Config ──
    pdf.add_page()
    pdf.chapter_title("11. Configuration Reference")
    pdf.section_title("config.yaml")
    pdf.set_font("Courier", "", 9)
    cfg = """paths:
  raw_data: "data/raw/social_media_engagement_dataset.csv"
  processed_data: "data/processed/processed_data.parquet"
  model_card: "saved_model/model_card.json"

model:
  base_model: "distilbert-base-uncased"
  num_labels: 3
  max_length: 128

training:
  num_train_epochs: 5
  learning_rate: 2.0e-5
  metric_for_best_model: "f1_macro"

app:
  redis_ttl: 3600
  rate_limit: "100/minute"
  drift_threshold_psi: 0.2
  retrain_f1_threshold: 0.75"""
    pdf.multi_cell(0, 5, cfg)
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 11)
    pdf.section_title("Environment Variables")
    w7 = [55, 135]
    pdf.table_row(["Variable", "Description"], w7, bold=True)
    for r in [["DATABASE_URL", "PostgreSQL connection string"],
              ["REDIS_URL", "Redis connection (default: redis://localhost:6379)"],
              ["JWT_SECRET_KEY", "Secret for JWT signing"],
              ["MLFLOW_TRACKING_URI", "MLflow server URL"],
              ["API_BASE_URL", "FastAPI URL (for Docker networking)"]]:
        pdf.table_row(r, w7)

    # Save
    out_path = "docs/Sentiment_Intelligence_Documentation.pdf"
    pdf.output(out_path)
    print(f"PDF saved to {out_path}")

if __name__ == "__main__":
    generate()
