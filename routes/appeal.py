from fastapi import APIRouter, HTTPException, Body, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import os
from datetime import datetime, timezone
from bson import ObjectId

from database import users_col, appeals_col, atonements_col, death_events_col
from utils.atonement import create_atonement_plan, validate_atonement_proof, get_user_atonement_plans
from utils.paap import classify_paap_action, calculate_paap_value
from utils.loka import compute_loka_assignment, create_rebirth_carryover

router = APIRouter()

def serialize_mongodb_doc(doc):
    """Helper function to serialize MongoDB documents"""
    if isinstance(doc, dict):
        return {k: serialize_mongodb_doc(v) for k, v in doc.items()}
    elif isinstance(doc, list):
        return [serialize_mongodb_doc(item) for item in doc]
    elif isinstance(doc, ObjectId):
        return str(doc)
    else:
        return doc

class AppealRequest(BaseModel):
    user_id: str
    action: str
    context: Optional[str] = None

class AtonementSubmission(BaseModel):
    user_id: str
    plan_id: str
    atonement_type: str
    amount: float
    proof_text: Optional[str] = None
    tx_hash: Optional[str] = None

class DeathEventRequest(BaseModel):
    user_id: str

@router.post("/appeal-karma/")
async def appeal_karma(request: AppealRequest):
    """
    User requests review of a Paap action and receives a prescribed prāyaśchitta plan.
    """
    # Check if user exists
    user = users_col.find_one({"user_id": request.user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Classify the action to determine Paap severity
    severity_class = classify_paap_action(request.action)
    if not severity_class:
        raise HTTPException(status_code=400, detail="Action does not qualify for appeal")
    
    # Create an atonement plan
    plan = create_atonement_plan(request.user_id, request.action, severity_class)
    if not plan:
        raise HTTPException(status_code=500, detail="Failed to create atonement plan")
    
    return {
        "status": "success",
        "message": "Appeal registered successfully",
        "plan": serialize_mongodb_doc(plan)
    }

@router.post("/submit-atonement/")
async def submit_atonement(submission: AtonementSubmission):
    """
    Submit proof for completion of an atonement task.
    """
    # Validate the submission
    success, message, updated_plan = validate_atonement_proof(
        submission.plan_id,
        submission.atonement_type,
        submission.amount,
        submission.proof_text,
        submission.tx_hash
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {
        "status": "success",
        "message": message,
        "plan": serialize_mongodb_doc(updated_plan)
    }

@router.post("/submit-atonement-with-file/")
async def submit_atonement_with_file(
    user_id: str = Form(...),
    plan_id: str = Form(...),
    atonement_type: str = Form(...),
    amount: float = Form(...),
    proof_text: Optional[str] = Form(None),
    tx_hash: Optional[str] = Form(None),
    proof_file: Optional[UploadFile] = File(None)
):
    """
    Submit proof for completion of an atonement task with file upload.
    """
    # Validate file size if provided (limit to 1MB)
    if proof_file:
        file_size = 0
        content = await proof_file.read()
        file_size = len(content)
        
        if file_size > 1024 * 1024:  # 1MB limit
            raise HTTPException(status_code=400, detail="File size exceeds 1MB limit")
        
        # Store file reference or content hash instead of actual file
        file_reference = f"{plan_id}_{datetime.now(timezone.utc).timestamp()}"
        proof_text = f"{proof_text or ''}\nFile reference: {file_reference}"
    
    # Validate the submission
    success, message, updated_plan = validate_atonement_proof(
        plan_id,
        atonement_type,
        amount,
        proof_text,
        tx_hash
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {
        "status": "success",
        "message": message,
        "plan": serialize_mongodb_doc(updated_plan)
    }

@router.get("/appeal-status/{user_id}")
async def appeal_status(user_id: str):
    """
    Shows open appeals and progress for a user.
    """
    plans = get_user_atonement_plans(user_id)
    
    return {
        "status": "success",
        "pending_plans": [serialize_mongodb_doc(p) for p in plans if p["status"] == "pending"],
        "completed_plans": [serialize_mongodb_doc(p) for p in plans if p["status"] == "completed"]
    }

@router.post("/death-event/")
async def death_event(request: DeathEventRequest):
    """
    Compute loka assignment for a user (used by game engine).
    """
    # Check if user exists
    user = users_col.find_one({"user_id": request.user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Compute loka assignment
    loka, description = compute_loka_assignment(user)
    
    # Create rebirth carryover
    carryover = create_rebirth_carryover(user)
    
    return {
        "status": "success",
        "user_id": request.user_id,
        "loka": loka,
        "description": description,
        "carryover": serialize_mongodb_doc(carryover)
    }