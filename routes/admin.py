from fastapi import APIRouter, HTTPException
from database import users_col
from utils.utils_user import create_user_if_missing
from config import ROLE_SEQUENCE
from bson import ObjectId
import json

router = APIRouter()

def serialize_document(doc):
    """Convert MongoDB document to JSON-serializable format"""
    if doc is None:
        return None
    if isinstance(doc, list):
        return [serialize_document(item) for item in doc]
    if isinstance(doc, dict):
        return {key: serialize_document(value) for key, value in doc.items()}
    if isinstance(doc, ObjectId):
        return str(doc)
    return doc

@router.post("/init-user/{user_id}")
def init_user(user_id: str, role: str = "learner"):
    if role not in ROLE_SEQUENCE:
        raise HTTPException(status_code=400, detail=f"Invalid role. choose from {ROLE_SEQUENCE}")
    
    user = create_user_if_missing(user_id, role=role)
    
    # Get user data and serialize it
    user_data = users_col.find_one({"user_id": user_id})
    serialized_user = serialize_document(user_data)
    
    return {"message": "user initialized", "user": serialized_user}