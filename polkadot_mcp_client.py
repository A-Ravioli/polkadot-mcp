#!/usr/bin/env python3
"""
Polkadot Model Context Protocol (MCP) Client
This implements an MCP client that connects to the Polkadot MCP server
"""

import json
import sys
import os
import asyncio
import logging
import argparse
import subprocess
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
logger = logging.getLogger("PolkadotMCPClient")

class PolkadotMCPClient:
    """
    MCP client implementation for connecting to a Polkadot MCP server
    """
    
    def __init__(self, server_path: str):
        """
        Initialize the MCP client
        
        Args:
            server_path: Path to the MCP server Python script
        """
        self.server_path = server_path
        self.server_process = None
        self.tools = []
        self.resources = []
        self.prompts = []
        self.request_id = 0
    
    async def start(self, api_url: str, api_key: str):
        """
        Start the MCP server and initialize the connection
        
        Args:
            api_url: Base URL of the Polkadot API
            api_key: API key for authentication
        """
        logger.info(f"Starting MCP server: {self.server_path}")
        self.server_process = await asyncio.create_subprocess_exec(
            sys.executable, self.server_path,
            "--api-url", api_url,
            "--api-key", api_key,
            "--mode", "stdio",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Discover available tools, resources, and prompts
        await self.discover()
    
    async def stop(self):
        """
        Stop the MCP server process
        """
        if self.server_process:
            logger.info("Stopping MCP server")
            self.server_process.terminate()
            await self.server_process.wait()
            self.server_process = None
    
    async def send_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a request to the MCP server
        
        Args:
            method: The method to call
            params: The parameters for the method
            
        Returns:
            Dict containing the response
        """
        if not self.server_process:
            raise Exception("MCP server is not running")
        
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params
        }
        
        # Write the request to the server's stdin
        request_json = json.dumps(request) + "\n"
        self.server_process.stdin.write(request_json.encode())
        await self.server_process.stdin.drain()
        
        # Read the response from the server's stdout
        response_line = await self.server_process.stdout.readline()
        if not response_line:
            raise Exception("MCP server closed the connection")
        
        response = json.loads(response_line.decode())
        
        if "error" in response:
            logger.error(f"Error from MCP server: {response['error']}")
        
        return response
    
    async def discover(self):
        """
        Discover available tools, resources, and prompts from the MCP server
        
        Returns:
            Dict containing discovery information
        """
        response = await self.send_request("mcp.discover", {})
        
        if "result" in response:
            self.tools = response["result"].get("tools", [])
            self.resources = response["result"].get("resources", [])
            self.prompts = response["result"].get("prompts", [])
            
            logger.info(f"Discovered {len(self.tools)} tools, {len(self.resources)} resources, and {len(self.prompts)} prompts")
            for tool in self.tools:
                logger.info(f"Tool: {tool['name']} - {tool['description']}")
            
            return response["result"]
        else:
            raise Exception("Failed to discover MCP capabilities")
    
    async def invoke_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoke a tool on the MCP server
        
        Args:
            tool_name: The name of the tool to invoke
            parameters: The parameters for the tool
            
        Returns:
            Dict containing the tool invocation result
        """
        response = await self.send_request("mcp.invoke", {
            "name": tool_name,
            "parameters": parameters
        })
        
        if "result" in response:
            return response["result"]
        elif "error" in response:
            raise Exception(f"Tool invocation error: {response['error']['message']}")
        else:
            raise Exception("Unknown response format")

async def main():
    """Initialize and run the MCP client demo"""
    parser = argparse.ArgumentParser(description="Polkadot MCP Client")
    parser.add_argument("--server-path", default=os.getenv("MCP_SERVER_PATH", "./polkadot_mcp_server.py"), help="Path to the MCP server script")
    parser.add_argument("--api-url", default=os.getenv("API_URL", "http://localhost:3000"), help="API URL for the Polkadot server")
    parser.add_argument("--api-key", default=os.getenv("API_KEY", "your-api-key"), help="API key for authentication")
    parser.add_argument("--address", default=os.getenv("WALLET_ADDRESS", "0x123456789012345678901234567890123456789A"), help="Wallet address to use in examples")
    
    args = parser.parse_args()
    
    client = PolkadotMCPClient(args.server_path)
    
    try:
        # Start the MCP server
        await client.start(args.api_url, args.api_key)
        
        # Example: Get network information
        logger.info("Getting network information...")
        network_info = await client.invoke_tool("get_network_info", {})
        logger.info(f"Network: {network_info.get('name')} (Chain ID: {network_info.get('chainId')})")
        logger.info(f"Current block: {network_info.get('blockNumber')}")
        
        # Example: Check wallet balance
        logger.info(f"Checking balance for address: {args.address}")
        balance_info = await client.invoke_tool("check_balance", {"address": args.address})
        if "error" not in balance_info:
            logger.info(f"Balance: {balance_info.get('formattedBalance')} {balance_info.get('unit')}")
        else:
            logger.error(f"Error checking balance: {balance_info.get('error')}")
        
        # Example: Deposit tokens
        logger.info(f"Depositing 0.1 tokens to address: {args.address}")
        deposit_result = await client.invoke_tool("deposit", {"address": args.address, "amount": "0.1"})
        if "error" not in deposit_result:
            logger.info(f"Deposit successful. Transaction: {deposit_result.get('transaction')}")
        else:
            logger.error(f"Error during deposit: {deposit_result.get('error')}")
        
        # Wait a moment for the transaction to be processed
        await asyncio.sleep(2)
        
        # Example: Check updated balance
        logger.info(f"Checking updated balance for address: {args.address}")
        updated_balance = await client.invoke_tool("check_balance", {"address": args.address})
        if "error" not in updated_balance:
            logger.info(f"Updated balance: {updated_balance.get('formattedBalance')} {updated_balance.get('unit')}")
        else:
            logger.error(f"Error checking updated balance: {updated_balance.get('error')}")
        
    finally:
        # Stop the MCP server
        await client.stop()

if __name__ == "__main__":
    asyncio.run(main()) 