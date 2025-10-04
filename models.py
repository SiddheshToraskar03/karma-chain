from pydantic import BaseModel
from typing import Optional

class LogActionRequest(BaseModel):
    user_id: str
    role: str
    action: str
    note: Optional[str] = None

class RedeemRequest(BaseModel):
    user_id: str
    token_type: str
    amount: float
