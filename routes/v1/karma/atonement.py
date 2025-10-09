from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
from utils.atonement import validate_atonement_proof, get_user_atonement_plans

router = APIRouter()

class AtonementSubmission(BaseModel):
    user_id: str
    plan_id: str
    atonement_type: str
    amount: float
    proof_text: Optional[str] = None
    tx_hash: Optional[str] = None

@router.post("/submit")
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
        "plan": updated_plan
    }

@router.post("/submit-with-file")
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
        "plan": updated_plan
    }

@router.get("/plans/{user_id}")
async def get_atonement_plans(user_id: str):
    """
    Get all atonement plans for a user.
    """
    plans = get_user_atonement_plans(user_id)
    
    return {
        "status": "success",
        "user_id": user_id,
        "plans": plans
    }