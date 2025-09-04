from pydantic import BaseModel
from typing import List, Optional


class ValidateRequest(BaseModel):
    vendor_id: str
    solution_id: Optional[str] = None
    user_id: Optional[str] = None
    controls: Optional[List[str]] = None


class ControlResult(BaseModel):
    id: str
    passed: bool
    reason: Optional[str] = None
    evidence_id: Optional[str] = None


class ValidateResponse(BaseModel):
    vendor_id: str
    score: float
    failed: List[ControlResult]
    passed: List[ControlResult]
    source: str

