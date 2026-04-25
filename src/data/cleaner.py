import pandas as pd
import numpy as np

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans raw social media data according to specs.
    """
    df = df.copy()
    
    # Remove duplicate Post_ID, keeping the most recent timestamp
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    df = df.sort_values(by="Timestamp", ascending=False)
    df = df.drop_duplicates(subset=["Post_ID"], keep="first")
    
    # Cap Engagement_Rate at 99th percentile (Winsorization)
    er_99th = df["Engagement_Rate"].quantile(0.99)
    df["Engagement_Rate"] = df["Engagement_Rate"].clip(upper=er_99th)
    
    # Parse Timestamp features
    df["hour"] = df["Timestamp"].dt.hour
    df["day_of_week"] = df["Timestamp"].dt.dayofweek
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)
    df["month"] = df["Timestamp"].dt.month
    df["quarter"] = df["Timestamp"].dt.quarter
    
    # Fill missing values
    df["Hashtag_Count"] = df["Hashtag_Count"].fillna(0)
    
    # Fill Content_Length with platform median
    platform_medians = df.groupby("Platform")["Content_Length"].transform("median")
    df["Content_Length"] = df["Content_Length"].fillna(platform_medians)
    # If still any missing (e.g., all missing for a platform), fill with overall median
    df["Content_Length"] = df["Content_Length"].fillna(df["Content_Length"].median())
    
    return df

def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """
    Creates derived features.
    """
    df = df.copy()
    
    df["virality_score"] = (df["Shares"] * 3 + df["Comments"] * 2 + df["Likes"]) / (df["Views"] + 1)
    df["save_rate"] = df["Saves"] / (df["Views"] + 1)
    df["engagement_per_follower"] = df["Engagement_Rate"] / (df["Follower_Count"] + 1)
    df["content_density"] = df["Content_Length"] / (df["Hashtag_Count"] + 1)
    
    df["is_peak_hour"] = df["hour"].isin([9, 10, 11, 19, 20, 21]).astype(int)
    
    platform_tier_map = {
        "TikTok": 6,
        "Instagram": 5,
        "YouTube": 4,
        "Twitter": 3,
        "Facebook": 2,
        "LinkedIn": 1
    }
    df["platform_tier"] = df["Platform"].map(platform_tier_map)
    
    df["log_views"] = np.log1p(df["Views"])
    df["log_likes"] = np.log1p(df["Likes"])
    df["log_followers"] = np.log1p(df["Follower_Count"])
    
    return df
