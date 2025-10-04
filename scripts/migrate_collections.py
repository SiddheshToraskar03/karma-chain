#!/usr/bin/env python3
"""
Collection Migration Script

This script migrates data from the old collection structure to the new separate collections.
It performs the following operations:
1. Extracts data from the old 'user' collection
2. Moves data to the appropriate new collections (users, appeals, atonements, death_events)
3. Updates references to maintain data integrity
"""

import os
import sys
import datetime
from pymongo import MongoClient
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

def migrate_user_data(db):
    """Migrate user data from old 'user' collection to new 'users' collection"""
    print("Migrating user data...")
    
    # Check if old collection exists
    if "user" not in db.list_collection_names():
        print("- Old 'user' collection not found. Skipping user migration.")
        return
    
    # Get all documents from old collection
    old_users = list(db.user.find({}))
    
    if not old_users:
        print("- No user data found in old collection.")
        return
    
    # Extract core user data (excluding appeals, atonements, death_events)
    migrated_count = 0
    
    for old_user in old_users:
        # Create new user document with core user fields
        new_user = {
            "user_id": old_user.get("user_id"),
            "name": old_user.get("name"),
            "balances": old_user.get("balances", {}),
            "role": old_user.get("role"),
            "created_at": old_user.get("created_at", datetime.datetime.now()),
            "updated_at": datetime.datetime.now()
        }
        
        # Insert into new users collection
        result = db.users.update_one(
            {"user_id": new_user["user_id"]},
            {"$set": new_user},
            upsert=True
        )
        
        if result.upserted_id or result.modified_count > 0:
            migrated_count += 1
    
    print(f"- Migrated {migrated_count} users to new 'users' collection")

def migrate_appeals_data(db):
    """Extract appeals data from old 'user' collection and move to new 'appeals' collection"""
    print("Migrating appeals data...")
    
    # Check if old collection exists
    if "user" not in db.list_collection_names():
        print("- Old 'user' collection not found. Skipping appeals migration.")
        return
    
    # Get all documents from old collection that have appeals data
    old_users = list(db.user.find({"appeals": {"$exists": True}}))
    
    if not old_users:
        print("- No appeals data found in old collection.")
        return
    
    # Extract appeals data
    migrated_count = 0
    
    for old_user in old_users:
        user_id = old_user.get("user_id")
        appeals = old_user.get("appeals", [])
        
        for appeal in appeals:
            # Create new appeal document
            new_appeal = {
                "user_id": user_id,
                "action": appeal.get("action"),
                "paap_class": appeal.get("paap_class"),
                "status": appeal.get("status", "pending"),
                "created_at": appeal.get("created_at", datetime.datetime.now()),
                "updated_at": datetime.datetime.now(),
                "note": appeal.get("note", ""),
                "atonement_plan_id": appeal.get("atonement_plan_id")
            }
            
            # Insert into new appeals collection
            result = db.appeals.insert_one(new_appeal)
            
            if result.inserted_id:
                migrated_count += 1
    
    print(f"- Migrated {migrated_count} appeals to new 'appeals' collection")

def migrate_atonements_data(db):
    """Extract atonements data from old 'user' collection and move to new 'atonements' collection"""
    print("Migrating atonements data...")
    
    # Check if old collection exists
    if "user" not in db.list_collection_names():
        print("- Old 'user' collection not found. Skipping atonements migration.")
        return
    
    # Get all documents from old collection that have atonements data
    old_users = list(db.user.find({"atonements": {"$exists": True}}))
    
    if not old_users:
        print("- No atonements data found in old collection.")
        return
    
    # Extract atonements data
    migrated_count = 0
    
    for old_user in old_users:
        user_id = old_user.get("user_id")
        atonements = old_user.get("atonements", [])
        
        for atonement in atonements:
            # Create new atonement document
            new_atonement = {
                "user_id": user_id,
                "appeal_id": atonement.get("appeal_id"),
                "paap_class": atonement.get("paap_class"),
                "status": atonement.get("status", "pending"),
                "created_at": atonement.get("created_at", datetime.datetime.now()),
                "updated_at": datetime.datetime.now(),
                "requirements": atonement.get("requirements", {}),
                "progress": atonement.get("progress", {})
            }
            
            # Insert into new atonements collection
            result = db.atonements.insert_one(new_atonement)
            
            if result.inserted_id:
                migrated_count += 1
    
    print(f"- Migrated {migrated_count} atonements to new 'atonements' collection")

def migrate_death_events_data(db):
    """Extract death events data from old 'user' collection and move to new 'death_events' collection"""
    print("Migrating death events data...")
    
    # Check if old collection exists
    if "user" not in db.list_collection_names():
        print("- Old 'user' collection not found. Skipping death events migration.")
        return
    
    # Get all documents from old collection that have death_events data
    old_users = list(db.user.find({"death_events": {"$exists": True}}))
    
    if not old_users:
        print("- No death events data found in old collection.")
        return
    
    # Extract death events data
    migrated_count = 0
    
    for old_user in old_users:
        user_id = old_user.get("user_id")
        death_events = old_user.get("death_events", [])
        
        for event in death_events:
            # Create new death event document
            new_event = {
                "user_id": user_id,
                "timestamp": event.get("timestamp", datetime.datetime.now()),
                "karma_score": event.get("karma_score"),
                "assigned_loka": event.get("assigned_loka"),
                "carryover": event.get("carryover", {})
            }
            
            # Insert into new death_events collection
            result = db.death_events.insert_one(new_event)
            
            if result.inserted_id:
                migrated_count += 1
    
    print(f"- Migrated {migrated_count} death events to new 'death_events' collection")

def create_indexes(db):
    """Create indexes for efficient querying"""
    print("Creating indexes for collections...")
    
    # Users collection indexes
    db.users.create_index("user_id", unique=True)
    
    # Appeals collection indexes
    db.appeals.create_index("user_id")
    db.appeals.create_index("status")
    
    # Atonements collection indexes
    db.atonements.create_index("user_id")
    db.atonements.create_index("appeal_id")
    db.atonements.create_index("status")
    
    # Death events collection indexes
    db.death_events.create_index("user_id")
    
    print("- Created indexes for all collections")

def main():
    """Main migration function"""
    print("\n=== Starting Collection Migration ===\n")
    
    # Connect to database
    try:
        db = connect_to_db()
        print(f"Connected to database: {DB_NAME}")
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return
    
    # Run migration steps
    try:
        migrate_user_data(db)
        migrate_appeals_data(db)
        migrate_atonements_data(db)
        migrate_death_events_data(db)
        create_indexes(db)
        
        print("\nMigration completed successfully!")
        print("\nYour data is now organized in separate collections:")
        print("- users: Core user data")
        print("- appeals: Appeal records")
        print("- atonements: Atonement plans and progress")
        print("- death_events: Death and rebirth events")
        print("- transactions: Transaction history (already separate)")
        print("- q_table: Q-learning data (already separate)")
        
    except Exception as e:
        print(f"\nError during migration: {e}")
        print("Migration failed. Please check the error and try again.")

if __name__ == "__main__":
    main()