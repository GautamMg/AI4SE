from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from .config import get_settings

security = HTTPBearer(auto_error=True)


class Actor(BaseModel):
    id: str
    role: str


def get_current_actor(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Actor:
    """
    Simple bearer-token auth.

    - Token must match API_TOKEN.
    - Actor identity and role are taken from X-Actor-Id and X-Actor-Role headers.
    """
    settings = get_settings()
    if credentials.credentials != settings.api_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bearer token",
        )

    actor_id = request.headers.get("X-Actor-Id", "unknown-actor")
    actor_role = request.headers.get("X-Actor-Role", "UnknownRole")
    return Actor(id=actor_id, role=actor_role)
