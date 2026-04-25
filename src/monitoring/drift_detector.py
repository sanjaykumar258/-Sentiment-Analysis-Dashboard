import pandas as pd
import os
import yaml
import logging
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, ClassificationPreset
import mlflow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_drift_report(config_path="config.yaml"):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
        
    reference_data_path = config["paths"]["processed_data"] # Use the whole dataset as reference for demo
    # In a real scenario, reference is training set, current is latest inference batch.
    
    if not os.path.exists(reference_data_path):
        logger.error("Reference data not found.")
        return
        
    ref_df = pd.read_parquet(reference_data_path)
    # Mock current data by shifting distributions slightly
    curr_df = ref_df.copy()
    curr_df["Engagement_Rate"] = curr_df["Engagement_Rate"] * 1.05
    curr_df["virality_score"] = curr_df["virality_score"] * 0.95
    
    features = ["Engagement_Rate", "Follower_Count", "Hashtag_Count", "Content_Length", "virality_score"]
    
    report = Report(metrics=[
        DataDriftPreset(num_features=features, cat_features=["Platform", "Category"]),
        ClassificationPreset() # Would need prediction column
    ])
    
    # We will only run Data Drift for this demo since we might not have predictions in the reference yet
    report = Report(metrics=[DataDriftPreset(num_features=features, cat_features=["Platform", "Category"])])
    
    report.run(reference_data=ref_df, current_data=curr_df)
    
    drift_report_path = config["paths"]["drift_report"]
    os.makedirs(os.path.dirname(drift_report_path), exist_ok=True)
    report.save_html(drift_report_path)
    
    logger.info(f"Drift report generated at {drift_report_path}")
    
    # Check for alerts
    drift_result = report.as_dict()
    drifts = drift_result["metrics"][0]["result"]["drift_by_columns"]
    
    threshold = config["app"]["drift_threshold_psi"]
    alerts = []
    
    for col, data in drifts.items():
        if data["drift_score"] > threshold:
            alerts.append(f"Feature '{col}' drift detected: PSI {data['drift_score']:.3f} > {threshold}")
            
    if alerts:
        alert_path = config["paths"]["drift_alerts"]
        os.makedirs(os.path.dirname(alert_path), exist_ok=True)
        with open(alert_path, "a") as f:
            for alert in alerts:
                f.write(f"{pd.Timestamp.now()} - {alert}\n")
                logger.warning(alert)

if __name__ == "__main__":
    generate_drift_report()
