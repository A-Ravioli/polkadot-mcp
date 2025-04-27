# Polkadot Model Context Protocol (MCP)

A bridge between Large Language Models (LLMs) and the Polkadot blockchain ecosystem through the Model Context Protocol (MCP) standard.

![Project Banner](images/banner-placeholder.png)

## Demo Video

[![Polkadot MCP Demo](images/demo-thumbnail-placeholder.png)](https://youtu.be/your-video-id)

*Click the image above to watch the full demo*

## Project Overview

Polkadot MCP enables any LLM that supports the Model Context Protocol to interact directly with Polkadot blockchain wallets without requiring specialized blockchain knowledge. It exposes wallet functionality like balance checking, deposits, and withdrawals as standardized tools that LLMs can discover and invoke.

### The Problem

Large Language Models encounter several challenges when trying to interact with blockchain networks:

- **Technical Barriers**: Interacting with blockchains requires specialized knowledge of RPC interfaces, transaction formats, and cryptographic operations
- **Real-time Data Access**: LLMs lack access to current blockchain state and user wallet information
- **Security Concerns**: Direct wallet access by AI agents requires proper authorization mechanisms

### Our Solution

We've developed a complete MCP server implementation that:

1. **Simplifies Integration**: Provides a standardized interface for LLMs to interact with Polkadot
2. **Enhances Security**: Includes agent authorization to restrict sensitive operations
3. **Enables Real-time Access**: Allows LLMs to query current blockchain state and perform transactions
4. **Follows Open Standards**: Implements the Model Context Protocol specification for seamless LLM integration

## Features

- **Balance Checking**: Query wallet balances in real-time
- **Token Deposits**: Initiate deposits to any wallet address
- **Authorized Withdrawals**: Securely withdraw tokens with proper authorization
- **Network Information**: Access current blockchain state and network details
- **Agent Authorization**: Manage which AI agents can perform sensitive operations

## Screenshots

### MCP Server in Action

![MCP Server Discovery](images/discovery-screenshot-placeholder.png)
*MCP Server tool discovery in action*

![Wallet Operations](images/wallet-operations-placeholder.png)
*Performing wallet operations through the MCP interface*

### LLM Integration

![LLM Chat](images/llm-chat-placeholder.png)
*Example of an LLM using the MCP server to interact with a wallet*

## Smart Contract Architecture

Our solution is powered by a custom smart contract deployed on Polkadot Asset Hub. The contract provides secure wallet management functions specifically designed for AI agent interactions.

### Contract Components

The `AIWalletManager.sol` contract includes:

1. **Balance Management**
   - Maps addresses to token balances
   - Updates balances on deposits and withdrawals
   - Provides secure balance checking functionality

2. **Agent Authorization System**
   - Maintains a registry of authorized AI agents
   - Restricts sensitive operations to authorized agents only
   - Includes owner-only controls for managing agent permissions

3. **Security Mechanisms**
   - Implements checks-effects-interactions pattern
   - Includes balance verification for withdrawals
   - Emits events for all operations for transparency

### Function Descriptions

- `deposit(address account)`: Allows anyone to deposit tokens to a specified address
- `withdraw(address payable account, uint256 amount)`: Enables authorized agents to withdraw tokens
- `getBalance(address account)`: Returns the current balance of an address
- `authorizeAgent(address agent)`: Adds an AI agent to the authorized list
- `deauthorizeAgent(address agent)`: Removes an AI agent from the authorized list
- `isAuthorizedAgent(address agent)`: Checks if an agent is authorized

### Smart Contract Code

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title AIWalletManager
 * @dev A smart contract for managing wallet balances with AI agent authorization
 */
contract AIWalletManager {
    mapping(address => uint256) private balances;
    mapping(address => bool) private authorizedAgents;
    address public owner;
    
    event Deposit(address indexed account, uint256 amount);
    event Withdrawal(address indexed account, uint256 amount);
    event AgentAuthorized(address indexed agent);
    event AgentDeauthorized(address indexed agent);
    
    constructor() {
        owner = msg.sender;
    }
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }
    
    modifier onlyAuthorized() {
        require(msg.sender == owner || authorizedAgents[msg.sender], "Not authorized");
        _;
    }
    
    function authorizeAgent(address agent) external onlyOwner {
        require(agent != address(0), "Invalid agent address");
        authorizedAgents[agent] = true;
        emit AgentAuthorized(agent);
    }
    
    function deauthorizeAgent(address agent) external onlyOwner {
        authorizedAgents[agent] = false;
        emit AgentDeauthorized(agent);
    }
    
    function deposit(address account) external payable {
        require(msg.value > 0, "Amount must be greater than 0");
        require(account != address(0), "Invalid account address");
        
        balances[account] += msg.value;
        emit Deposit(account, msg.value);
    }
    
    function withdraw(address payable account, uint256 amount) external onlyAuthorized {
        require(amount > 0, "Amount must be greater than 0");
        require(account != address(0), "Invalid account address");
        require(balances[account] >= amount, "Insufficient balance");
        
        balances[account] -= amount;
        (bool success, ) = account.call{value: amount}("");
        require(success, "Transfer failed");
        
        emit Withdrawal(account, amount);
    }
    
    function getBalance(address account) external view returns (uint256) {
        return balances[account];
    }
    
    function isAuthorizedAgent(address agent) external view returns (bool) {
        return authorizedAgents[agent];
    }
}
```

## Block Explorer Link

[View AIWalletManager Contract on Polkadot Asset Hub](https://assethub.polkadot.io/contract/your-contract-address)

## Repository Structure

This repository is organized as follows:

```
polkadot-mcp/
├── contracts/                    # Smart contract code
│   └── AIWalletManager.sol       # Main wallet management contract
├── docs/                         # Documentation files
│   ├── images/                   # Screenshots and images
│   ├── project-summary.md        # Project summary document
│   └── README-full.md            # Full README template
├── polkadot_mcp_server.py        # MCP server implementation
├── polkadot_mcp_client.py        # Example MCP client
├── PolkadotMCP.js                # Node.js blockchain API
├── env.sample                    # Example environment configuration
├── requirements.txt              # Python dependencies
├── package.json                  # Node.js dependencies
└── README.md                     # Main repository README
```

## Installation and Usage

### Prerequisites

- Python 3.8+
- Node.js 14+
- Access to a Polkadot/Moonbeam node (or use a public RPC endpoint)

### Setup Instructions

1. Clone the repository:
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

4. Create a `.env` file by copying the sample:
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

### Running the Demo

1. Start the Polkadot API server:
   ```
   npm start
   ```

2. Run the MCP client demo (which will automatically start the MCP server):
   ```
   python polkadot_mcp_client.py
   ```

### Integrating with an LLM

To integrate this MCP server with an LLM:

1. Ensure your LLM platform supports the Model Context Protocol
2. Configure the LLM to connect to your MCP server
3. The LLM will automatically discover the available tools during initialization
4. The LLM can now interact with Polkadot wallets through natural language requests

Example of an LLM conversation using MCP:

```
User: What's my wallet balance?

LLM: [Invokes check_balance tool with the user's address]
Your wallet balance is 1.5 DOT.

User: Please deposit 0.5 DOT into my wallet.

LLM: [Invokes deposit tool with the user's address and amount 0.5]
I've deposited 0.5 DOT into your wallet. The transaction hash is 0x1234...
```

## Technical Deep Dive

For more technical details about the implementation, protocol, and architecture, please watch our explanation video:

[![Technical Deep Dive](images/technical-thumbnail-placeholder.png)](https://youtu.be/your-technical-video-id)

*Click the image above to watch the technical explanation*

## Future Development

We plan to expand this project with:

- **Multi-chain Support**: Extend to other Polkadot parachains
- **Advanced Operations**: Support for staking, governance participation, and NFT operations
- **Enhanced Security**: Multi-signature wallet support and rate limiting
- **LLM-specific Training**: Fine-tune models for blockchain interactions
- **UI Dashboard**: Build a web interface for monitoring and managing AI agent operations

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Polkadot Team for the excellent blockchain infrastructure
- Model Context Protocol developers for standardizing AI tool integration
- The open source community for support and inspiration 