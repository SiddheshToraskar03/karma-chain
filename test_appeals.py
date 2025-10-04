#!/usr/bin/env python3

from database import users_col, appeals_col, atonements_col
from utils.atonement import create_atonement_plan, get_user_atonement_plans
from utils.paap import classify_paap_action
from datetime import datetime
import uuid

def test_appeals_and_atonements():
    print("\n=== Testing Appeals and Atonements Collections ===\n")
    
    # Create a test user
    user_id = f"test_user_{uuid.uuid4().hex[:8]}"
    test_user = {
        "user_id": user_id,
        "username": "Test User",
        "role": "learner",
        "balances": {
            "PaapTokens": {
                "minor": 10,
                "medium": 5,
                "maha": 2
            }
        },
        "created_at": datetime.now()
    }
    
    # Insert test user
    users_col.insert_one(test_user)
    print(f"Created test user with ID: {user_id}")
    
    # Create an appeal and atonement plan
    paap_action = "disrespect_guru"
    severity_class = classify_paap_action(paap_action)
    
    # Create atonement plan (this should also create an appeal record)
    plan = create_atonement_plan(user_id, paap_action, severity_class)
    print(f"Created atonement plan with ID: {plan['plan_id']}")
    
    # Verify data in appeals collection
    appeal = appeals_col.find_one({"user_id": user_id})
    if appeal:
        print(f"Appeal saved in appeals collection: {appeal['paap_action']} (Status: {appeal['status']})")
    else:
        print("ERROR: Appeal not found in appeals collection!")
    
    # Verify data in atonements collection
    atonement = atonements_col.find_one({"user_id": user_id})
    if atonement:
        print(f"Atonement plan saved in atonements collection: {atonement['plan_id']} (Status: {atonement['status']})")
    else:
        print("ERROR: Atonement plan not found in atonements collection!")
    
    # Get user's atonement plans
    plans = get_user_atonement_plans(user_id)
    print(f"Retrieved {len(plans)} atonement plans for user")
    
    # Clean up test data
    print("\nCleaning up test data...")
    users_col.delete_one({"user_id": user_id})
    appeals_col.delete_one({"user_id": user_id})
    atonements_col.delete_one({"user_id": user_id})
    print("Test data cleaned up.")

if __name__ == "__main__":
    test_appeals_and_atonements()