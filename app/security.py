# app/security.py
import json
import logging
import os
import re
from functools import lru_cache

import requests
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from .authz import AuthzEngine

# --- Logger Setup ---
log = logging.getLogger(__name__)

# --- Configuration ---
KEYCLOAK_SERVER_URL = os.getenv("KEYCLOAK_SERVER_URL")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM")
KEYCLOAK_AUDIENCE = os.getenv("KEYCLOAK_AUDIENCE")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID")
KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET")
IS_AUTH_DEBUG = os.getenv("SUPERVITY_AUTH_DEBUG", "false").lower() == "true"
jwks_url = (
    f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/certs"
)
introspection_url = f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token/introspect"

# auto_error=False is critical. It makes the "Authorization" header optional.
# This allows the same dependency (`verify_access`) to process requests for
# both public and protected routes without immediately failing if a token is not present.
# The decision to require a token is deferred to the authorization engine.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

# --- Singleton Engine Instance ---
# We create one instance of the engine when the application starts.
# This is efficient as policies are loaded from disk only once.
# This instance is imported by main.py for manual, context-aware checks.
authz_engine = AuthzEngine()


@lru_cache(maxsize=1)
def get_jwks():
    """Fetches and caches the JSON Web Key Set (JWKS) from Keycloak."""
    log.info(f"Fetching JWKS from: {jwks_url}")
    try:
        response = requests.get(jwks_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Could not fetch JWKS from Keycloak: {e}")


def introspect_token(token: str) -> dict:
    """Makes a back-channel call to Keycloak's introspection endpoint to validate the token."""
    payload = {
        "client_id": KEYCLOAK_CLIENT_ID,
        "client_secret": KEYCLOAK_CLIENT_SECRET,
        "token": token,
    }
    try:
        response = requests.post(introspection_url, data=payload)
        response.raise_for_status()
        introspection_result = response.json()
        if not introspection_result.get("active"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is not active"
            )
        return introspection_result
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token introspection failed: {e}",
        )


def get_current_user(token: str | None = Depends(oauth2_scheme)) -> dict | None:
    """
    Demo Mode: Returns a mock user object without JWT validation.
    """
    # Return mock user dictionary for Demo Mode
    return {
        "sub": "demo-user",
        "preferred_username": "Demo Admin",
        "realm_access": {"roles": ["admin"]}
    }


def verify_access(
    request: Request, current_user: dict | None = Depends(get_current_user)
):
    """
    Demo Mode: Allows all requests through without authorization checks.
    """
    # Demo Mode - allow all requests
    pass
