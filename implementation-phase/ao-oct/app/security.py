import os

from fastapi import Header, HTTPException, status

API_TOKEN = os.getenv("API_TOKEN", "secret-token")


async def auth_bearer(authorization: str = Header("")):
    """Simple bearer-token auth for the slice."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing authorization header",
        )
    token = authorization.split(" ", 1)[1].strip()
    if token != API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    return {"caller": "aooct-user"}

