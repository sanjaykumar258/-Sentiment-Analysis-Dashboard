from pydantic import BaseModel
from typing import Optional, Literal, Dict

class PredictRequest(BaseModel):
    text: str
    post_id: Optional[str] = None
    include_shap: bool = False

class PredictResponse(BaseModel):
    post_id: Optional[str]
    sentiment: Literal["Positive", "Negative", "Neutral"]
    confidence: float
    probabilities: Dict[str, float]
    shap_values: Optional[Dict] = None
    latency_ms: float
