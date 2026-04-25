import os
import json
import yaml
import pandas as pd
import numpy as np
import torch
from dataclasses import dataclass, asdict
from datetime import datetime
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report, confusion_matrix, roc_auc_score
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.calibration import calibration_curve
from transformers import EarlyStoppingCallback

@dataclass
class ModelCard:
    model_name: str
    training_date: str
    metrics: dict
    per_class_metrics: dict
    dataset_size: int
    hyperparameters: dict

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    
    acc = accuracy_score(labels, predictions)
    precision_macro, recall_macro, f1_macro, _ = precision_recall_fscore_support(labels, predictions, average="macro")
    precision_weighted, recall_weighted, f1_weighted, _ = precision_recall_fscore_support(labels, predictions, average="weighted")
    
    return {
        "accuracy": acc,
        "f1_macro": f1_macro,
        "f1_weighted": f1_weighted,
        "precision_macro": precision_macro,
        "recall_macro": recall_macro
    }

def format_text(row):
    text_cols = ["Text", "Post_Text", "Content", "Tweet", "Text_Content"]
    actual_text = ""
    for col in text_cols:
        if col in row and pd.notna(row[col]):
            actual_text = f" Text: {row[col]}"
            break
    eng_label = "High" if row['Engagement_Rate'] > 15 else "Low" if row['Engagement_Rate'] < 5 else "Medium"
    return f"Engagement: {eng_label}.{actual_text}"

def prepare_dataset(df, tokenizer, max_length):
    df["text"] = df.apply(format_text, axis=1)
    label_map = {"negative": 0, "neutral": 1, "positive": 2}
    df["label"] = df["Sentiment"].astype(str).str.lower().str.strip().map(label_map)
    df = df.dropna(subset=["label"]).copy()
    df["label"] = df["label"].astype(int)
    
    dataset = Dataset.from_pandas(df[["text", "label"]])
    def tokenize_function(examples):
        return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=max_length)
    
    tokenized_dataset = dataset.map(tokenize_function, batched=True)
    return tokenized_dataset

def train_model(config_path="config.yaml"):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
        
    base_model = config["model"]["base_model"]
    num_labels = config["model"]["num_labels"]
    max_length = config["model"]["max_length"]
    
    df = pd.read_parquet(config["paths"]["processed_data"])
    
    try:
        with open(config["paths"]["data_splits"], "r") as f:
            splits = json.load(f)
        train_df = df.loc[splits["train_indices"]]
        val_df = df.loc[splits["val_indices"]]
        test_df = df.loc[splits["test_indices"]]
    except FileNotFoundError:
        # If no split exists, create an 80/10/10 split dynamically
        from sklearn.model_selection import train_test_split
        train_df, temp_df = train_test_split(df, test_size=0.2, random_state=42)
        val_df, test_df = train_test_split(temp_df, test_size=0.5, random_state=42)
        print("data_splits.json not found. Dynamically split dataset (80/10/10).")
    
    tokenizer = AutoTokenizer.from_pretrained(base_model)
    model = AutoModelForSequenceClassification.from_pretrained(base_model, num_labels=num_labels)
    
    train_dataset = prepare_dataset(train_df, tokenizer, max_length)
    val_dataset = prepare_dataset(val_df, tokenizer, max_length)
    test_dataset = prepare_dataset(test_df, tokenizer, max_length)
    
    training_args = TrainingArguments(
        output_dir=config["paths"]["model_output"],
        num_train_epochs=config["training"]["num_train_epochs"],
        per_device_train_batch_size=config["training"]["per_device_train_batch_size"],
        per_device_eval_batch_size=config["training"]["per_device_eval_batch_size"],
        gradient_accumulation_steps=config["training"].get("gradient_accumulation_steps", 1),
        warmup_ratio=config["training"]["warmup_ratio"],
        weight_decay=config["training"]["weight_decay"],
        learning_rate=float(config["training"]["learning_rate"]),
        lr_scheduler_type=config["training"]["lr_scheduler_type"],
        eval_strategy=config["training"]["evaluation_strategy"],
        save_strategy=config["training"]["save_strategy"],
        load_best_model_at_end=config["training"]["load_best_model_at_end"],
        metric_for_best_model=config["training"]["metric_for_best_model"],
        fp16=config["training"]["fp16"] and torch.cuda.is_available(),
        logging_steps=config["training"]["logging_steps"],
        report_to="none" # Disable mlflow integration in Trainer to handle manually or let Trainer do it
    )
    
    training_args.metric_for_best_model = "f1_macro"
    training_args.load_best_model_at_end = True
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=10)]
    )
    
    # Train
    trainer.train()
    
    # Eval on Test
    test_results = trainer.evaluate(test_dataset)
    
    # Generate confusion matrix
    predictions = trainer.predict(test_dataset)
    preds = np.argmax(predictions.predictions, axis=-1)
    labels = predictions.label_ids
    
    cm = confusion_matrix(labels, preds)
    plt.figure(figsize=(8,6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=["Negative", "Neutral", "Positive"], yticklabels=["Negative", "Neutral", "Positive"])
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    os.makedirs("data/artifacts", exist_ok=True)
    plt.savefig("data/artifacts/confusion_matrix.png")
    
    # Calculate per-class metrics
    report = classification_report(labels, preds, target_names=["Negative", "Neutral", "Positive"], output_dict=True)
    per_class_metrics = {}
    for label in ["Negative", "Neutral", "Positive"]:
        if label in report:
            per_class_metrics[label] = {
                "precision": report[label]["precision"],
                "recall": report[label]["recall"],
                "f1": report[label]["f1-score"],
                "support": report[label]["support"]
            }
    
    # Save Model
    saved_model_path = config["paths"]["saved_model"]
    os.makedirs(saved_model_path, exist_ok=True)
    trainer.save_model(saved_model_path)
    tokenizer.save_pretrained(saved_model_path)
    
    # Save Model Card
    card = ModelCard(
        model_name=base_model,
        training_date=datetime.now().isoformat(),
        metrics=test_results,
        per_class_metrics=per_class_metrics,
        dataset_size=len(train_df),
        hyperparameters=asdict(training_args) if hasattr(training_args, "__dict__") else {}
    )
    
    with open(config["paths"]["model_card"], "w") as f:
        # Use a safe serialization
        json.dump(card.__dict__, f, default=str)
        
    print(f"Model trained and saved to {saved_model_path}")

if __name__ == "__main__":
    train_model()
