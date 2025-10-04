from fastapi import APIRouter, HTTPException
from database import users_col
from utils.tokens import apply_decay_and_expiry
from utils.merit import compute_user_merit_score

router = APIRouter()

@router.get("/user-status/{user_id}")
def user_status(user_id: str):
    user = users_col.find_one({"user_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user = apply_decay_and_expiry(user)
    merit_score = compute_user_merit_score(user)
    return {
        "user_id": user_id,
        "role": user.get("role"),
        "merit_score": merit_score,
        "balances": user.get("balances"),
        "history_count": len(user.get("history", []))
    }
