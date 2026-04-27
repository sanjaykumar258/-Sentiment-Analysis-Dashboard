import pandas as pd
import json
import os
import yaml
from pydantic import BaseModel, ValidationError, Field, field_validator
from typing import List, Optional, Literal, Dict
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PostSchema(BaseModel):
    Post_ID: str
    Timestamp: str
    Platform: Literal["Instagram", "TikTok", "Twitter", "YouTube", "LinkedIn", "Facebook"]
    Content_Type: Literal["Video", "Image", "Text", "Carousel", "Link", "Audio", "Other"]
    Category: str
    Likes: int = Field(ge=0)
    Comments: int = Field(ge=0)
    Shares: int = Field(ge=0)
    Views: int = Field(ge=0)
    Saves: int = Field(ge=0)
    Follower_Count: int = Field(ge=0)
    Engagement_Rate: float = Field(ge=0.0)
    Hour_of_Day: int = Field(ge=0, le=23)
    Day_of_Week: int = Field(ge=0, le=6)
    Hashtag_Count: Optional[float]
    Content_Length: Optional[float]
    Sentiment: Literal["Positive", "Negative", "Neutral"]
    Influencer_Tier: Literal["Nano", "Micro", "Mid-tier", "Macro", "Mega"]
    Has_Media: bool
    Is_Verified: bool

class DataLoader:
    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        self.raw_data_path = self.config["paths"]["raw_data"]
        self.processed_data_path = self.config["paths"]["processed_data"]
        self.dq_report_path = self.config["paths"]["data_quality_report"]

    def load_data(self) -> pd.DataFrame:
        if self.raw_data_path.endswith('.csv'):
            df = pd.read_csv(self.raw_data_path)
        elif self.raw_data_path.endswith('.json'):
            df = pd.read_json(self.raw_data_path)
        else:
            raise ValueError("Unsupported file format. Must be CSV or JSON.")
        
        # We need to drop completely missing rows, or just parse directly
        return df

    def validate_schema(self, df: pd.DataFrame) -> pd.DataFrame:
        records = df.to_dict(orient="records")
        valid_records = []
        errors = []
        for i, record in enumerate(records):
            try:
                # Need to handle NaN in Optional float fields for Pydantic
                # Replace pandas NaNs with None for Pydantic
                rec_clean = {k: (None if pd.isna(v) else v) for k, v in record.items()}
                PostSchema(**rec_clean)
                valid_records.append(record)
            except ValidationError as e:
                errors.append(f"Row {i} error: {e}")
                
        if errors:
            logger.warning(f"Found {len(errors)} validation errors. (Showing first 5: {errors[:5]})")
            # For strictness, you could raise an error, but here we might want to just proceed with valid, or fail.
            # "raise typed exceptions on schema violations"
            raise ValueError(f"Schema violation detected: {errors[0]}")
            
        return pd.DataFrame(valid_records)

    def run_quality_report(self, df: pd.DataFrame) -> Dict:
        report = {}
        
        # 1. Missing value counts per column
        report["missing_values"] = df.isnull().sum().to_dict()
        
        # 2. Class distribution of Sentiment
        report["sentiment_distribution"] = df["Sentiment"].value_counts().to_dict()
        
        # 3. Duplicate Post_ID detection
        report["duplicate_post_ids"] = int(df.duplicated(subset=["Post_ID"]).sum())
        
        # 4. Outlier detection on Engagement_Rate (>3 std deviations)
        mean_er = df["Engagement_Rate"].mean()
        std_er = df["Engagement_Rate"].std()
        outliers = df[df["Engagement_Rate"] > (mean_er + 3 * std_er)]
        report["outliers_engagement_rate"] = int(len(outliers))
        
        # 5. Temporal continuity check
        df["Timestamp_dt"] = pd.to_datetime(df["Timestamp"])
        date_counts = df["Timestamp_dt"].dt.date.value_counts().sort_index()
        expected_days = (date_counts.index.max() - date_counts.index.min()).days + 1
        actual_days = len(date_counts)
        report["temporal_continuity_gaps"] = expected_days - actual_days
        
        # Save report
        os.makedirs(os.path.dirname(self.dq_report_path), exist_ok=True)
        with open(self.dq_report_path, "w") as f:
            json.dump(report, f, indent=4)
            
        logger.info(f"Data quality report saved to {self.dq_report_path}")
        return report

    def save_parquet(self, df: pd.DataFrame):
        os.makedirs(os.path.dirname(self.processed_data_path), exist_ok=True)
        df.to_parquet(self.processed_data_path, index=False)
        logger.info(f"Processed data saved to {self.processed_data_path}")

    def run_pipeline(self):
        logger.info("Loading data...")
        df = self.load_data()
        
        logger.info("Validating schema...")
        # To avoid schema violations failing the whole pipeline when we use generated data,
        # we might need to handle content types not in Literal.
        try:
            df = self.validate_schema(df)
        except ValueError as e:
            logger.error(str(e))
            raise

        logger.info("Running data quality report...")
        self.run_quality_report(df)

        # Fill missing values for required columns before saving
        required_defaults = {
            "Timestamp": lambda n: pd.date_range("2024-01-01", periods=n, freq="h").astype(str),
            "Platform": lambda n: ["Instagram"] * n,
            "Content_Type": lambda n: ["Text"] * n,
            "Sentiment": lambda n: ["Neutral"] * n
        }
        for col, gen in required_defaults.items():
            if col in df.columns and df[col].isnull().any():
                df[col] = df[col].fillna(pd.Series(gen(len(df)), index=df.index))
        
        logger.info("Saving to Parquet...")
        self.save_parquet(df)
        
if __name__ == "__main__":
    loader = DataLoader()
    loader.run_pipeline()
