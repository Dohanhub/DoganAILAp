from __future__ import annotations

import os
import time
from datetime import datetime, timedelta
from typing import Any, Optional

import requests
from jose import JWTError, jwt  # type: ignore
from passlib.context import CryptContext  # type: ignore

from .config import get as get_config
from .database import SessionLocal
from . import models


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"
SECRET_KEY = get_config("SECRET_KEY") or get_config("JWT_SECRET")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def get_user(db: SessionLocal, email: str) -> models.User | None:
    return db.query(models.User).filter((models.User.email == email)).first()


def authenticate_user(db: SessionLocal, email: str, password: str) -> models.User | bool:
    user = get_user(db, email)
    if (not user) or (not verify_password(password, user.hashed_password)):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = (datetime.utcnow() + (expires_delta or timedelta(minutes=15)))
    to_encode.update({"exp": expire})
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY is not configured")
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def _get_claim(obj: Any, path: str) -> Any:
    try:
        cur = obj
        for part in path.split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                return None
        return cur
    except Exception:
        return None


_jwks_cache: dict[str, Any] = {}
_jwks_cache_at: float = 0.0


def _load_jwks() -> Optional[dict[str, Any]]:
    url = os.getenv("OIDC_JWKS_URL")
    if not url:
        return None
    global _jwks_cache, _jwks_cache_at
    now = time.time()
    if _jwks_cache and now - _jwks_cache_at < 300:
        return _jwks_cache
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        _jwks_cache = r.json()
        _jwks_cache_at = now
        return _jwks_cache
    except Exception:
        return _jwks_cache or None


def _try_verify_oidc(token: str) -> Optional[dict[str, Any]]:
    issuer = os.getenv("OIDC_ISSUER")
    audience = os.getenv("OIDC_AUDIENCE")
    if not issuer:
        return None
    jwks = _load_jwks()
    if not jwks:
        return None
    try:
        data = jwt.decode(
            token, jwks, algorithms=["RS256", "RS512", "ES256"], audience=audience, issuer=issuer
        )
        return data
    except Exception:
        return None


def get_current_user(token: str, db: SessionLocal):
    from fastapi import HTTPException, status

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Try OIDC first if configured
    data = _try_verify_oidc(token)
    email: Optional[str] = None
    role: Optional[str] = None
    if data:
        email_claim = os.getenv("OIDC_EMAIL_CLAIM", "email")
        roles_claim = os.getenv("OIDC_ROLES_CLAIM", "roles")
        tenant_claim = os.getenv("OIDC_TENANT_CLAIM")
        email = _get_claim(data, email_claim) or data.get("sub")
        roles_val = _get_claim(data, roles_claim)
        if isinstance(roles_val, list):
            rs = {str(x).lower() for x in roles_val}
            if "admin" in rs:
                role = "admin"
            elif "auditor" in rs:
                role = "auditor"
            else:
                role = "user"
        if email:
            user = get_user(db, email)
            if not user:
                user = models.User(
                    email=email,
                    hashed_password=get_password_hash(os.urandom(8).hex()),
                    full_name=email.split("@")[0],
                    role=role or "user",
                )
                if tenant_claim:
                    tname = _get_claim(data, tenant_claim)
                    if tname:
                        t = db.query(models.Tenant).filter(models.Tenant.name == tname).first()
                        if not t and os.getenv("AUTO_CREATE_TENANT", "false").lower() in {"1", "true", "yes"}:
                            t = models.Tenant(name=str(tname))
                            db.add(t)
                            db.flush()
                        if t:
                            user.tenant_id = t.id
                db.add(user)
                db.commit()
                db.refresh(user)
            return user

    # Fallback: local JWT
    try:
        if not SECRET_KEY:
            raise credentials_exception
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(db, email)
    if user is None:
        raise credentials_exception
    return user

