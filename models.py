from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class LogActionRequest(BaseModel):
    user_id: str
    role: str
    action: str
    note: Optional[str] = None

class RedeemRequest(BaseModel):
    user_id: str
    token_type: str
    amount: float

class KarmaEvent(BaseModel):
    """Model for storing unified events in karma_events collection"""
    event_id: str
    event_type: str
    data: Dict[str, Any]
    timestamp: datetime
    source: Optional[str] = None
    status: str = "processed"  # processed, failed, pending
    response_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime = None
    updated_at: Optional[datetime] = None
