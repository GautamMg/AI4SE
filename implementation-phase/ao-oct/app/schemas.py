from typing import List, Optional, Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class EngRunResponse(BaseModel):
    run_id: str
    status: Literal["PENDING", "PROCESSING", "SUCCEEDED", "FAILED"]
    model_name: str
    model_version: Optional[str] = None
    confidence_threshold: float
    created_at: str
    updated_at: str
    overlay_image_uri: Optional[str] = None
    metrics_csv_uri: Optional[str] = None
    metrics_json_uri: Optional[str] = None
    manifest_uri: Optional[str] = None
    dip_columns: List[int]
    dip_count: int

