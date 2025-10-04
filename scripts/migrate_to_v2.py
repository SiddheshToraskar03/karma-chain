#!/usr/bin/env python3
"""
KarmaChain v2 Migration Script

This script migrates existing KarmaChain data to the new dual-ledger system.
It performs the following operations:
1. Creates new collections for appeals and atonements
2. Updates user schema to include PaapTokens
3. Creates indexes for efficient querying
4. Initializes default values for new fields
"""

import os
import sys
import json
import datetime
from pymongo import MongoClient, ASCENDING
from bson.objectid import ObjectId
from dotenv import load_dotenv

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Import configuration
from config import MONGO_URI, DB_NAME

def connect_to_db():
    """Connect to MongoDB and return database object"""
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]

def create_new_collections(db):
    """Create new collections required for KarmaChain v2"""
    print("Creating new collections...")
    
    # Create appeals collection if it doesn't exist
    if "appeals" not in db.list_collection_names():
        db.create_collection("appeals")
        print("- Created 'appeals' collection")
    else:
        print("- 'appeals' collection already exists")
    
    # Create atonements collection if it doesn't exist
    if "atonements" not in db.list_collection_names():
        db.create_collection("atonements")
        print("- Created 'atonements' collection")
    else:
        print("- 'atonements' collection already exists")
    
    # Create indexes for efficient querying
    db.appeals.create_index([("user_id", ASCENDING)])
    db.appeals.create_index([("status", ASCENDING)])
    db.atonements.create_index([("user_id", ASCENDING)])
    db.atonements.create_index([("appeal_id", ASCENDING)])
    db.atonements.create_index([("status", ASCENDING)])
    
    print("Created indexes for new collections")

def update_user_schema(db):
    """Update user schema to include PaapTokens"""
    print("Updating user schema...")
    
    # Get all users
    users = db.users.find({})
    updated_count = 0
    
    for user in users:
        updates_needed = False
        
        # Check if PaapTokens field exists
        if "balances" in user and "PaapTokens" not in user["balances"]:
            updates_needed = True
            
            # Initialize PaapTokens with zero values
            update_operation = {
                "$set": {
                    "balances.PaapTokens": {
                        "minor": 0,
                        "medium": 0,
                        "maha": 0
                    }
                }
            }
            
            # Update user document
            db.users.update_one({"_id": user["_id"]}, update_operation)
            updated_count += 1
    
    print(f"Updated {updated_count} user documents with PaapTokens field")

def create_sample_data(db):
    """Create sample data for testing (optional)"""
    print("Creating sample data...")
    
    # Check if sample data already exists
    if db.appeals.count_documents({}) > 0 or db.atonements.count_documents({}) > 0:
        print("Sample data already exists. Skipping...")
        return
    
    # Get a random user for sample data
    user = db.users.find_one({})
    if not user:
        print("No users found. Skipping sample data creation...")
        return
    
    user_id = user["_id"]
    
    # Create a sample appeal
    appeal_id = ObjectId()
    appeal = {
        "_id": appeal_id,
        "user_id": user_id,
        "action": "disrespect_guru",
        "paap_class": "medium",
        "status": "pending",
        "created_at": datetime.datetime.now().isoformat(),
        "atonement_plan_id": None
    }
    db.appeals.insert_one(appeal)
    
    # Create a sample atonement plan
    atonement_plan = {
        "_id": ObjectId(),
        "user_id": user_id,
        "appeal_id": appeal_id,
        "paap_class": "medium",
        "requirements": {
            "Jap": 108,
            "Tap": 3,
            "Bhakti": 1,
            "Daan": 0.05
        },
        "progress": {
            "Jap": 0,
            "Tap": 0,
            "Bhakti": 0,
            "Daan": 0
        },
        "status": "active",
        "created_at": datetime.datetime.now().isoformat(),
        "completed_at": None
    }
    db.atonements.insert_one(atonement_plan)
    
    # Update the appeal with the atonement plan ID
    db.appeals.update_one(
        {"_id": appeal_id},
        {"$set": {"atonement_plan_id": atonement_plan["_id"]}}
    )
    
    print("Created sample appeal and atonement plan")

def update_action_history(db):
    """Update action history to include paap classification"""
    print("Updating action history...")
    
    # Load the mahapaap map
    try:
        with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                              "data", "vedic_corpus", "mahapaap_map.json"), "r") as f:
            mahapaap_map = json.load(f)
            actions_map = mahapaap_map.get("actions", {})
    except (FileNotFoundError, json.JSONDecodeError):
        print("Warning: Could not load mahapaap_map.json. Skipping action history update.")
        return
    
    # Get all transactions
    transactions = db.transactions.find({"type": "action"})
    updated_count = 0
    
    for transaction in transactions:
        action = transaction.get("action")
        
        # Check if action exists in the mahapaap map
        if action in actions_map:
            paap_class = actions_map[action].get("class")
            
            # Update transaction with paap classification
            db.transactions.update_one(
                {"_id": transaction["_id"]},
                {"$set": {"paap_class": paap_class}}
            )
            updated_count += 1
    
    print(f"Updated {updated_count} transactions with paap classification")

def main():
    """Main migration function"""
    print("Starting KarmaChain v2 migration...")
    
    # Connect to database
    try:
        db = connect_to_db()
        print(f"Connected to database: {DB_NAME}")
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return
    
    # Run migration steps
    try:
        create_new_collections(db)
        update_user_schema(db)
        update_action_history(db)
        
        # Optional: Create sample data
        create_sample_data(db)
        
        print("\nMigration completed successfully!")
        print("\nKarmaChain v2 is now ready to use.")
        print("You can now run the application with the new dual-ledger karmic engine.")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        print("Migration failed. Please check the error and try again.")

if __name__ == "__main__":
    main()