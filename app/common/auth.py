import os
import time
from fastapi import Request, HTTPException
from jose import jwt

ALG = "HS256"
SECRET = os.getenv("INTERNAL_JWT_SECRET", "change-me")


def issue_token(issuer: str, audience: str, ttl_s: int = 60) -> str:
    now = int(time.time())
    payload = {"iss": issuer, "aud": audience, "iat": now, "exp": now + ttl_s}
    return jwt.encode(payload, SECRET, algorithm=ALG)


async def verify_request(req: Request, expected_aud: str):
    if os.getenv("FEATURE_GATEWAY_AUTH", "true").lower() not in {"1", "true", "yes"}:
        return
    h = req.headers.get("authorization", "")
    if not h.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")
    tok = h.split(" ", 1)[1]
    try:
        jwt.decode(tok, SECRET, algorithms=[ALG], audience=expected_aud)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"invalid token: {e}")

