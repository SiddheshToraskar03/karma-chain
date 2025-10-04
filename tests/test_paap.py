import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import paap, atonement
from routes import actions
from config import PAAP_CLASSES, PRAYASCHITTA_MAP

class TestPaapIssuance(unittest.TestCase):
    def setUp(self):
        # Mock database and collections
        self.db_mock = MagicMock()
        self.users_mock = MagicMock()
        self.transactions_mock = MagicMock()
        
        # Set up mock returns
        self.db_mock.users = self.users_mock
        self.db_mock.transactions = self.transactions_mock
        
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

    def test_classify_paap_action(self):
        # Test minor paap classification
        action = "false_speech"
        result = paap.classify_paap_action(action)
        self.assertEqual(result, "minor")
        
        # Test medium paap classification
        action = "cheat"
        result = paap.classify_paap_action(action)
        self.assertEqual(result, "medium")
        
        # Test maha paap classification
        action = "harm_others"
        result = paap.classify_paap_action(action)
        self.assertEqual(result, "maha")
        
        # Test unknown action
        action = "unknown_action"
        result = paap.classify_paap_action(action)
        self.assertEqual(result, None)

    def test_calculate_paap_value(self):
        # Test minor paap value
        severity = "minor"
        result = paap.calculate_paap_value(severity)
        self.assertEqual(result, 1)
        
        # Test medium paap value
        severity = "medium"
        result = paap.calculate_paap_value(severity)
        self.assertEqual(result, 3)
        
        # Test maha paap value
        severity = "maha"
        result = paap.calculate_paap_value(severity)
        self.assertEqual(result, 7)
        
        # Test invalid severity
        severity = "invalid"
        with self.assertRaises(ValueError):
            paap.calculate_paap_value(severity)

    @patch('database.get_db')
    def test_apply_paap_tokens(self, mock_get_db):
        # Setup
        mock_get_db.return_value = self.db_mock
        
        # Test applying minor paap tokens
        severity = "minor"
        result = paap.apply_paap_tokens(self.user_id, severity)
        
        # Assertions
        self.users_mock.update_one.assert_called_once()
        self.assertEqual(result["minor"], 6)  # 5 + 1
        self.assertEqual(result["medium"], 3)
        self.assertEqual(result["maha"], 1)
        
        # Reset mock
        self.users_mock.update_one.reset_mock()
        
        # Test applying medium paap tokens
        severity = "medium"
        result = paap.apply_paap_tokens(self.user_id, severity)
        
        # Assertions
        self.users_mock.update_one.assert_called_once()
        self.assertEqual(result["minor"], 5)
        self.assertEqual(result["medium"], 6)  # 3 + 3
        self.assertEqual(result["maha"], 1)
        
        # Reset mock
        self.users_mock.update_one.reset_mock()
        
        # Test applying maha paap tokens
        severity = "maha"
        result = paap.apply_paap_tokens(self.user_id, severity)
        
        # Assertions
        self.users_mock.update_one.assert_called_once()
        self.assertEqual(result["minor"], 5)
        self.assertEqual(result["medium"], 3)
        self.assertEqual(result["maha"], 8)  # 1 + 7

    @patch('database.get_db')
    def test_reduce_paap_tokens(self, mock_get_db):
        # Setup
        mock_get_db.return_value = self.db_mock
        
        # Test reducing medium paap tokens
        severity = "medium"
        result = paap.reduce_paap_tokens(self.user_id, severity)
        
        # Assertions
        self.users_mock.update_one.assert_called_once()
        self.assertEqual(result["minor"], 5)
        self.assertEqual(result["medium"], 2)  # 3 - 1
        self.assertEqual(result["maha"], 1)

    @patch('database.get_db')
    def test_calculate_total_paap_score(self, mock_get_db):
        # Setup
        mock_get_db.return_value = self.db_mock
        
        # Test calculating total paap score
        result = paap.calculate_total_paap_score(self.user_id)
        
        # Expected: (5*1) + (3*3) + (1*7) = 5 + 9 + 7 = 21
        self.assertEqual(result, 21)


class TestAtonementProcess(unittest.TestCase):
    def setUp(self):
        # Mock database and collections
        self.db_mock = MagicMock()
        self.users_mock = MagicMock()
        self.atonements_mock = MagicMock()
        
        # Set up mock returns
        self.db_mock.users = self.users_mock
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
        
        # Sample atonement plan
        self.atonement_plan_id = "atonement123"
        self.atonement_plan = {
            "_id": self.atonement_plan_id,
            "user_id": self.user_id,
            "appeal_id": "appeal123",
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
        
        # Mock atonement plan retrieval
        self.atonements_mock.find_one.return_value = self.atonement_plan

    def test_get_atonement_requirements(self):
        # Test getting atonement requirements for minor paap
        severity = "minor"
        result = atonement.get_atonement_requirements(severity)
        self.assertEqual(result, PRAYASCHITTA_MAP[severity])
        
        # Test getting atonement requirements for medium paap
        severity = "medium"
        result = atonement.get_atonement_requirements(severity)
        self.assertEqual(result, PRAYASCHITTA_MAP[severity])
        
        # Test getting atonement requirements for maha paap
        severity = "maha"
        result = atonement.get_atonement_requirements(severity)
        self.assertEqual(result, PRAYASCHITTA_MAP[severity])
        
        # Test invalid severity
        severity = "invalid"
        with self.assertRaises(ValueError):
            atonement.get_atonement_requirements(severity)

    @patch('database.get_db')
    def test_create_atonement_plan(self, mock_get_db):
        # Setup
        mock_get_db.return_value = self.db_mock
        self.atonements_mock.insert_one.return_value = MagicMock(inserted_id=self.atonement_plan_id)
        
        # Test creating atonement plan
        appeal_id = "appeal123"
        severity = "medium"
        result = atonement.create_atonement_plan(self.user_id, appeal_id, severity)
        
        # Assertions
        self.atonements_mock.insert_one.assert_called_once()
        self.assertEqual(result, self.atonement_plan_id)

    @patch('database.get_db')
    def test_validate_atonement_proof(self, mock_get_db):
        # Setup
        mock_get_db.return_value = self.db_mock
        
        # Test validating Jap proof
        atonement_type = "Jap"
        proof = "Completed 108 mantras"
        units = 108
        result = atonement.validate_atonement_proof(atonement_type, proof, units)
        self.assertTrue(result)
        
        # Test validating Tap proof
        atonement_type = "Tap"
        proof = "Fasted for 3 days"
        units = 3
        result = atonement.validate_atonement_proof(atonement_type, proof, units)
        self.assertTrue(result)
        
        # Test validating with invalid units
        atonement_type = "Jap"
        proof = "Completed 108 mantras"
        units = -1
        result = atonement.validate_atonement_proof(atonement_type, proof, units)
        self.assertFalse(result)

    @patch('database.get_db')
    def test_update_atonement_progress(self, mock_get_db):
        # Setup
        mock_get_db.return_value = self.db_mock
        
        # Test updating atonement progress
        atonement_type = "Jap"
        units = 50
        result = atonement.update_atonement_progress(self.atonement_plan_id, atonement_type, units)
        
        # Assertions
        self.atonements_mock.update_one.assert_called_once()
        self.assertEqual(result["progress"]["Jap"], 50)
        self.assertEqual(result["progress"]["Tap"], 0)
        self.assertEqual(result["progress"]["Bhakti"], 0)
        self.assertEqual(result["progress"]["Daan"], 0)

    @patch('database.get_db')
    def test_check_atonement_completion(self, mock_get_db):
        # Setup
        mock_get_db.return_value = self.db_mock
        
        # Test with incomplete atonement
        result = atonement.check_atonement_completion(self.atonement_plan_id)
        self.assertFalse(result)
        
        # Update atonement plan to be complete
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
        
        # Test with complete atonement
        result = atonement.check_atonement_completion(self.atonement_plan_id)
        self.assertTrue(result)


class TestActionsWithPaap(unittest.TestCase):
    def setUp(self):
        # Mock database and collections
        self.db_mock = MagicMock()
        self.users_mock = MagicMock()
        self.transactions_mock = MagicMock()
        self.appeals_mock = MagicMock()
        
        # Set up mock returns
        self.db_mock.users = self.users_mock
        self.db_mock.transactions = self.transactions_mock
        self.db_mock.appeals = self.appeals_mock
        
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

    @patch('database.get_db')
    @patch('utils.paap.classify_paap_action')
    @patch('utils.paap.apply_paap_tokens')
    @patch('utils.atonement.create_atonement_plan')
    def test_log_paap_action(self, mock_create_plan, mock_apply_paap, mock_classify_paap, mock_get_db):
        # Setup
        mock_get_db.return_value = self.db_mock
        mock_classify_paap.return_value = "medium"
        mock_apply_paap.return_value = {
            "minor": 5,
            "medium": 6,  # Increased by 3
            "maha": 1
        }
        mock_create_plan.return_value = "atonement123"
        
        # Test logging a paap action without auto appeal
        request_data = {
            "user_id": self.user_id,
            "action": "disrespect_guru",
            "note": "Disrespected teacher"
        }
        
        # Mock the original log_action function to avoid testing its implementation
        with patch('routes.actions.log_action_original', return_value={"status": "success"}):
            result = actions.log_action(request_data)
            
            # Assertions
            mock_classify_paap.assert_called_once_with("disrespect_guru")
            mock_apply_paap.assert_called_once_with(self.user_id, "medium")
            mock_create_plan.assert_not_called()
            self.assertEqual(result["paap_severity"], "medium")
            self.assertEqual(result["paap_tokens"]["medium"], 6)
            
        # Reset mocks
        mock_classify_paap.reset_mock()
        mock_apply_paap.reset_mock()
        mock_create_plan.reset_mock()
        
        # Test logging a paap action with auto appeal
        request_data = {
            "user_id": self.user_id,
            "action": "disrespect_guru",
            "note": "Disrespected teacher, auto_appeal"
        }
        
        # Mock the original log_action function
        with patch('routes.actions.log_action_original', return_value={"status": "success"}):
            result = actions.log_action(request_data)
            
            # Assertions
            mock_classify_paap.assert_called_once_with("disrespect_guru")
            mock_apply_paap.assert_called_once_with(self.user_id, "medium")
            mock_create_plan.assert_called_once()
            self.assertEqual(result["paap_severity"], "medium")
            self.assertEqual(result["paap_tokens"]["medium"], 6)
            self.assertEqual(result["atonement_plan_id"], "atonement123")


if __name__ == '__main__':
    unittest.main()