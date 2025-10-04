#!/usr/bin/env python3
"""
Test Collections Script

This script tests the new collection structure by inserting and retrieving data
from each of the separate collections.
"""

from pymongo import MongoClient
import datetime
from config import MONGO_URI, DB_NAME
from database import users_col, transactions_col, qtable_col, appeals_col, atonements_col, death_events_col

def test_collections():
    """Test inserting and retrieving data from each collection"""
    print("\n=== Testing Collection Structure ===\n")
    
    # Generate a unique test user ID
    test_user_id = f"test_user_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Test users collection
    print("Testing users collection...")
    user_data = {
        "user_id": test_user_id,
        "name": "Test User",
        "balances": {
            "DharmaPoints": 100,
            "SevaPoints": 50,
            "PunyaTokens": {"minor": 10, "medium": 5, "major": 2},
            "PaapTokens": {"minor": 5, "medium": 3, "maha": 1}
        },
        "role": "learner",
        "created_at": datetime.datetime.now()
    }
    
    users_result = users_col.insert_one(user_data)
    print(f"- Inserted user with ID: {users_result.inserted_id}")
    
    # Test transactions collection
    print("\nTesting transactions collection...")
    transaction_data = {
        "user_id": test_user_id,
        "action": "completing_lessons",
        "points_earned": 5,
        "timestamp": datetime.datetime.now()
    }
    
    transactions_result = transactions_col.insert_one(transaction_data)
    print(f"- Inserted transaction with ID: {transactions_result.inserted_id}")
    
    # Test q_table collection
    print("\nTesting q_table collection...")
    qtable_data = {
        "state": "learner",
        "action": "completing_lessons",
        "reward": 5,
        "next_state": "volunteer"
    }
    
    qtable_result = qtable_col.insert_one(qtable_data)
    print(f"- Inserted q_table entry with ID: {qtable_result.inserted_id}")
    
    # Test appeals collection
    print("\nTesting appeals collection...")
    appeal_data = {
        "user_id": test_user_id,
        "action": "disrespect_guru",
        "paap_class": "medium",
        "status": "pending",
        "created_at": datetime.datetime.now(),
        "note": "Test appeal"
    }
    
    appeals_result = appeals_col.insert_one(appeal_data)
    appeal_id = appeals_result.inserted_id
    print(f"- Inserted appeal with ID: {appeal_id}")
    
    # Test atonements collection
    print("\nTesting atonements collection...")
    atonement_data = {
        "user_id": test_user_id,
        "appeal_id": str(appeal_id),
        "paap_class": "medium",
        "status": "pending",
        "created_at": datetime.datetime.now(),
        "requirements": {
            "Jap": 108,
            "Tap": 3,
            "Bhakti": 7,
            "Daan": 0
        },
        "progress": {
            "Jap": 0,
            "Tap": 0,
            "Bhakti": 0,
            "Daan": 0
        }
    }
    
    atonements_result = atonements_col.insert_one(atonement_data)
    print(f"- Inserted atonement with ID: {atonements_result.inserted_id}")
    
    # Test death_events collection
    print("\nTesting death_events collection...")
    death_event_data = {
        "user_id": test_user_id,
        "timestamp": datetime.datetime.now(),
        "karma_score": 75,
        "assigned_loka": "Swarga",
        "carryover": {
            "carryover_paap": 1,
            "carryover_punya": 5,
            "starting_level": "volunteer"
        }
    }
    
    death_events_result = death_events_col.insert_one(death_event_data)
    print(f"- Inserted death event with ID: {death_events_result.inserted_id}")
    
    # Verify data retrieval from each collection
    print("\n=== Verifying Data Retrieval ===\n")
    
    # Retrieve user
    retrieved_user = users_col.find_one({"user_id": test_user_id})
    print(f"Retrieved user: {retrieved_user['name']} (Role: {retrieved_user['role']})")
    
    # Retrieve transaction
    retrieved_transaction = transactions_col.find_one({"user_id": test_user_id})
    print(f"Retrieved transaction: {retrieved_transaction['action']} (Points: {retrieved_transaction['points_earned']})")
    
    # Retrieve q_table entry
    retrieved_qtable = qtable_col.find_one({"state": "learner", "action": "completing_lessons"})
    print(f"Retrieved q_table entry: {retrieved_qtable['state']} -> {retrieved_qtable['next_state']}")
    
    # Retrieve appeal
    retrieved_appeal = appeals_col.find_one({"user_id": test_user_id})
    print(f"Retrieved appeal: {retrieved_appeal['action']} (Status: {retrieved_appeal['status']})")
    
    # Retrieve atonement
    retrieved_atonement = atonements_col.find_one({"user_id": test_user_id})
    print(f"Retrieved atonement: {retrieved_atonement['paap_class']} (Status: {retrieved_atonement['status']})")
    
    # Retrieve death event
    retrieved_death = death_events_col.find_one({"user_id": test_user_id})
    print(f"Retrieved death event: Loka - {retrieved_death['assigned_loka']} (Karma: {retrieved_death['karma_score']})")
    
    print("\n=== Test Completed Successfully ===")
    print("All collections are working correctly!")
    
    # Clean up test data
    print("\nCleaning up test data...")
    users_col.delete_one({"user_id": test_user_id})
    transactions_col.delete_one({"user_id": test_user_id})
    appeals_col.delete_one({"user_id": test_user_id})
    atonements_col.delete_one({"user_id": test_user_id})
    death_events_col.delete_one({"user_id": test_user_id})
    print("Test data cleaned up.")

if __name__ == "__main__":
    test_collections()