# Polkadot MCP (Minimum Compute Platform)

An MCP that allows AI agents to interact with smart contracts on the Polkadot ecosystem.

## Overview

This project provides a REST API that AI agents can use to interact with an EVM-compatible smart contract deployed on a Polkadot parachain (like Moonbeam, Astar, etc.). The smart contract serves as a simple wallet manager where agents can:

- Check token balances
- Deposit tokens
- Withdraw tokens
- Authorize and deauthorize AI agents

## Smart Contract

The smart contract (`AIWalletManager.sol`) is written in Solidity and can be deployed to any EVM-compatible parachain in the Polkadot ecosystem.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

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
        authorizedAgents[agent] = true;
        emit AgentAuthorized(agent);
    }
    
    function deauthorizeAgent(address agent) external onlyOwner {
        authorizedAgents[agent] = false;
        emit AgentDeauthorized(agent);
    }
    
    function deposit(address account) external payable {
        require(msg.value > 0, "Amount must be greater than 0");
        balances[account] += msg.value;
        emit Deposit(account, msg.value);
    }
    
    function withdraw(address payable account, uint256 amount) external onlyAuthorized {
        require(amount > 0, "Amount must be greater than 0");
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

## Prerequisites

- Node.js (v14 or higher)
- An EVM-compatible wallet with a private key
- Access to a Polkadot EVM-compatible network (Moonbeam, Astar, etc.)
- The deployed contract address on the network

## Installation

1. Clone this repository
```bash
git clone https://github.com/yourusername/polkadot-mcp.git
cd polkadot-mcp
```

2. Install dependencies
```bash
npm install
```

3. Create a `.env` file based on the example
```bash
cp .env.example .env
```

4. Edit the `.env` file with your configuration
```bash
CONTRACT_ADDRESS=your_deployed_contract_address
PROVIDER_URL=your_provider_url
PRIVATE_KEY=your_private_key
API_KEY=your_secure_api_key
```

## Deploying the Smart Contract

1. Go to [Remix IDE](https://remix.ethereum.org/)
2. Create a new file and paste the smart contract code
3. Compile the contract using Solidity compiler 0.8.0 or higher
4. In the deploy tab, connect Remix to MetaMask
5. Configure MetaMask for an EVM-compatible Polkadot network:
   - For Moonbeam's testnet (Moonbase Alpha):
     - Network Name: Moonbase Alpha
     - RPC URL: https://rpc.api.moonbase.moonbeam.network
     - Chain ID: 1287
     - Currency Symbol: DEV
   - For Astar's testnet (Shibuya):
     - Network Name: Shibuya
     - RPC URL: https://evm.shibuya.astar.network
     - Chain ID: 81
     - Currency Symbol: SBY
6. Deploy the contract and save the contract address

## Starting the MCP

Run the server:
```bash
npm start
```

For development with auto-restart:
```bash
npm run dev
```

## API Endpoints

All API endpoints require the `x-api-key` header with your API key.

### Health Check
```
GET /api/health
```

### Get Wallet Balance
```
GET /api/balance/:address
```

### Get Contract Owner
```
GET /api/owner
```

### Check if Address is Authorized Agent
```
GET /api/agent/:address
```

### Deposit Tokens
```
POST /api/deposit
Content-Type: application/json

{
  "address": "0x...",
  "amount": "0.1"
}
```

### Withdraw Tokens
```
POST /api/withdraw
Content-Type: application/json

{
  "address": "0x...",
  "amount": "0.1"
}
```

### Authorize an AI Agent
```
POST /api/authorize-agent
Content-Type: application/json

{
  "address": "0x..."
}
```

### Deauthorize an AI Agent
```
POST /api/deauthorize-agent
Content-Type: application/json

{
  "address": "0x..."
}
```

### Get Network Information
```
GET /api/network
```

## Integration with AI Agents

AI agents can interact with this MCP through HTTP requests. Here's an example in Python:

```python
import requests

API_URL = "http://localhost:3000/api"
API_KEY = "your-api-key"
HEADERS = {
    "Content-Type": "application/json",
    "x-api-key": API_KEY
}

# Get wallet balance
def get_balance(address):
    response = requests.get(f"{API_URL}/balance/{address}", headers=HEADERS)
    return response.json()

# Deposit tokens
def deposit(address, amount):
    data = {"address": address, "amount": str(amount)}
    response = requests.post(f"{API_URL}/deposit", json=data, headers=HEADERS)
    return response.json()

# Withdraw tokens
def withdraw(address, amount):
    data = {"address": address, "amount": str(amount)}
    response = requests.post(f"{API_URL}/withdraw", json=data, headers=HEADERS)
    return response.json()
```

## Security Considerations

- Always use HTTPS in production
- Store your private key securely, never commit it to your repository
- Use a strong API key and consider integrating OAuth2 for production use
- Consider implementing rate limiting per client
- Monitor transactions for unusual activity

## License

MIT
