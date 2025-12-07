from typing import List, Optional

from pydantic import BaseModel, Field


class BatchInfo(BaseModel):
    batch_id: int
    mission_id: str
    file_count: int
    total_bytes: int
    status: str


class ScanAndBatchRequest(BaseModel):
    root_path: str = Field(..., max_length=256)
    max_files_per_batch: int = Field(50, ge=1, le=1000)
    max_batch_bytes: int = Field(50 * 1024 * 1024, ge=1_000_000, le=2_000_000_000)


class ScanAndBatchResponse(BaseModel):
    mission_id: str
    batches: List[BatchInfo]


class UploadBatchRequest(BaseModel):
    session_key: Optional[str] = None


class UploadBatchResponse(BaseModel):
    batch_id: int
    session_key: str
    status: str
    remote_path: Optional[str] = None
    retry_count: int


class HealthResponse(BaseModel):
    status: str
