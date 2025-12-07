import datetime as dt
import hashlib
import json
import logging
from typing import Optional

from .auth import Actor
from .config import get_settings
from . import db, metrics
from .models import (
    AoiConfig,
    ConfigChangeSet,
    ConfigChangeSetCreateRequest,
    ModelConfig,
    SpeciesThreshold,
)

logger = logging.getLogger(__name__)


def _now_utc_iso() -> str:
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def create_change_set(
    actor: Actor, payload: ConfigChangeSetCreateRequest
) -> ConfigChangeSet:
    """
    Create a new signed configuration change set.

    - Canonicalizes the payload JSON.
    - Computes SHA-256(signatureSalt + canonicalJson).
    - Persists the versioned config.
    """
    settings = get_settings()
    created_at = _now_utc_iso()
    payload_dict = payload.dict()
    canonical = json.dumps(payload_dict, sort_keys=True, separators=(",", ":"))
    signature = hashlib.sha256(
        (settings.config_signing_salt + canonical).encode("utf-8")
    ).hexdigest()

    aois_json = json.dumps(payload_dict["aois"])
    species_json = json.dumps(payload_dict["species_thresholds"])
    model_json = json.dumps(payload_dict["model_config"])

    config_version, _ = db.insert_config_version(
        actor_id=actor.id,
        actor_role=actor.role,
        created_at=created_at,
        aois_json=aois_json,
        species_json=species_json,
        model_json=model_json,
        signature=signature,
    )

    metrics.increment("config_change_sets_created")
    audit_log("config.change_set.created", actor, config_version)

    return ConfigChangeSet(
        config_version=config_version,
        created_at=created_at,
        actor_id=actor.id,
        actor_role=actor.role,
        aois=payload.aois,
        species_thresholds=payload.species_thresholds,
        model_config=payload.model_config,
        signature=signature,
    )


def get_latest_config() -> Optional[ConfigChangeSet]:
    """Return the most recent config as a domain model."""
    row = db.fetch_latest_config_row()
    if row is None:
        return None

    aois = [AoiConfig(**obj) for obj in json.loads(row["aois_json"])]
    species = [
        SpeciesThreshold(**obj)
        for obj in json.loads(row["species_thresholds_json"])
    ]
    model_cfg = ModelConfig(**json.loads(row["model_config_json"]))

    return ConfigChangeSet(
        config_version=row["config_version"],
        created_at=row["created_at"],
        actor_id=row["actor_id"],
        actor_role=row["actor_role"],
        aois=aois,
        species_thresholds=species,
        model_config=model_cfg,
        signature=row["signature"],
    )


def audit_log(event: str, actor: Actor, config_version: str) -> None:
    """Emit a structured audit log and bump a metric counter."""
    logger.info(
        "audit event=%s actor_id=%s actor_role=%s config_version=%s",
        event,
        actor.id,
        actor.role,
        config_version,
    )
    metrics.increment(f"audit_{event}")
