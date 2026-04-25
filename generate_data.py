import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def generate_dataset(num_rows=5000):
    platforms = ["Instagram", "TikTok", "Twitter", "YouTube", "LinkedIn", "Facebook"]
    content_types = ["Video", "Image", "Text", "Carousel", "Link"]
    categories = ["Tech", "Fashion", "Finance", "Gaming", "Education", "Entertainment", "Health"]
    sentiments = ["Positive", "Negative", "Neutral"]
    influencer_tiers = ["Nano", "Micro", "Mid-tier", "Macro", "Mega"]
    
    np.random.seed(42)
    random.seed(42)

    data = []
    base_time = datetime(2023, 1, 1)

    for i in range(num_rows):
        platform = random.choice(platforms)
        content_type = random.choice(content_types)
        category = random.choice(categories)
        influencer_tier = random.choice(influencer_tiers)
        has_media = random.choice([True, False])
        is_verified = random.choice([True, False])
        
        # Follower count
        follower_count = int(np.random.lognormal(mean=10, sigma=2))
        
        # Views, Likes, Comments, Shares, Saves
        views = int(follower_count * np.random.uniform(0.01, 1.5)) + 1
        likes = int(views * np.random.uniform(0.01, 0.2))
        comments = int(likes * np.random.uniform(0.01, 0.1))
        shares = int(likes * np.random.uniform(0.01, 0.1))
        saves = int(likes * np.random.uniform(0.01, 0.15))
        
        engagement_rate = ((likes + comments + shares + saves) / views) * 100 if views > 0 else 0
        
        # --- INJECT SIGNAL ---
        # Rule-based sentiment so model can learn a pattern
        if engagement_rate > 15:
            sentiment = "Positive"
            text_prefix = random.choice(["Amazing results!", "Absolutely love this", "Incredible engagement", "Top tier content", "Best ever"])
        elif engagement_rate < 5:
            sentiment = "Negative"
            text_prefix = random.choice(["Disappointing reach", "Needs improvement", "Poor performance", "Bad quality", "Frustrating"])
        else:
            sentiment = "Neutral"
            text_prefix = random.choice(["Standard update", "Regular posting", "Consistent performance", "Checking in", "Average stats"])
        
        # Add platform/category signal too
        text_content = f"{text_prefix}. Check out this {category} post on {platform}!"
        
        timestamp = base_time + timedelta(
            days=random.randint(0, 365),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        hashtag_count = random.randint(0, 30) if random.random() > 0.1 else np.nan
        content_length = len(text_content)
        
        row = {
            "Post_ID": f"POST_{i:05d}",
            "Timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "Platform": platform,
            "Content_Type": content_type,
            "Category": category,
            "Text_Content": text_content,  # New column with signal
            "Likes": likes,
            "Comments": comments,
            "Shares": shares,
            "Views": views,
            "Saves": saves,
            "Follower_Count": follower_count,
            "Engagement_Rate": engagement_rate,
            "Hour_of_Day": timestamp.hour,
            "Day_of_Week": timestamp.weekday(),
            "Hashtag_Count": hashtag_count,
            "Content_Length": content_length,
            "Sentiment": sentiment,
            "Influencer_Tier": influencer_tier,
            "Has_Media": has_media,
            "Is_Verified": is_verified
        }
        data.append(row)

    df = pd.DataFrame(data)
    
    # Introduce some duplicates
    df = pd.concat([df, df.sample(50, random_state=42)], ignore_index=True)
    
    # Introduce some Engagement_Rate outliers
    df.loc[df.sample(20).index, "Engagement_Rate"] = df["Engagement_Rate"] * 10
    
    df.to_csv("data/raw/social_media_engagement_dataset.csv", index=False)
    print("Dataset generated at data/raw/social_media_engagement_dataset.csv")

if __name__ == "__main__":
    generate_dataset()
