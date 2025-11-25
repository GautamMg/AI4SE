from typing import Dict, List, Optional

from pydantic import BaseModel, Field, conlist, confloat, constr


class AoiConfig(BaseModel):
    id: constr(strip_whitespace=True, min_length=1, max_length=64)
    name: constr(strip_whitespace=True, min_length=1, max_length=128)
    polygon_ref: constr(strip_whitespace=True, min_length=1, max_length=256) = (
        Field(description="Reference to stored GeoJSON AOI polygon")
    )
    altitude_m: confloat(ge=5, le=300) = Field(
        description="Planned flight altitude in meters"
    )
    overlap_percent: confloat(ge=0.0, le=90.0) = Field(
        default=60.0,
        description="Front/side overlap percentage",
    )


class SpeciesThreshold(BaseModel):
    aoi_id: constr(strip_whitespace=True, min_length=1, max_length=64)
    species: constr(strip_whitespace=True, min_length=1, max_length=64)
    min_confidence: confloat(ge=0.0, le=1.0)


class ModelConfig(BaseModel):
    model_version_id: constr(strip_whitespace=True, min_length=1, max_length=64)
    rollout_group: Optional[constr(strip_whitespace=True, max_length=64)] = Field(
        default=None, description="Optional rollout ring identifier"
    )
    notes: Optional[constr(strip_whitespace=True, max_length=256)] = None


class ConfigChangeSetCreateRequest(BaseModel):
    aois: conlist(AoiConfig, min_items=1, max_items=20)
    species_thresholds: conlist(SpeciesThreshold, min_items=1, max_items=100)
    model_config: ModelConfig


class ConfigChangeSet(BaseModel):
    config_version: str
    created_at: str
    actor_id: str
    actor_role: str
    aois: List[AoiConfig]
    species_thresholds: List[SpeciesThreshold]
    model_config: ModelConfig
    signature: str


class HealthStatus(BaseModel):
    status: str
    metrics: Dict[str, int]
    timestamp: str
