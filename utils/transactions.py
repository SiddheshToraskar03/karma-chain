from database import transactions_col, users_col
from datetime import datetime

def now_utc():
    return datetime.utcnow()

def log_transaction(user_id, action, reward, intent, reward_tier, punishment_name=None):
    tx = {
        "user_id": user_id,
        "action": action,
        "intent": intent,
        "reward": reward,
        "reward_tier": reward_tier,
        "timestamp": now_utc()
    }
    
    # Add punishment name if provided (for cheat transactions)
    if punishment_name:
        tx["punishment_name"] = punishment_name
    
    transactions_col.insert_one(tx)
    users_col.update_one({"user_id": user_id}, {"$push": {"history": tx}})
