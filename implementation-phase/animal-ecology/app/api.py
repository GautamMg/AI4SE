import datetime as dt

from fastapi import APIRouter, Depends, HTTPException

from .auth import Actor, get_current_actor
from .models import ConfigChangeSet, ConfigChangeSetCreateRequest, HealthStatus
from . import metrics, services

router = APIRouter()


@router.post(
    "/config/change-sets",
    response_model=ConfigChangeSet,
    status_code=201,
    tags=["ConfigAdminAPI"],
)
def create_config_change_set(
    request: ConfigChangeSetCreateRequest,
    actor: Actor = Depends(get_current_actor),
) -> ConfigChangeSet:
    """Create a new versioned, signed configuration change set."""
    return services.create_change_set(actor=actor, payload=request)


@router.get(
    "/config/latest",
    response_model=ConfigChangeSet,
    tags=["ConfigAdminAPI"],
)
def get_latest_config(
    actor: Actor = Depends(get_current_actor),
) -> ConfigChangeSet:
    """Return the latest configuration; 404 if none exists yet."""
    config = services.get_latest_config()
    if config is None:
        raise HTTPException(status_code=404, detail="No config versions found")
    services.audit_log("config.latest.read", actor, config.config_version)
    return config


@router.get(
    "/health",
    response_model=HealthStatus,
    tags=["Observability"],
)
def health() -> HealthStatus:
    """Simple liveness endpoint with metric snapshot."""
    now = dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    return HealthStatus(status="ok", metrics=metrics.snapshot(), timestamp=now)
