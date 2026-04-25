import os
import json
import time
import asyncio
import hashlib
from typing import List
from concurrent.futures import ThreadPoolExecutor
import numpy as np

from fastapi import FastAPI, Request, Depends, HTTPException, BackgroundTasks
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
import redis.asyncio as redis
import torch
import shap
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from src.api.schemas import PredictRequest, PredictResponse
from src.api.middleware import limiter, _rate_limit_exceeded_handler, RateLimitExceeded, RequestIDMiddleware, global_exception_handler, jwt_auth_middleware

app = FastAPI(title="Sentiment API")

# Add Middlewares
# app.add_middleware(BaseHTTPMiddleware, dispatch=jwt_auth_middleware)
app.add_middleware(RequestIDMiddleware)
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.state.limiter = limiter

# Setup Redis (Disabled for No-Docker environment)
# redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
# redis_client = redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
redis_client = None
CACHE_TTL = 3600

# Setup Model
HF_REPO_ID = os.getenv("HF_REPO_ID", "sanjaykumar258/Sentiment-Intel-V4") # Placeholder
MODEL_PATH = os.getenv("MODEL_PATH", "saved_model")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = None
tokenizer = None
explainer = None
executor = ThreadPoolExecutor(max_workers=2)

label_map_inv = {0: "Negative", 1: "Neutral", 2: "Positive"}

def load_model():
    global model, tokenizer, explainer
    # Use local folder if it exists, otherwise stream from Hugging Face
    load_source = MODEL_PATH if os.path.exists(MODEL_PATH) else HF_REPO_ID
    print(f"Loading model from: {load_source}")
    
    try:
        tokenizer = AutoTokenizer.from_pretrained(load_source)
        model = AutoModelForSequenceClassification.from_pretrained(load_source).to(device)
        model.eval()
    except Exception as e:
        print(f"Error loading model from {load_source}: {e}")
        return

    def f(x):
        tv = torch.tensor([tokenizer.encode(v, padding='max_length', max_length=128, truncation=True) for v in x]).to(device)
        with torch.no_grad():
            outputs = model(tv)[0].detach().cpu().numpy()
        import scipy as sp
        scores = (np.exp(outputs).T / np.exp(outputs).sum(-1)).T
        return scores

    explainer = shap.Explainer(f, tokenizer)

def do_predict(text: str):
    if model is None:
        raise ValueError("Model not loaded")
    
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding="max_length", max_length=128).to(device)
    with torch.no_grad():
        outputs = model(**inputs)
    
    # Ultra-logit sharpening (Temperature Scaling)
    # A temperature of 0.2 forces the model to express its certainty clearly (99%+)
    temperature = 0.2
    sharpened_logits = outputs.logits / temperature
    probs = torch.nn.functional.softmax(sharpened_logits, dim=-1).cpu().numpy()[0]
    pred_idx = int(np.argmax(probs))
    
    return {
        "sentiment": label_map_inv[pred_idx],
        "confidence": float(probs[pred_idx]),
        "probabilities": {label_map_inv[i]: float(probs[i]) for i in range(3)}
    }
    
def do_explain(text: str):
    if explainer is None:
        return None
    # For text, we get an Explanation object for the list of inputs
    shap_explanations = explainer([text])
    
    # Extract tokens and values for the first (and only) input string
    tokens = shap_explanations.data[0]
    values = shap_explanations.values[0] # (tokens, classes)
    
    # Create a clean dictionary of {token: [val_neg, val_neu, val_pos]}
    # We ignore special tokens like [PAD] to keep the chart clean
    clean_shap = {}
    for i, token in enumerate(tokens):
        if token not in ["[PAD]", "[CLS]", "[SEP]"]:
            # Ensure we are sending a list of floats
            clean_shap[token] = [float(v) for v in values[i]]
            
    return clean_shap

Instrumentator().instrument(app).expose(app, endpoint="/metrics")

@app.on_event("startup")
async def startup_event():
    
    # Warm up
    start = time.time()
    await asyncio.get_event_loop().run_in_executor(executor, load_model)
    if model:
        await asyncio.get_event_loop().run_in_executor(executor, do_predict, "Test warmup text")
    print(f"Model warmed up in {time.time() - start:.2f}s")

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model is not None}

@app.get("/model/info")
def model_info():
    card_path = "saved_model/model_card.json"
    if os.path.exists(card_path):
        with open(card_path, "r") as f:
            return json.load(f)
    return {"error": "Model card not found"}

@app.post("/predict", response_model=PredictResponse)
@limiter.limit("100/minute")
async def predict(request: Request, body: PredictRequest):
    start = time.time()
    
    # Check cache (Skipped - No Redis)
    # text_hash = hashlib.md5(body.text.encode()).hexdigest()
    # if redis_client:
    #     cached = await redis_client.get(text_hash)
    #     if cached:
    #         result = json.loads(cached)
    #         result["latency_ms"] = (time.time() - start) * 1000
    #         return result
        
    loop = asyncio.get_event_loop()
    try:
        pred_result = await loop.run_in_executor(executor, do_predict, body.text)
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))
    
    shap_vals = None
    if body.include_shap:
        shap_vals = await loop.run_in_executor(executor, do_explain, body.text)
        
    response = PredictResponse(
        post_id=body.post_id,
        sentiment=pred_result["sentiment"],
        confidence=pred_result["confidence"],
        probabilities=pred_result["probabilities"],
        shap_values=shap_vals,
        latency_ms=(time.time() - start) * 1000
    )
    
    # Cache (Skipped - No Redis)
    # if redis_client:
    #     await redis_client.setex(text_hash, CACHE_TTL, response.json())
    
    return response

@app.post("/predict/batch", response_model=List[PredictResponse])
@limiter.limit("100/minute")
async def predict_batch(request: Request, body: List[PredictRequest]):
    if len(body) > 500:
        raise HTTPException(status_code=400, detail="Batch size exceeds 500")
        
    results = []
    # Simplified parallel/batch processing
    for req in body:
        start = time.time()
        # text_hash = hashlib.md5(req.text.encode()).hexdigest()
        # if redis_client:
        #     cached = await redis_client.get(text_hash)
        #     if cached:
        #         res = PredictResponse.parse_raw(cached)
        #         res.latency_ms = (time.time() - start) * 1000
        #         results.append(res)
        #         continue
            
        loop = asyncio.get_event_loop()
        pred_result = await loop.run_in_executor(executor, do_predict, req.text)
        
        shap_vals = None
        if req.include_shap:
            shap_vals = await loop.run_in_executor(executor, do_explain, req.text)
            
        res = PredictResponse(
            post_id=req.post_id,
            sentiment=pred_result["sentiment"],
            confidence=pred_result["confidence"],
            probabilities=pred_result["probabilities"],
            shap_values=shap_vals,
            latency_ms=(time.time() - start) * 1000
        )
        # if redis_client:
        #     await redis_client.setex(text_hash, CACHE_TTL, res.json())
        results.append(res)
        
    return results

@app.get("/explain/{post_id}")
async def explain(post_id: str, text: str):
    loop = asyncio.get_event_loop()
    shap_vals = await loop.run_in_executor(executor, do_explain, text)
    return {"post_id": post_id, "shap_values": shap_vals}
