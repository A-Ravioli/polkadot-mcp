const express = require('express');
const { ethers } = require('ethers');
const cors = require('cors');
const rateLimit = require('express-rate-limit');
const dotenv = require('dotenv');
const helmet = require('helmet');
const morgan = require('morgan');

// Load environment variables
dotenv.config();

const app = express();

// Middleware
app.use(express.json());
app.use(cors());
app.use(helmet());
app.use(morgan('combined'));

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});
app.use(limiter);

// ABI from the compiled AIWalletManager contract
const contractABI = [
  {
    "inputs": [],
    "stateMutability": "nonpayable",
    "type": "constructor"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "agent",
        "type": "address"
      }
    ],
    "name": "AgentAuthorized",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "agent",
        "type": "address"
      }
    ],
    "name": "AgentDeauthorized",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "account",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      }
    ],
    "name": "Deposit",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "account",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      }
    ],
    "name": "Withdrawal",
    "type": "event"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "agent",
        "type": "address"
      }
    ],
    "name": "authorizeAgent",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "agent",
        "type": "address"
      }
    ],
    "name": "deauthorizeAgent",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "account",
        "type": "address"
      }
    ],
    "name": "deposit",
    "outputs": [],
    "stateMutability": "payable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "account",
        "type": "address"
      }
    ],
    "name": "getBalance",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "agent",
        "type": "address"
      }
    ],
    "name": "isAuthorizedAgent",
    "outputs": [
      {
        "internalType": "bool",
        "name": "",
        "type": "bool"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "owner",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address payable",
        "name": "account",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      }
    ],
    "name": "withdraw",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  }
];

// Configuration
const contractAddress = process.env.CONTRACT_ADDRESS || "YOUR_DEPLOYED_CONTRACT_ADDRESS";
const providerUrl = process.env.PROVIDER_URL || "https://rpc.api.moonbase.moonbeam.network";
const privateKey = process.env.PRIVATE_KEY || "YOUR_PRIVATE_KEY";
const apiKey = process.env.API_KEY || "test-api-key";

// API key authentication middleware
const authenticateApiKey = (req, res, next) => {
  const requestApiKey = req.headers['x-api-key'];
  
  if (!requestApiKey || requestApiKey !== apiKey) {
    return res.status(401).json({ error: 'Unauthorized: Invalid API key' });
  }
  
  next();
};

// Setup provider and wallet
let provider, wallet, contract;

try {
  provider = new ethers.providers.JsonRpcProvider(providerUrl);
  wallet = new ethers.Wallet(privateKey, provider);
  contract = new ethers.Contract(contractAddress, contractABI, wallet);
} catch (error) {
  console.error('Error initializing blockchain connection:', error);
}

// Validate Ethereum address
const isValidAddress = (address) => {
  return ethers.utils.isAddress(address);
};

// Helper for standard error responses
const handleError = (res, error, statusCode = 500) => {
  console.error(error);
  
  // Provide more user-friendly error message based on error type
  if (error.code === 'INSUFFICIENT_FUNDS') {
    return res.status(400).json({ error: 'Insufficient funds for this transaction' });
  } else if (error.code === 'UNPREDICTABLE_GAS_LIMIT') {
    return res.status(400).json({ error: 'Transaction would fail. Possible reasons: insufficient balance or unauthorized access' });
  }
  
  res.status(statusCode).json({ 
    error: error.message || 'An unexpected error occurred',
    code: error.code || 'UNKNOWN_ERROR'
  });
};

// API Routes
app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    network: providerUrl,
    contractAddress 
  });
});

// Get wallet balance
app.get('/api/balance/:address', authenticateApiKey, async (req, res) => {
  try {
    const { address } = req.params;
    
    if (!isValidAddress(address)) {
      return res.status(400).json({ error: 'Invalid Ethereum address' });
    }
    
    const balance = await contract.getBalance(address);
    const formattedBalance = ethers.utils.formatEther(balance);
    
    res.json({ 
      address, 
      balance: balance.toString(),
      formattedBalance,
      unit: 'ETH' 
    });
  } catch (error) {
    handleError(res, error);
  }
});

// Get contract owner
app.get('/api/owner', authenticateApiKey, async (req, res) => {
  try {
    const owner = await contract.owner();
    res.json({ owner });
  } catch (error) {
    handleError(res, error);
  }
});

// Check if an address is an authorized agent
app.get('/api/agent/:address', authenticateApiKey, async (req, res) => {
  try {
    const { address } = req.params;
    
    if (!isValidAddress(address)) {
      return res.status(400).json({ error: 'Invalid Ethereum address' });
    }
    
    const isAuthorized = await contract.isAuthorizedAgent(address);
    res.json({ address, isAuthorized });
  } catch (error) {
    handleError(res, error);
  }
});

// Deposit tokens to a wallet
app.post('/api/deposit', authenticateApiKey, async (req, res) => {
  try {
    const { address, amount } = req.body;
    
    if (!address || !amount) {
      return res.status(400).json({ error: 'Address and amount are required' });
    }
    
    if (!isValidAddress(address)) {
      return res.status(400).json({ error: 'Invalid Ethereum address' });
    }
    
    if (isNaN(parseFloat(amount)) || parseFloat(amount) <= 0) {
      return res.status(400).json({ error: 'Amount must be a positive number' });
    }
    
    const parsedAmount = ethers.utils.parseEther(amount.toString());
    const tx = await contract.deposit(address, { value: parsedAmount });
    const receipt = await tx.wait();
    
    res.json({ 
      success: true, 
      transaction: tx.hash,
      blockNumber: receipt.blockNumber,
      gasUsed: receipt.gasUsed.toString(),
      address,
      amount
    });
  } catch (error) {
    handleError(res, error);
  }
});

// Withdraw tokens from a wallet
app.post('/api/withdraw', authenticateApiKey, async (req, res) => {
  try {
    const { address, amount } = req.body;
    
    if (!address || !amount) {
      return res.status(400).json({ error: 'Address and amount are required' });
    }
    
    if (!isValidAddress(address)) {
      return res.status(400).json({ error: 'Invalid Ethereum address' });
    }
    
    if (isNaN(parseFloat(amount)) || parseFloat(amount) <= 0) {
      return res.status(400).json({ error: 'Amount must be a positive number' });
    }
    
    const parsedAmount = ethers.utils.parseEther(amount.toString());
    const tx = await contract.withdraw(address, parsedAmount);
    const receipt = await tx.wait();
    
    res.json({ 
      success: true, 
      transaction: tx.hash,
      blockNumber: receipt.blockNumber,
      gasUsed: receipt.gasUsed.toString(),
      address,
      amount
    });
  } catch (error) {
    handleError(res, error);
  }
});

// Authorize an AI agent
app.post('/api/authorize-agent', authenticateApiKey, async (req, res) => {
  try {
    const { address } = req.body;
    
    if (!address) {
      return res.status(400).json({ error: 'Agent address is required' });
    }
    
    if (!isValidAddress(address)) {
      return res.status(400).json({ error: 'Invalid Ethereum address' });
    }
    
    const tx = await contract.authorizeAgent(address);
    const receipt = await tx.wait();
    
    res.json({ 
      success: true, 
      transaction: tx.hash,
      blockNumber: receipt.blockNumber,
      agentAddress: address,
      authorized: true
    });
  } catch (error) {
    handleError(res, error);
  }
});

// Deauthorize an AI agent
app.post('/api/deauthorize-agent', authenticateApiKey, async (req, res) => {
  try {
    const { address } = req.body;
    
    if (!address) {
      return res.status(400).json({ error: 'Agent address is required' });
    }
    
    if (!isValidAddress(address)) {
      return res.status(400).json({ error: 'Invalid Ethereum address' });
    }
    
    const tx = await contract.deauthorizeAgent(address);
    const receipt = await tx.wait();
    
    res.json({ 
      success: true, 
      transaction: tx.hash,
      blockNumber: receipt.blockNumber,
      agentAddress: address,
      authorized: false
    });
  } catch (error) {
    handleError(res, error);
  }
});

// Get network information
app.get('/api/network', authenticateApiKey, async (req, res) => {
  try {
    const network = await provider.getNetwork();
    const blockNumber = await provider.getBlockNumber();
    const gasPrice = await provider.getGasPrice();
    
    res.json({
      chainId: network.chainId,
      name: network.name,
      blockNumber,
      gasPrice: gasPrice.toString(),
      formattedGasPrice: ethers.utils.formatUnits(gasPrice, 'gwei') + ' gwei'
    });
  } catch (error) {
    handleError(res, error);
  }
});

// Error handling for non-existent routes
app.use((req, res) => {
  res.status(404).json({ error: 'Endpoint not found' });
});

// Global error handler
app.use((err, req, res, next) => {
  console.error('Unhandled error:', err);
  res.status(500).json({ error: 'Server error', message: err.message });
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Polkadot AI Wallet MCP running on port ${PORT}`);
  console.log(`Network: ${providerUrl}`);
  console.log(`Contract address: ${contractAddress}`);
});