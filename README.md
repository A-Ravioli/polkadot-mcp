# Polkadot Model Context Protocol (MCP)

This project implements a [Model Context Protocol (MCP)](https://zencoder.ai/blog/model-context-protocol) server and client for interacting with Polkadot blockchain wallets. MCP is an open protocol that standardizes how applications provide context to large language models (LLMs), enabling them to interact with external systems through a common interface.

## Components

- **polkadot_mcp_server.py**: MCP server that exposes Polkadot wallet functionality
- **polkadot_mcp_client.py**: Example MCP client that connects to the server
- **PolkadotMCP.js**: Express.js server that provides the underlying Polkadot API
- **contracts/AIWalletManager.sol**: Solidity smart contract for wallet management

## Features

The MCP server exposes the following tools:

- **check_balance**: Get the balance of a wallet address
- **deposit**: Deposit tokens to a wallet address
- **withdraw**: Withdraw tokens from a wallet address
- **get_network_info**: Get information about the current blockchain network
- **check_agent_authorization**: Check if an agent address is authorized

## Prerequisites

- Python 3.8+
- Node.js 14+
- [Optional] Access to a Polkadot/Moonbeam node

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/polkadot-mcp.git
   cd polkadot-mcp
   ```

2. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Install Node.js dependencies:
   ```
   npm install
   ```

4. Create a `.env` file by copying the sample file:
   ```
   cp env.sample .env
   ```

5. Edit the `.env` file with your configuration:
   ```
   # Backend API configuration
   API_URL=http://localhost:3000
   API_KEY=your-api-key

   # Blockchain configuration
   CONTRACT_ADDRESS=YOUR_DEPLOYED_CONTRACT_ADDRESS
   PROVIDER_URL=https://rpc.api.moonbase.moonbeam.network
   PRIVATE_KEY=YOUR_PRIVATE_KEY
   PORT=3000

   # MCP server configuration
   MCP_MODE=stdio
   MCP_PORT=3001
   MCP_SERVER_PATH=./polkadot_mcp_server.py

   # Wallet configuration for examples
   WALLET_ADDRESS=0x123456789012345678901234567890123456789A
   ```

## Usage

1. Start the Polkadot API server:
   ```
   npm start
   ```

2. Run the MCP client demo (which automatically starts the MCP server):
   ```
   python polkadot_mcp_client.py
   ```

   The client will automatically read configuration from your `.env` file. However, you can still override these settings with command-line arguments:
   ```
   python polkadot_mcp_client.py --api-key override-api-key --address 0xAnotherWalletAddress
   ```

## Using with an LLM

This MCP server can be integrated with any LLM system that supports the Model Context Protocol. Here's a basic example of how a conversation might look:

```
User: What's my wallet balance?

LLM: [Invokes check_balance tool with the user's address]
Your wallet balance is 1.5 DOT.

User: Please deposit 0.5 DOT into my wallet.

LLM: [Invokes deposit tool with the user's address and amount 0.5]
I've deposited 0.5 DOT into your wallet. The transaction hash is 0x1234...
```

## Protocol Implementation

The MCP implementation follows the JSON-RPC format for communication:

1. **Discovery**: Clients can query the server for available tools, resources, and prompts.
2. **Tool Invocation**: Clients can invoke tools with specific parameters.

Example discovery request:
```json
{
  "jsonrpc": "2.0", 
  "id": 1,
  "method": "mcp.discover",
  "params": {}
}
```

Example tool invocation:
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "mcp.invoke",
  "params": {
    "name": "check_balance",
    "parameters": {
      "address": "0x123456789012345678901234567890123456789A"
    }
  }
}
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
