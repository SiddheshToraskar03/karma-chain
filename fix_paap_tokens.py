#!/usr/bin/env python3
"""
Fix PaapTokens structure for existing users.
This script converts PaapTokens from float to proper dictionary structure.
"""

from database import users_col
from datetime import datetime, timezone

def fix_paap_tokens_structure():
    """Fix PaapTokens structure for all users."""
    print("Starting PaapTokens structure fix...")
    
    # Find all users with PaapTokens as float (incorrect structure)
    users_with_float_paap = users_col.find({
        "balances.PaapTokens": {"$type": "double"}
    })
    
    fixed_count = 0
    for user in users_with_float_paap:
        user_id = user["user_id"]
        old_value = user["balances"]["PaapTokens"]
        
        # Convert float to proper dictionary structure
        new_paap_tokens = {
            "minor": float(old_value) if old_value > 0 else 0.0,
            "medium": 0.0,
            "maha": 0.0
        }
        
        # Update the user
        result = users_col.update_one(
            {"user_id": user_id},
            {"$set": {"balances.PaapTokens": new_paap_tokens}}
        )
        
        if result.modified_count > 0:
            fixed_count += 1
            print(f"Fixed user {user_id}: PaapTokens from {old_value} to {new_paap_tokens}")
    
    print(f"Fixed {fixed_count} users with incorrect PaapTokens structure.")
    
    # Also fix users with missing PaapTokens
    users_without_paap = users_col.find({
        "balances.PaapTokens": {"$exists": False}
    })
    
    missing_count = 0
    for user in users_without_paap:
        user_id = user["user_id"]
        
        # Add proper PaapTokens structure
        new_paap_tokens = {
            "minor": 0.0,
            "medium": 0.0,
            "maha": 0.0
        }
        
        # Update the user
        result = users_col.update_one(
            {"user_id": user_id},
            {"$set": {"balances.PaapTokens": new_paap_tokens}}
        )
        
        if result.modified_count > 0:
            missing_count += 1
            print(f"Added PaapTokens structure for user {user_id}")
    
    print(f"Added PaapTokens structure for {missing_count} users.")
    print("PaapTokens fix completed!")

if __name__ == "__main__":
    fix_paap_tokens_structure()