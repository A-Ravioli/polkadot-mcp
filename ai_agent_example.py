#!/usr/bin/env python3
"""
Example AI Agent for Polkadot MCP
This script demonstrates how an AI agent can interact with the Polkadot MCP API
"""

import requests
import json
import time
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("PolkadotAgent")

class PolkadotAIAgent:
    """A simple AI agent that interacts with the Polkadot MCP API"""
    
    def __init__(self, api_url: str, api_key: str):
        """
        Initialize the AI agent
        
        Args:
            api_url: Base URL of the Polkadot MCP API
            api_key: API key for authentication
        """
        self.api_url = api_url.rstrip('/')
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key
        }
        self.my_address = None  # Will be set with the agent's address
    
    def check_health(self) -> Dict[str, Any]:
        """Check if the API is running and get basic network info"""
        response = requests.get(f"{self.api_url}/api/health", headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Health check failed: {response.text}")
            raise Exception("API health check failed")
    
    def get_balance(self, address: str) -> Dict[str, Any]:
        """
        Get the balance of an address
        
        Args:
            address: Ethereum address to check balance for
            
        Returns:
            Dict containing balance information
        """
        response = requests.get(
            f"{self.api_url}/api/balance/{address}", 
            headers=self.headers
        )
        
        if response.status_code == 200:
            balance_data = response.json()
            logger.info(f"Balance for {address}: {balance_data['formattedBalance']} {balance_data['unit']}")
            return balance_data
        else:
            logger.error(f"Failed to get balance: {response.text}")
            raise Exception(f"Failed to get balance: {response.text}")
    
    def deposit(self, target_address: str, amount: float) -> Dict[str, Any]:
        """
        Deposit tokens to an address
        
        Args:
            target_address: Address to deposit tokens to
            amount: Amount of tokens to deposit
            
        Returns:
            Dict containing transaction information
        """
        payload = {
            "address": target_address,
            "amount": str(amount)
        }
        
        response = requests.post(
            f"{self.api_url}/api/deposit",
            headers=self.headers,
            json=payload
        )
        
        if response.status_code == 200:
            tx_data = response.json()
            logger.info(f"Deposited {amount} to {target_address}. TX: {tx_data['transaction']}")
            return tx_data
        else:
            logger.error(f"Deposit failed: {response.text}")
            raise Exception(f"Deposit failed: {response.text}")
    
    def withdraw(self, from_address: str, amount: float) -> Dict[str, Any]:
        """
        Withdraw tokens from an address
        
        Args:
            from_address: Address to withdraw tokens from
            amount: Amount of tokens to withdraw
            
        Returns:
            Dict containing transaction information
        """
        payload = {
            "address": from_address,
            "amount": str(amount)
        }
        
        response = requests.post(
            f"{self.api_url}/api/withdraw",
            headers=self.headers,
            json=payload
        )
        
        if response.status_code == 200:
            tx_data = response.json()
            logger.info(f"Withdrew {amount} from {from_address}. TX: {tx_data['transaction']}")
            return tx_data
        else:
            logger.error(f"Withdrawal failed: {response.text}")
            raise Exception(f"Withdrawal failed: {response.text}")
    
    def is_agent_authorized(self, agent_address: str) -> bool:
        """
        Check if an agent is authorized
        
        Args:
            agent_address: Address to check authorization for
            
        Returns:
            True if authorized, False otherwise
        """
        response = requests.get(
            f"{self.api_url}/api/agent/{agent_address}", 
            headers=self.headers
        )
        
        if response.status_code == 200:
            agent_data = response.json()
            logger.info(f"Agent {agent_address} authorized: {agent_data['isAuthorized']}")
            return agent_data["isAuthorized"]
        else:
            logger.error(f"Failed to check agent authorization: {response.text}")
            raise Exception(f"Failed to check agent authorization: {response.text}")
    
    def get_network_info(self) -> Dict[str, Any]:
        """Get information about the blockchain network"""
        response = requests.get(f"{self.api_url}/api/network", headers=self.headers)
        if response.status_code == 200:
            network_data = response.json()
            logger.info(f"Connected to network: {network_data['name']} (Chain ID: {network_data['chainId']})")
            return network_data
        else:
            logger.error(f"Failed to get network info: {response.text}")
            raise Exception(f"Failed to get network info: {response.text}")

    def run_wallet_management_task(self, user_address: str, action: str, amount: Optional[float] = None) -> Dict[str, Any]:
        """
        Execute a wallet management task based on the specified action
        
        Args:
            user_address: The address to perform the action on
            action: The action to perform (check_balance, deposit, withdraw)
            amount: The amount for deposit or withdraw actions
            
        Returns:
            Dict containing the result of the operation
        """
        if action == "check_balance":
            return self.get_balance(user_address)
        elif action == "deposit" and amount is not None:
            return self.deposit(user_address, amount)
        elif action == "withdraw" and amount is not None:
            return self.withdraw(user_address, amount)
        else:
            raise ValueError(f"Invalid action: {action} or missing amount for deposit/withdraw")


def main():
    """Simple demonstration of AI agent interacting with the MCP"""
    
    # Configuration (in a real agent, these would be securely stored or passed as environment variables)
    API_URL = "http://localhost:3000"
    API_KEY = "your-api-key"
    
    # Example addresses (replace with real addresses in actual usage)
    AGENT_ADDRESS = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
    USER_ADDRESS = "0x123456789012345678901234567890123456789A"
    
    # Initialize the agent
    agent = PolkadotAIAgent(API_URL, API_KEY)
    
    # Check if API is up and running
    try:
        health_info = agent.check_health()
        logger.info(f"API is healthy. Connected to: {health_info['network']}")
        
        # Get network information
        network_info = agent.get_network_info()
        logger.info(f"Current block number: {network_info['blockNumber']}")
        logger.info(f"Current gas price: {network_info['formattedGasPrice']}")
        
        # Check if agent is authorized
        is_authorized = agent.is_agent_authorized(AGENT_ADDRESS)
        logger.info(f"Agent authorization status: {is_authorized}")
        
        # Example workflow: Check balance -> Deposit -> Check balance -> Withdraw -> Check balance
        logger.info("Starting wallet management workflow:")
        
        # 1. Check initial balance
        initial_balance = agent.run_wallet_management_task(USER_ADDRESS, "check_balance")
        
        # 2. Deposit some tokens
        if float(initial_balance["formattedBalance"]) < 0.2:
            logger.info("Depositing 0.1 tokens...")
            deposit_result = agent.run_wallet_management_task(USER_ADDRESS, "deposit", 0.1)
            
            # Wait for transaction to be processed
            logger.info("Waiting for transaction confirmation...")
            time.sleep(5)
        
        # 3. Check updated balance
        updated_balance = agent.run_wallet_management_task(USER_ADDRESS, "check_balance")
        
        # 4. Withdraw some tokens if enough balance and agent is authorized
        if is_authorized and float(updated_balance["formattedBalance"]) >= 0.05:
            logger.info("Withdrawing 0.05 tokens...")
            withdraw_result = agent.run_wallet_management_task(USER_ADDRESS, "withdraw", 0.05)
            
            # Wait for transaction to be processed
            logger.info("Waiting for transaction confirmation...")
            time.sleep(5)
            
            # 5. Check final balance
            final_balance = agent.run_wallet_management_task(USER_ADDRESS, "check_balance")
        
    except Exception as e:
        logger.error(f"Error in AI agent operation: {str(e)}")


if __name__ == "__main__":
    main() 