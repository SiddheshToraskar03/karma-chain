import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json
from bson.objectid import ObjectId

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routes import appeal
from utils import atonement, paap

class TestAppealLifecycle(unittest.TestCase):
    def setUp(self):
        # Mock database and collections
        self.db_mock = MagicMock()
        self.users_mock = MagicMock()
        self.appeals_mock = MagicMock()
        self.atonements_mock = MagicMock()
        
        # Set up mock returns
        self.db_mock.users = self.users_mock
        self.db_mock.appeals = self.appeals_mock
        self.db_mock.atonements = self.atonements_mock
        
        # Sample user data
        self.user_id = "user123"
        self.user_data = {
            "_id": self.user_id,
            "name": "Test User",
            "balances": {
                "DharmaPoints": 100,
                "SevaPoints": 50,
                "PunyaTokens": {"minor": 10, "medium": 5, "major": 2},
                "PaapTokens": {"minor": 5, "medium": 3, "maha": 1}
            },
            "role": "learner"
        }
        
        # Mock user retrieval
        self.users_mock.find_one.return_value = self.user_data
        
        # Sample appeal data
        self.appeal_id = str(ObjectId())
        self.appeal_data = {
            "_id": self.appeal_id,
            "user_id": self.user_id,
            "action": "disrespect_guru",
            "paap_class": "medium",
            "status": "pending",
            "created_at": "2023-01-01T00:00:00",
            "atonement_plan_id": None
        }
        
        # Sample atonement plan
        self.atonement_plan_id = str(ObjectId())
        self.atonement_plan = {
            "_id": self.atonement_plan_id,
            "user_id": self.user_id,
            "appeal_id": self.appeal_id,
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
            "created_at": "2023-01-01T00:00:00",
            "completed_at": None
        }

    @patch('database.get_db')
    def test_appeal_karma_creates_plan(self, mock_get_db):
        # Setup
        mock_get_db.return_value = self.db_mock
        self.appeals_mock.insert_one.return_value = MagicMock(inserted_id=self.appeal_id)
        
        # Mock atonement.create_atonement_plan
        with patch('utils.atonement.create_atonement_plan') as mock_create_plan:
            mock_create_plan.return_value = self.atonement_plan_id
            
            # Test appeal_karma endpoint
            request_data = {
                "user_id": self.user_id,
                "action": "disrespect_guru",
                "note": "I disrespected my teacher"
            }
            
            result = appeal.appeal_karma(request_data)
            
            # Assertions
            self.appeals_mock.insert_one.assert_called_once()
            mock_create_plan.assert_called_once()
            self.assertEqual(result["atonement_plan_id"], self.atonement_plan_id)
            self.assertEqual(result["status"], "pending")

    @patch('database.get_db')
    def test_submit_atonement_updates_progress(self, mock_get_db):
        # Setup
        mock_get_db.return_value = self.db_mock
        self.atonements_mock.find_one.return_value = self.atonement_plan
        
        # Mock atonement.validate_atonement_proof
        with patch('utils.atonement.validate_atonement_proof') as mock_validate:
            mock_validate.return_value = True
            
            # Mock atonement.update_atonement_progress
            with patch('utils.atonement.update_atonement_progress') as mock_update:
                mock_update.return_value = {
                    **self.atonement_plan,
                    "progress": {"Jap": 108, "Tap": 0, "Bhakti": 0, "Daan": 0}
                }
                
                # Test submit_atonement endpoint
                request_data = {
                    "user_id": self.user_id,
                    "atonement_plan_id": self.atonement_plan_id,
                    "atonement_type": "Jap",
                    "proof": "Completed 108 mantras",
                    "units": 108
                }
                
                result = appeal.submit_atonement(request_data)
                
                # Assertions
                mock_validate.assert_called_once()
                mock_update.assert_called_once()
                self.assertEqual(result["progress"]["Jap"], 108)

    @patch('database.get_db')
    def test_complete_atonement_reduces_paap(self, mock_get_db):
        # Setup
        mock_get_db.return_value = self.db_mock
        
        # Updated atonement plan with all requirements met
        completed_plan = {
            **self.atonement_plan,
            "progress": {
                "Jap": 108,
                "Tap": 3,
                "Bhakti": 1,
                "Daan": 0.05
            }
        }
        self.atonements_mock.find_one.return_value = completed_plan
        
        # Mock atonement.check_atonement_completion
        with patch('utils.atonement.check_atonement_completion') as mock_check:
            mock_check.return_value = True
            
            # Mock atonement.mark_atonement_completed
            with patch('utils.atonement.mark_atonement_completed') as mock_mark:
                # Mock paap.reduce_paap_tokens
                with patch('utils.paap.reduce_paap_tokens') as mock_reduce:
                    mock_reduce.return_value = {
                        "minor": 5,
                        "medium": 2,  # Reduced by 1
                        "maha": 1
                    }
                    
                    # Test submit_atonement with completion
                    request_data = {
                        "user_id": self.user_id,
                        "atonement_plan_id": self.atonement_plan_id,
                        "atonement_type": "Daan",
                        "proof": "Donation transaction hash: 0x123456",
                        "units": 0.05
                    }
                    
                    result = appeal.submit_atonement(request_data)
                    
                    # Assertions
                    mock_check.assert_called_once()
                    mock_mark.assert_called_once()
                    mock_reduce.assert_called_once()
                    self.assertEqual(result["status"], "completed")

    @patch('database.get_db')
    def test_appeal_status_returns_correct_data(self, mock_get_db):
        # Setup
        mock_get_db.return_value = self.db_mock
        
        # Mock appeals and atonements for this user
        self.appeals_mock.find.return_value = [self.appeal_data]
        self.atonements_mock.find.return_value = [self.atonement_plan]
        
        # Test appeal_status endpoint
        result = appeal.appeal_status(self.user_id)
        
        # Assertions
        self.appeals_mock.find.assert_called_once_with({"user_id": self.user_id})
        self.atonements_mock.find.assert_called_once()
        self.assertEqual(len(result["appeals"]), 1)
        self.assertEqual(len(result["atonement_plans"]), 1)
        self.assertEqual(result["appeals"][0]["_id"], self.appeal_id)
        self.assertEqual(result["atonement_plans"][0]["_id"], self.atonement_plan_id)

    @patch('database.get_db')
    def test_death_event_assigns_correct_loka(self, mock_get_db):
        # Setup
        mock_get_db.return_value = self.db_mock
        
        # Mock loka.calculate_net_karma
        with patch('utils.loka.calculate_net_karma') as mock_calc:
            mock_calc.return_value = 75  # Positive karma
            
            # Mock loka.assign_loka
            with patch('utils.loka.assign_loka') as mock_assign:
                mock_assign.return_value = "Swarga"
                
                # Mock loka.create_rebirth_carryover
                with patch('utils.loka.create_rebirth_carryover') as mock_carryover:
                    mock_carryover.return_value = {
                        "carryover_paap": 1,
                        "carryover_punya": 5,
                        "starting_level": "volunteer"
                    }
                    
                    # Test death_event endpoint
                    request_data = {"user_id": self.user_id}
                    result = appeal.death_event(request_data)
                    
                    # Assertions
                    mock_calc.assert_called_once()
                    mock_assign.assert_called_once()
                    mock_carryover.assert_called_once()
                    self.assertEqual(result["assigned_loka"], "Swarga")
                    self.assertEqual(result["carryover"]["starting_level"], "volunteer")


if __name__ == '__main__':
    unittest.main()