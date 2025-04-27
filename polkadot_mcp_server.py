#!/usr/bin/env python3
"""
Polkadot Model Context Protocol (MCP) Server
This implements an MCP server that exposes Polkadot wallet functionality to LLMs
"""

import json
import sys
import os
import asyncio
import logging
import argparse
import requests
from typing import Dict, Any, List, Optional, Union
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("PolkadotMCPServer")

class PolkadotMCPServer:
    """
    MCP server implementation for Polkadot wallet functionality
    """
    
    def __init__(self, api_url: str, api_key: str):
        """
        Initialize the MCP server
        
        Args:
            api_url: Base URL of the Polkadot API
            api_key: API key for authentication
        """
        self.api_url = api_url.rstrip('/')
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key
        }
        
        # Define MCP tool schemas
        self.tools = [
            {
                "name": "check_balance",
                "description": "Get the balance of a wallet address",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "address": {
                            "type": "string",
                            "description": "The wallet address to check balance for"
                        }
                    },
                    "required": ["address"]
                }
            },
            {
                "name": "deposit",
                "description": "Deposit tokens to a wallet address",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "address": {
                            "type": "string",
                            "description": "The wallet address to deposit tokens to"
                        },
                        "amount": {
                            "type": "string",
                            "description": "The amount of tokens to deposit"
                        }
                    },
                    "required": ["address", "amount"]
                }
            },
            {
                "name": "withdraw",
                "description": "Withdraw tokens from a wallet address",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "address": {
                            "type": "string",
                            "description": "The wallet address to withdraw tokens from"
                        },
                        "amount": {
                            "type": "string",
                            "description": "The amount of tokens to withdraw"
                        }
                    },
                    "required": ["address", "amount"]
                }
            },
            {
                "name": "get_network_info",
                "description": "Get information about the current blockchain network",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "check_agent_authorization",
                "description": "Check if an agent address is authorized",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "agent_address": {
                            "type": "string",
                            "description": "The agent address to check authorization for"
                        }
                    },
                    "required": ["agent_address"]
                }
            }
        ]
        
        # Define MCP resources
        self.resources = []
        
        # Define MCP prompts
        self.prompts = [
            {
                "name": "wallet_management",
                "content": """You are a wallet management assistant for Polkadot.
You can help users check their balance, deposit tokens, and withdraw tokens.
Please use the available tools to assist users with their wallet needs."""
            }
        ]
    
    async def check_balance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get the balance of a wallet address
        
        Args:
            params: The parameters containing the address
            
        Returns:
            Dict containing balance information
        """
        address = params.get("address")
        if not address:
            return {"error": "Address is required"}
        
        try:
            response = requests.get(
                f"{self.api_url}/api/balance/{address}", 
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get balance: {response.text}")
                return {"error": f"Failed to get balance: {response.text}"}
        except Exception as e:
            logger.error(f"Error checking balance: {str(e)}")
            return {"error": str(e)}
    
    async def deposit(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deposit tokens to a wallet address
        
        Args:
            params: The parameters containing the address and amount
            
        Returns:
            Dict containing transaction information
        """
        address = params.get("address")
        amount = params.get("amount")
        
        if not address or not amount:
            return {"error": "Address and amount are required"}
        
        try:
            payload = {
                "address": address,
                "amount": amount
            }
            
            response = requests.post(
                f"{self.api_url}/api/deposit",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Deposit failed: {response.text}")
                return {"error": f"Deposit failed: {response.text}"}
        except Exception as e:
            logger.error(f"Error during deposit: {str(e)}")
            return {"error": str(e)}
    
    async def withdraw(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Withdraw tokens from a wallet address
        
        Args:
            params: The parameters containing the address and amount
            
        Returns:
            Dict containing transaction information
        """
        address = params.get("address")
        amount = params.get("amount")
        
        if not address or not amount:
            return {"error": "Address and amount are required"}
        
        try:
            payload = {
                "address": address,
                "amount": amount
            }
            
            response = requests.post(
                f"{self.api_url}/api/withdraw",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Withdrawal failed: {response.text}")
                return {"error": f"Withdrawal failed: {response.text}"}
        except Exception as e:
            logger.error(f"Error during withdrawal: {str(e)}")
            return {"error": str(e)}
    
    async def get_network_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get information about the blockchain network
        
        Args:
            params: Empty parameters (not used)
            
        Returns:
            Dict containing network information
        """
        try:
            response = requests.get(
                f"{self.api_url}/api/network", 
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get network info: {response.text}")
                return {"error": f"Failed to get network info: {response.text}"}
        except Exception as e:
            logger.error(f"Error getting network info: {str(e)}")
            return {"error": str(e)}
    
    async def check_agent_authorization(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if an agent is authorized
        
        Args:
            params: The parameters containing the agent_address
            
        Returns:
            Dict containing authorization information
        """
        agent_address = params.get("agent_address")
        if not agent_address:
            return {"error": "Agent address is required"}
        
        try:
            response = requests.get(
                f"{self.api_url}/api/agent/{agent_address}", 
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to check agent authorization: {response.text}")
                return {"error": f"Failed to check agent authorization: {response.text}"}
        except Exception as e:
            logger.error(f"Error checking agent authorization: {str(e)}")
            return {"error": str(e)}
    
    async def process_mcp_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an incoming MCP message
        
        Args:
            message: The MCP message
            
        Returns:
            Dict containing the response
        """
        method = message.get("method")
        params = message.get("params", {})
        request_id = message.get("id")
        
        if method == "mcp.discover":
            # Return discovery information
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": self.tools,
                    "resources": self.resources,
                    "prompts": self.prompts
                }
            }
        elif method == "mcp.invoke":
            # Invoke a tool
            tool_name = params.get("name")
            tool_params = params.get("parameters", {})
            
            # Map tool name to method
            tool_methods = {
                "check_balance": self.check_balance,
                "deposit": self.deposit,
                "withdraw": self.withdraw,
                "get_network_info": self.get_network_info,
                "check_agent_authorization": self.check_agent_authorization
            }
            
            if tool_name in tool_methods:
                result = await tool_methods[tool_name](tool_params)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result
                }
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method {tool_name} not found"
                    }
                }
        else:
            # Unknown method
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method {method} not found"
                }
            }

async def run_stdio_server(server: PolkadotMCPServer):
    """
    Run the MCP server using stdio communication
    
    Args:
        server: The PolkadotMCPServer instance
    """
    logger.info("Starting Polkadot MCP Server (stdio mode)")
    
    while True:
        try:
            # Read a message from stdin
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
            
            # Parse the JSON message
            message = json.loads(line)
            
            # Process the message
            response = await server.process_mcp_message(message)
            
            # Write the response to stdout
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
            
        except json.JSONDecodeError:
            logger.error("Invalid JSON received")
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": "Parse error"
                }
            }
            sys.stdout.write(json.dumps(error_response) + "\n")
            sys.stdout.flush()
        
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
            sys.stdout.write(json.dumps(error_response) + "\n")
            sys.stdout.flush()

async def main():
    """Initialize and run the MCP server"""
    parser = argparse.ArgumentParser(description="Polkadot MCP Server")
    parser.add_argument("--api-url", default=os.getenv("API_URL", "http://localhost:3000"), help="API URL for the Polkadot server")
    parser.add_argument("--api-key", default=os.getenv("API_KEY", "your-api-key"), help="API key for authentication")
    parser.add_argument("--mode", choices=["stdio", "http"], default=os.getenv("MCP_MODE", "stdio"), help="Communication mode (stdio or http)")
    parser.add_argument("--port", type=int, default=int(os.getenv("MCP_PORT", "3001")), help="HTTP server port (if mode is http)")
    
    args = parser.parse_args()
    
    server = PolkadotMCPServer(args.api_url, args.api_key)
    
    if args.mode == "stdio":
        await run_stdio_server(server)
    else:
        # Note: HTTP mode with SSE would be implemented here
        # For brevity, this implementation only includes stdio mode
        logger.error("HTTP mode not implemented in this example")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 