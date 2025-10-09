"""
KarmaChain Integration Demo
Tests the complete workflow: log-action → appeal → atonement → death → stats
Plus file upload functionality and all event types.
"""

import requests
import json
import time
import sys
import os
import tempfile
from datetime import datetime, timezone
from pprint import pprint

# Add parent directory to path for direct imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration
BASE_URL = "http://localhost:8000/v1/karma"
USER_ID = "test_user_123"

def test_full_karma_flow():
    """Test the complete karma flow using the unified event endpoint"""
    print("\n=== KARMACHAIN INTEGRATION DEMO ===\n")
    
    # Step 1: Log a negative action
    print("Step 1: Logging negative action...")
    action_payload = {
        "event_type": "life_event",
        "user_id": USER_ID,
        "data": {
            "action_type": "rule_violation",
            "description": "Test violation for integration demo",
            "evidence": "Integration test evidence",
            "severity": "medium"
        }
    }
    
    action_response = requests.post(f"{BASE_URL}/event", json=action_payload)
    print(f"Status: {action_response.status_code}")
    action_data = action_response.json()
    pprint(action_data)
    
    action_id = action_data.get("action_id")
    if not action_id:
        print("Error: Failed to get action_id from response")
        return False
    
    time.sleep(1)  # Brief pause between steps
    
    # Step 2: Submit an appeal
    print("\nStep 2: Submitting appeal...")
    appeal_payload = {
        "event_type": "appeal",
        "user_id": USER_ID,
        "data": {
            "action_id": action_id,
            "reason": "This is a test appeal for the integration demo",
            "evidence": "Integration demo evidence for appeal"
        }
    }
    
    appeal_response = requests.post(f"{BASE_URL}/event", json=appeal_payload)
    print(f"Status: {appeal_response.status_code}")
    appeal_data = appeal_response.json()
    pprint(appeal_data)
    
    time.sleep(1)  # Brief pause between steps
    
    # Step 3: Request atonement
    print("\nStep 3: Requesting atonement...")
    atonement_payload = {
        "event_type": "atonement",
        "user_id": USER_ID,
        "data": {
            "action_id": action_id,
            "severity": "medium",
            "request_type": "atonement_plan"
        }
    }
    
    atonement_response = requests.post(f"{BASE_URL}/event", json=atonement_payload)
    print(f"Status: {atonement_response.status_code}")
    atonement_data = atonement_response.json()
    pprint(atonement_data)
    
    time.sleep(1)  # Brief pause between steps
    
    # Step 4: Record death event
    print("\nStep 4: Recording death event...")
    death_payload = {
        "event_type": "death_event",
        "user_id": USER_ID,
        "data": {
            "cause": "integration_test",
            "details": "User died during integration testing",
            "location": "Test Environment",
            "witnesses": ["integration_test"]
        }
    }
    
    death_response = requests.post(f"{BASE_URL}/event", json=death_payload)
    print(f"Status: {death_response.status_code}")
    death_data = death_response.json()
    pprint(death_data)
    
    time.sleep(1)  # Brief pause between steps
    
    # Step 5: Get user stats
    print("\nStep 5: Retrieving user stats...")
    stats_payload = {
        "event_type": "stats_request",
        "user_id": USER_ID,
        "data": {
            "include_history": True,
            "include_transactions": True,
            "include_appeals": True,
            "include_atonements": True
        }
    }
    
    stats_response = requests.post(f"{BASE_URL}/event", json=stats_payload)
    print(f"Status: {stats_response.status_code}")
    stats_data = stats_response.json()
    pprint(stats_data)
    
    print("\n=== INTEGRATION TEST COMPLETE ===")
    return True

def test_file_upload_with_atonement():
    """Test file upload functionality with atonement using the unified event endpoint"""
    print("\n=== TESTING FILE UPLOAD WITH ATONEMENT ===\n")
    
    # Step 1: Create a test file for upload
    print("Step 1: Creating test file for upload...")
    test_file_content = """This is a test file for atonement submission.
    It contains evidence of good deeds performed to atone for past actions.
    
    Test evidence includes:
    - Volunteering at local shelter
    - Donating to charity
    - Helping neighbors with daily tasks
    """
    
    # Create a temporary file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_file_content)
        temp_file_path = f.name
    
    try:
        # Step 2: Submit atonement with file upload
        print("Step 2: Submitting atonement with file upload...")
        
        # Prepare the multipart form data
        with open(temp_file_path, 'rb') as f:
            files = {'file': ('atonement_evidence.txt', f, 'text/plain')}
            
            atonement_data = {
                "event_type": "atonement_with_file",
                "user_id": USER_ID,
                "data": {
                    "action_id": "test_action_123",
                    "severity": "medium",
                    "description": "Test atonement with file upload evidence",
                    "atonement_type": "file_submission"
                }
            }
            
            # Submit the atonement with file
            response = requests.post(
                f"{BASE_URL}/event/with-file",
                data={"event_data": json.dumps(atonement_data)},
                files=files
            )
            
            print(f"Status: {response.status_code}")
            result = response.json()
            pprint(result)
            
            if response.status_code == 200:
                print("✅ File upload with atonement successful!")
                file_id = result.get("file_id")
                atonement_id = result.get("atonement_id")
                print(f"File ID: {file_id}")
                print(f"Atonement ID: {atonement_id}")
                return True
            else:
                print(f"❌ File upload failed: {result}")
                return False
                
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

def test_all_event_types():
    """Test all supported event types in the unified event system"""
    print("\n=== TESTING ALL EVENT TYPES ===\n")
    
    event_types = [
        ("life_event", {"action_type": "help_others", "description": "Helped someone in need"}),
        ("atonement", {"action_id": "test_123", "severity": "minor"}),
        ("atonement_with_file", {"action_id": "test_123", "severity": "medium", "description": "Atonement with evidence"}),
        ("appeal", {"action_id": "test_123", "reason": "Test appeal"}),
        ("death_event", {"cause": "natural", "details": "Test death event"}),
        ("stats_request", {"include_history": True})
    ]
    
    results = {}
    
    for event_type, event_data in event_types:
        print(f"Testing {event_type}...")
        
        payload = {
            "event_type": event_type,
            "user_id": USER_ID,
            "data": event_data
        }
        
        # Use file upload endpoint for atonement_with_file
        if event_type == "atonement_with_file":
            # Create a simple test file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write("Test atonement evidence file")
                temp_file_path = f.name
            
            try:
                with open(temp_file_path, 'rb') as f:
                    files = {'file': ('test_evidence.txt', f, 'text/plain')}
                    response = requests.post(
                        f"{BASE_URL}/event/with-file",
                        data={"event_data": json.dumps(payload)},
                        files=files
                    )
            finally:
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
        else:
            response = requests.post(f"{BASE_URL}/event", json=payload)
        
        results[event_type] = {
            "status_code": response.status_code,
            "success": response.status_code == 200,
            "response": response.json() if response.status_code == 200 else response.text
        }
        
        print(f"  Status: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
        
        time.sleep(0.5)  # Brief pause between tests
    
    # Summary
    print("\n=== EVENT TYPE TEST SUMMARY ===")
    successful = sum(1 for result in results.values() if result["success"])
    total = len(event_types)
    print(f"Successful: {successful}/{total}")
    
    for event_type, result in results.items():
        status = "✅" if result["success"] else "❌"
        print(f"  {event_type}: {status}")
    
    return results

def comprehensive_karma_workflow_demo():
    """
    Comprehensive demo testing the complete karma workflow:
    log-action → appeal → atonement → death → stats
    """
    print("\n" + "="*80)
    print("🚀 COMPREHENSIVE KARMACHAIN WORKFLOW DEMO")
    print("="*80)
    print("Testing complete workflow: log-action → appeal → atonement → death → stats")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    demo_results = {
        "start_time": datetime.now().isoformat(),
        "user_id": USER_ID,
        "steps": {},
        "success": False
    }
    
    try:
        # Step 1: Log multiple karma actions (both positive and negative)
        print("\n📝 STEP 1: Logging Karma Actions")
        print("-" * 50)
        
        actions = [
            {
                "action_type": "help_elderly",
                "description": "Helped an elderly person cross the street safely",
                "severity": "minor",
                "expected_outcome": "positive"
            },
            {
                "action_type": "donate_food",
                "description": "Donated food to homeless shelter",
                "severity": "medium", 
                "expected_outcome": "positive"
            },
            {
                "action_type": "teach_dharma",
                "description": "Taught dharma principles to 5 students",
                "severity": "major",
                "expected_outcome": "positive"
            },
            {
                "action_type": "disrespect_guru",
                "description": "Spoke harshly to spiritual teacher",
                "severity": "medium",
                "expected_outcome": "negative"
            }
        ]
        
        action_ids = []
        for i, action_data in enumerate(actions, 1):
            print(f"\nAction {i}: {action_data['action_type']} ({action_data['expected_outcome']})")
            
            action_payload = {
                "event_type": "life_event",
                "user_id": USER_ID,
                "data": {
                    "action_type": action_data['action_type'],
                    "description": action_data['description'],
                    "severity": action_data['severity'],
                    "evidence": f"Integration demo evidence for {action_data['action_type']}"
                }
            }
            
            response = requests.post(f"{BASE_URL}/event", json=action_payload)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                action_id = result.get("action_id")
                if action_id:
                    action_ids.append(action_id)
                    print(f"✅ Action logged: {action_id}")
                else:
                    print(f"⚠️  Warning: No action_id returned")
            else:
                print(f"❌ Failed to log action: {response.text}")
                demo_results["steps"]["log_actions"] = {"status": "failed", "error": response.text}
                return demo_results
        
        demo_results["steps"]["log_actions"] = {
            "status": "success", 
            "action_ids": action_ids,
            "total_actions": len(action_ids)
        }
        print(f"\n✅ Successfully logged {len(action_ids)} karma actions")
        
        time.sleep(1)
        
        # Step 2: Submit appeal for the negative action
        print("\n🙏 STEP 2: Appeal Process")
        print("-" * 50)
        
        # Find the negative action ID (disrespect_guru)
        negative_action_id = None
        for i, action in enumerate(actions):
            if action['action_type'] == 'disrespect_guru' and i < len(action_ids):
                negative_action_id = action_ids[i]
                break
        
        if negative_action_id:
            appeal_payload = {
                "event_type": "appeal",
                "user_id": USER_ID,
                "data": {
                    "action_id": negative_action_id,
                    "reason": "I deeply regret speaking harshly to my spiritual teacher. I was overwhelmed with ego and failed to recognize the divine presence in my guru. I seek forgiveness and guidance to correct this grave mistake.",
                    "evidence": "Heartfelt confession and commitment to spiritual growth"
                }
            }
            
            response = requests.post(f"{BASE_URL}/event", json=appeal_payload)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                appeal_data = response.json()
                appeal_id = appeal_data.get("appeal_id")
                print(f"✅ Appeal submitted: {appeal_id}")
                print(f"Reason: {appeal_payload['data']['reason'][:100]}...")
                demo_results["steps"]["appeal"] = {"status": "success", "appeal_id": appeal_id}
            else:
                print(f"❌ Appeal failed: {response.text}")
                demo_results["steps"]["appeal"] = {"status": "failed", "error": response.text}
        else:
            print("⚠️  Warning: Could not find negative action for appeal")
            demo_results["steps"]["appeal"] = {"status": "skipped", "reason": "No negative action found"}
        
        time.sleep(1)
        
        # Step 3: Request atonement
        print("\n🕉️ STEP 3: Atonement Plan")
        print("-" * 50)
        
        atonement_payload = {
            "event_type": "atonement",
            "user_id": USER_ID,
            "data": {
                "action_id": negative_action_id if negative_action_id else action_ids[-1],
                "severity": "medium",
                "request_type": "atonement_plan"
            }
        }
        
        response = requests.post(f"{BASE_URL}/event", json=atonement_payload)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            atonement_data = response.json()
            atonement_plan = atonement_data.get("atonement_plan")
            plan_id = atonement_data.get("plan_id")
            
            print(f"✅ Atonement plan created: {plan_id}")
            if atonement_plan:
                print("Requirements:")
                for req, amount in atonement_plan.get('requirements', {}).items():
                    print(f"  - {req}: {amount}")
            
            demo_results["steps"]["atonement"] = {
                "status": "success",
                "plan_id": plan_id,
                "plan": atonement_plan
            }
            
            # Simulate completing atonement requirements
            print("\n📿 Simulating atonement completion...")
            complete_payload = {
                "event_type": "atonement",
                "user_id": USER_ID,
                "data": {
                    "plan_id": plan_id,
                    "atonement_type": "complete",
                    "progress": {
                        "Jap": 1080,
                        "Tap": 7,
                        "Bhakti": 3,
                        "Daan": 0.1
                    }
                }
            }
            
            complete_response = requests.post(f"{BASE_URL}/event", json=complete_payload)
            if complete_response.status_code == 200:
                print("✅ Atonement completed successfully!")
                demo_results["steps"]["atonement"]["completed"] = True
            else:
                print(f"⚠️  Atonement completion failed: {complete_response.text}")
                demo_results["steps"]["atonement"]["completed"] = False
        else:
            print(f"❌ Atonement failed: {response.text}")
            demo_results["steps"]["atonement"] = {"status": "failed", "error": response.text}
        
        time.sleep(1)
        
        # Step 4: Record death event
        print("\n⚰️ STEP 4: Death Event Processing")
        print("-" * 50)
        
        death_payload = {
            "event_type": "death_event",
            "user_id": USER_ID,
            "data": {
                "cause": "natural_causes",
                "details": "User completed their earthly journey during integration testing",
                "location": "Home",
                "witnesses": ["family_member_1", "spiritual_teacher"]
            }
        }
        
        response = requests.post(f"{BASE_URL}/event", json=death_payload)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            death_data = response.json()
            death_id = death_data.get("death_id")
            final_merit = death_data.get("final_merit_score")
            next_loka = death_data.get("loka_assignment")
            
            print(f"✅ Death event recorded: {death_id}")
            print(f"Final merit score: {final_merit}")
            print(f"Next loka assignment: {next_loka}")
            
            demo_results["steps"]["death"] = {
                "status": "success",
                "death_id": death_id,
                "final_merit_score": final_merit,
                "loka_assignment": next_loka
            }
        else:
            print(f"❌ Death event failed: {response.text}")
            demo_results["steps"]["death"] = {"status": "failed", "error": response.text}
        
        time.sleep(1)
        
        # Step 5: Get comprehensive user statistics
        print("\n📊 STEP 5: Final Statistics")
        print("-" * 50)
        
        stats_payload = {
            "event_type": "stats_request",
            "user_id": USER_ID,
            "data": {
                "include_history": True,
                "include_transactions": True,
                "include_appeals": True,
                "include_atonements": True
            }
        }
        
        response = requests.post(f"{BASE_URL}/event", json=stats_payload)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            stats_data = response.json()
            user_stats = stats_data.get("user_stats", {})
            
            print("Final Statistics:")
            print(f"  Merit Score: {user_stats.get('merit_score', 'N/A')}")
            print(f"  Dharma Points: {user_stats.get('dharma_points', 'N/A')}")
            print(f"  Seva Points: {user_stats.get('seva_points', 'N/A')}")
            print(f"  Punya Tokens: {user_stats.get('punya_tokens', 'N/A')}")
            print(f"  Paap Tokens: {user_stats.get('paap_tokens', 'N/A')}")
            print(f"  Total Transactions: {user_stats.get('total_transactions', 'N/A')}")
            print(f"  Appeals Filed: {user_stats.get('appeals_filed', 'N/A')}")
            print(f"  Atonements Completed: {user_stats.get('atonements_completed', 'N/A')}")
            
            demo_results["steps"]["stats"] = {
                "status": "success",
                "stats": user_stats
            }
        else:
            print(f"❌ Stats retrieval failed: {response.text}")
            demo_results["steps"]["stats"] = {"status": "failed", "error": response.text}
        
        # Calculate demo duration and finalize results
        end_time = datetime.now()
        duration = (end_time - datetime.fromisoformat(demo_results["start_time"])).total_seconds()
        
        demo_results["end_time"] = end_time.isoformat()
        demo_results["duration_seconds"] = duration
        
        # Determine overall success
        failed_steps = [step for step, data in demo_results["steps"].items() 
                       if data.get("status") == "failed"]
        demo_results["success"] = len(failed_steps) == 0
        
        print("\n" + "="*80)
        print("🎉 COMPREHENSIVE DEMO COMPLETED!")
        print("="*80)
        print(f"Duration: {duration:.2f} seconds")
        print(f"User ID: {USER_ID}")
        print(f"Overall Status: {'✅ SUCCESS' if demo_results['success'] else '❌ FAILED'}")
        
        if failed_steps:
            print(f"Failed Steps: {', '.join(failed_steps)}")
        
        # Save detailed results
        results_file = f"comprehensive_demo_results_{USER_ID}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(demo_results, f, indent=2)
        
        print(f"Detailed results saved to: {results_file}")
        print("="*80)
        
        return demo_results
        
    except Exception as e:
        print(f"\n❌ DEMO FAILED WITH EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        demo_results["error"] = str(e)
        demo_results["traceback"] = traceback.format_exc()
        return demo_results

if __name__ == "__main__":
    print("Starting KarmaChain integration demo...")
    
    # Run all test suites
    print("\n" + "="*80)
    print("🚀 RUNNING COMPLETE INTEGRATION TEST SUITE")
    print("="*80)
    
    test_results = {}
    
    # Test 1: Basic unified event flow
    print("\n" + "="*60)
    print("Test 1: Basic Unified Event Flow")
    print("="*60)
    unified_result = test_full_karma_flow()
    test_results["basic_unified_flow"] = unified_result
    
    # Test 2: Comprehensive karma workflow
    print("\n" + "="*60)
    print("Test 2: Comprehensive Karma Workflow")
    print("="*60)
    comprehensive_results = comprehensive_karma_workflow_demo()
    test_results["comprehensive_workflow"] = comprehensive_results["success"]
    
    # Test 3: File upload with atonement
    print("\n" + "="*60)
    print("Test 3: File Upload with Atonement")
    print("="*60)
    file_upload_result = test_file_upload_with_atonement()
    test_results["file_upload"] = file_upload_result
    
    # Test 4: All event types
    print("\n" + "="*60)
    print("Test 4: All Event Types")
    print("="*60)
    all_event_results = test_all_event_types()
    test_results["all_event_types"] = all_event_results
    
    # Summary
    print("\n" + "="*80)
    print("📋 FINAL INTEGRATION TEST SUMMARY")
    print("="*80)
    
    # Basic results
    print(f"Basic Unified Flow: {'✅ PASSED' if unified_result else '❌ FAILED'}")
    print(f"Comprehensive Workflow: {'✅ PASSED' if comprehensive_results['success'] else '❌ FAILED'}")
    print(f"File Upload: {'✅ PASSED' if file_upload_result else '❌ FAILED'}")
    
    # Event types summary
    successful_events = sum(1 for result in all_event_results.values() if result["success"])
    total_events = len(all_event_results)
    print(f"All Event Types: {'✅ PASSED' if successful_events == total_events else '❌ FAILED'} ({successful_events}/{total_events})")
    
    # Overall result
    all_passed = (
        unified_result and 
        comprehensive_results['success'] and 
        file_upload_result and 
        successful_events == total_events
    )
    
    if all_passed:
        print("\n🎉 ALL INTEGRATION TESTS COMPLETED SUCCESSFULLY!")
        print("✅ Unified Event Gateway is working correctly")
        print("✅ File Upload System is operational")
        print("✅ All event types are supported")
        print("✅ Complete karma workflow is functional")
        sys.exit(0)
    else:
        print("\n❌ SOME INTEGRATION TESTS FAILED!")
        print("Check the detailed output above for specific failures.")
        sys.exit(1)