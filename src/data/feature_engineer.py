import pandas as pd
import json
import os
import yaml
import joblib
import mlflow
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from src.data.cleaner import clean_data, feature_engineering

class DataSplitter:
    def __init__(self, config_path="config.yaml"):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        self.splits_path = self.config["paths"]["data_splits"]

    def split(self, df: pd.DataFrame):
        train_val, test = train_test_split(df, test_size=0.15, stratify=df["Sentiment"], random_state=42)
        train, val = train_test_split(train_val, test_size=0.15/0.85, stratify=train_val["Sentiment"], random_state=42)
        
        splits = {
            "train_indices": train.index.tolist(),
            "val_indices": val.index.tolist(),
            "test_indices": test.index.tolist()
        }
        
        os.makedirs(os.path.dirname(self.splits_path), exist_ok=True)
        with open(self.splits_path, "w") as f:
            json.dump(splits, f)
            
        return train, val, test

def build_and_save_pipeline(df: pd.DataFrame, config_path="config.yaml"):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
        
    num_cols = [
        "Likes", "Comments", "Shares", "Views", "Saves", "Follower_Count",
        "Engagement_Rate", "hour", "day_of_week", "month", "quarter",
        "Hashtag_Count", "Content_Length", "virality_score", "save_rate",
        "engagement_per_follower", "content_density", "log_views", 
        "log_likes", "log_followers"
    ]
    
    cat_cols = ["Platform", "Content_Type", "Influencer_Tier", "Category"]
    
    # Has_Media, Is_Verified, is_peak_hour are already numeric binary (0/1 or False/True)
    # We can pass them through or scale them. Let's pass them through.
    passthrough_cols = ["Has_Media", "Is_Verified", "is_peak_hour", "platform_tier"]
    
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), num_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
            ("pass", "passthrough", passthrough_cols)
        ],
        remainder="drop"
    )
    
    pipeline = Pipeline([
        ("preprocessor", preprocessor)
    ])
    
    pipeline.fit(df)
    
    pipeline_path = config["paths"]["feature_pipeline"]
    os.makedirs(os.path.dirname(pipeline_path), exist_ok=True)
    joblib.dump(pipeline, pipeline_path)
    
    mlflow.set_tracking_uri("http://localhost:5000")
    mlflow.set_experiment("Feature_Engineering")
    with mlflow.start_run():
        mlflow.log_param("num_features", len(num_cols))
        mlflow.log_param("cat_features", len(cat_cols))
        mlflow.log_artifact(pipeline_path)
    
    return pipeline

def process_features(config_path="config.yaml"):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    df = pd.read_parquet(config["paths"]["processed_data"])
    df = clean_data(df)
    df = feature_engineering(df)
    
    splitter = DataSplitter(config_path)
    train, val, test = splitter.split(df)
    
    build_and_save_pipeline(train, config_path)
    
if __name__ == "__main__":
    process_features()
