import yaml
import json
import logging
import mlflow
from src.models.trainer import train_model

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_and_retrain(config_path="config.yaml"):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
        
    threshold = config["app"]["retrain_f1_threshold"]
    
    # Read latest model card metrics
    card_path = config["paths"]["model_card"]
    try:
        with open(card_path, "r") as f:
            card = json.load(f)
        
        current_f1 = card["metrics"].get("eval_f1_macro", 1.0) # Assume 1.0 if not found
        
        if current_f1 < threshold:
            logger.warning(f"F1 Macro ({current_f1:.4f}) is below threshold ({threshold}). Triggering retraining...")
            mlflow.set_tracking_uri("http://localhost:5000")
            mlflow.set_experiment("Automated_Retraining")
            with mlflow.start_run():
                train_model(config_path)
        else:
            logger.info(f"Model performance ({current_f1:.4f}) is acceptable. No retraining needed.")
            
    except FileNotFoundError:
        logger.error("Model card not found. Training for the first time...")
        train_model(config_path)

if __name__ == "__main__":
    check_and_retrain()
