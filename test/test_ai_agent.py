#!/usr/bin/env python3
"""
Unit tests for the Polkadot AI Agent
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Add parent directory to path to import ai_agent_example
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai_agent_example import PolkadotAIAgent

class TestPolkadotAIAgent(unittest.TestCase):
    """Test cases for PolkadotAIAgent class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.api_url = "http://localhost:3000"
        self.api_key = "test-api-key"
        self.agent = PolkadotAIAgent(self.api_url, self.api_key)
        self.test_address = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
    
    @patch('requests.get')
    def test_check_health(self, mock_get):
        """Test health check endpoint"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "ok",
            "network": "moonbase-alpha",
            "contractAddress": "0x1234567890123456789012345678901234567890"
        }
        mock_get.return_value = mock_response
        
        # Call method
        result = self.agent.check_health()
        
        # Verify
        mock_get.assert_called_once_with(
            "http://localhost:3000/api/health",
            headers=self.agent.headers
        )
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["network"], "moonbase-alpha")
    
    @patch('requests.get')
    def test_check_health_error(self, mock_get):
        """Test health check endpoint with error response"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response
        
        # Call method and verify it raises exception
        with self.assertRaises(Exception):
            self.agent.check_health()
    
    @patch('requests.get')
    def test_get_balance(self, mock_get):
        """Test get balance endpoint"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "address": self.test_address,
            "balance": "1000000000000000000",
            "formattedBalance": "1.0",
            "unit": "ETH"
        }
        mock_get.return_value = mock_response
        
        # Call method
        result = self.agent.get_balance(self.test_address)
        
        # Verify
        mock_get.assert_called_once_with(
            f"http://localhost:3000/api/balance/{self.test_address}",
            headers=self.agent.headers
        )
        self.assertEqual(result["address"], self.test_address)
        self.assertEqual(result["formattedBalance"], "1.0")
    
    @patch('requests.post')
    def test_deposit(self, mock_post):
        """Test deposit endpoint"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "transaction": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
            "blockNumber": 12345,
            "gasUsed": "21000",
            "address": self.test_address,
            "amount": "0.1"
        }
        mock_post.return_value = mock_response
        
        # Call method
        result = self.agent.deposit(self.test_address, 0.1)
        
        # Verify
        mock_post.assert_called_once_with(
            "http://localhost:3000/api/deposit",
            headers=self.agent.headers,
            json={"address": self.test_address, "amount": "0.1"}
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["address"], self.test_address)
        self.assertEqual(result["amount"], "0.1")
    
    @patch('requests.post')
    def test_withdraw(self, mock_post):
        """Test withdraw endpoint"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "transaction": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
            "blockNumber": 12345,
            "gasUsed": "21000",
            "address": self.test_address,
            "amount": "0.05"
        }
        mock_post.return_value = mock_response
        
        # Call method
        result = self.agent.withdraw(self.test_address, 0.05)
        
        # Verify
        mock_post.assert_called_once_with(
            "http://localhost:3000/api/withdraw",
            headers=self.agent.headers,
            json={"address": self.test_address, "amount": "0.05"}
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["address"], self.test_address)
        self.assertEqual(result["amount"], "0.05")
    
    @patch('requests.get')
    def test_is_agent_authorized(self, mock_get):
        """Test agent authorization endpoint"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "address": self.test_address,
            "isAuthorized": True
        }
        mock_get.return_value = mock_response
        
        # Call method
        result = self.agent.is_agent_authorized(self.test_address)
        
        # Verify
        mock_get.assert_called_once_with(
            f"http://localhost:3000/api/agent/{self.test_address}",
            headers=self.agent.headers
        )
        self.assertTrue(result)
    
    @patch('requests.get')
    def test_get_network_info(self, mock_get):
        """Test network info endpoint"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "chainId": 1287,
            "name": "moonbase-alpha",
            "blockNumber": 12345,
            "gasPrice": "1000000000",
            "formattedGasPrice": "1 gwei"
        }
        mock_get.return_value = mock_response
        
        # Call method
        result = self.agent.get_network_info()
        
        # Verify
        mock_get.assert_called_once_with(
            "http://localhost:3000/api/network",
            headers=self.agent.headers
        )
        self.assertEqual(result["chainId"], 1287)
        self.assertEqual(result["name"], "moonbase-alpha")
    
    @patch('ai_agent_example.PolkadotAIAgent.get_balance')
    def test_run_wallet_management_task_check_balance(self, mock_get_balance):
        """Test run_wallet_management_task with check_balance action"""
        # Setup mock
        mock_get_balance.return_value = {
            "address": self.test_address,
            "balance": "1000000000000000000",
            "formattedBalance": "1.0",
            "unit": "ETH"
        }
        
        # Call method
        result = self.agent.run_wallet_management_task(self.test_address, "check_balance")
        
        # Verify
        mock_get_balance.assert_called_once_with(self.test_address)
        self.assertEqual(result["formattedBalance"], "1.0")
    
    @patch('ai_agent_example.PolkadotAIAgent.deposit')
    def test_run_wallet_management_task_deposit(self, mock_deposit):
        """Test run_wallet_management_task with deposit action"""
        # Setup mock
        mock_deposit.return_value = {
            "success": True,
            "transaction": "0x1234",
            "address": self.test_address,
            "amount": "0.1"
        }
        
        # Call method
        result = self.agent.run_wallet_management_task(self.test_address, "deposit", 0.1)
        
        # Verify
        mock_deposit.assert_called_once_with(self.test_address, 0.1)
        self.assertTrue(result["success"])
    
    @patch('ai_agent_example.PolkadotAIAgent.withdraw')
    def test_run_wallet_management_task_withdraw(self, mock_withdraw):
        """Test run_wallet_management_task with withdraw action"""
        # Setup mock
        mock_withdraw.return_value = {
            "success": True,
            "transaction": "0x1234",
            "address": self.test_address,
            "amount": "0.05"
        }
        
        # Call method
        result = self.agent.run_wallet_management_task(self.test_address, "withdraw", 0.05)
        
        # Verify
        mock_withdraw.assert_called_once_with(self.test_address, 0.05)
        self.assertTrue(result["success"])
    
    def test_run_wallet_management_task_invalid_action(self):
        """Test run_wallet_management_task with invalid action"""
        # Call method and verify it raises exception
        with self.assertRaises(ValueError):
            self.agent.run_wallet_management_task(self.test_address, "invalid_action")
    
    def test_run_wallet_management_task_missing_amount(self):
        """Test run_wallet_management_task with missing amount"""
        # Call method and verify it raises exception
        with self.assertRaises(ValueError):
            self.agent.run_wallet_management_task(self.test_address, "deposit") # Missing amount


if __name__ == '__main__':
    unittest.main() 