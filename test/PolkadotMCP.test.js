const request = require('supertest');
const express = require('express');

// Create mock ethers object first, before mocking the module
const mockEthers = {
  utils: {
    isAddress: jest.fn().mockImplementation((address) => {
      // Simple regex to check if it looks like an Ethereum address
      return /^0x[a-fA-F0-9]{40}$/.test(address);
    }),
    formatEther: jest.fn().mockReturnValue('1.0'),
    parseEther: jest.fn().mockReturnValue('1000000000000000000'),
    formatUnits: jest.fn().mockReturnValue('1')
  },
  BigNumber: {
    from: jest.fn().mockReturnValue({
      toString: () => '1000000000000000000'
    })
  },
  providers: {
    JsonRpcProvider: jest.fn().mockImplementation(() => ({
      getNetwork: jest.fn().mockResolvedValue({
        name: 'moonbase-alpha',
        chainId: 1287
      }),
      getBlockNumber: jest.fn().mockResolvedValue(12345),
      getGasPrice: jest.fn().mockResolvedValue({
        toString: () => '1000000000',
      })
    }))
  },
  Contract: jest.fn().mockImplementation(() => ({
    getBalance: jest.fn().mockResolvedValue({
      toString: () => '1000000000000000000'
    }),
    deposit: jest.fn().mockResolvedValue({
      hash: '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef',
      wait: jest.fn().mockResolvedValue({
        blockNumber: 12345,
        gasUsed: {
          toString: () => '21000'
        }
      })
    }),
    withdraw: jest.fn().mockResolvedValue({
      hash: '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef',
      wait: jest.fn().mockResolvedValue({
        blockNumber: 12345,
        gasUsed: {
          toString: () => '21000'
        }
      })
    }),
    owner: jest.fn().mockResolvedValue('0x742d35Cc6634C0532925a3b844Bc454e4438f44e'),
    isAuthorizedAgent: jest.fn().mockImplementation((address) => {
      // Mock authorized agents
      return Promise.resolve(address === '0x742d35Cc6634C0532925a3b844Bc454e4438f44e');
    }),
    authorizeAgent: jest.fn().mockResolvedValue({
      hash: '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef',
      wait: jest.fn().mockResolvedValue({
        blockNumber: 12345,
        gasUsed: {
          toString: () => '21000'
        }
      })
    }),
    deauthorizeAgent: jest.fn().mockResolvedValue({
      hash: '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef',
      wait: jest.fn().mockResolvedValue({
        blockNumber: 12345,
        gasUsed: {
          toString: () => '21000'
        }
      })
    })
  })),
  Wallet: jest.fn().mockImplementation(() => ({
    address: '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
  }))
};

// Mock ethers.js
jest.mock('ethers', () => mockEthers);

// Import our app
const app = express();
const cors = require('cors');
const helmet = require('helmet');

// Get the mock ethers for use in tests
const ethers = mockEthers;

// Middleware setup similar to PolkadotMCP.js but simplified for testing
app.use(express.json());
app.use(cors());
app.use(helmet());

// Mock API key for testing
const TEST_API_KEY = 'test-api-key';

// Mock the authenticateApiKey middleware
const authenticateApiKey = (req, res, next) => {
  const requestApiKey = req.headers['x-api-key'];
  
  if (!requestApiKey || requestApiKey !== TEST_API_KEY) {
    return res.status(401).json({ error: 'Unauthorized: Invalid API key' });
  }
  
  next();
};

// Setup test contract and routes
const provider = new ethers.providers.JsonRpcProvider();
const wallet = new ethers.Wallet('0x0000000000000000000000000000000000000000000000000000000000000001', provider);
const contract = new ethers.Contract(
  '0x1234567890123456789012345678901234567890',
  [], // ABI not needed for mocked contract
  wallet
);

// Helper functions
const isValidAddress = (address) => {
  return ethers.utils.isAddress(address);
};

const handleError = (res, error, statusCode = 500) => {
  console.error(error);
  res.status(statusCode).json({ 
    error: error.message || 'An unexpected error occurred',
    code: error.code || 'UNKNOWN_ERROR'
  });
};

// Set up routes for testing
app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    network: 'moonbase-alpha',
    contractAddress: '0x1234567890123456789012345678901234567890'
  });
});

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

app.get('/api/owner', authenticateApiKey, async (req, res) => {
  try {
    const owner = await contract.owner();
    res.json({ owner });
  } catch (error) {
    handleError(res, error);
  }
});

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

// Tests
describe('Polkadot MCP API', () => {
  // Health endpoint
  describe('GET /api/health', () => {
    it('should return health status', async () => {
      const res = await request(app).get('/api/health');
      expect(res.statusCode).toEqual(200);
      expect(res.body).toHaveProperty('status', 'ok');
      expect(res.body).toHaveProperty('network', 'moonbase-alpha');
      expect(res.body).toHaveProperty('contractAddress');
    });
  });

  // Balance endpoint
  describe('GET /api/balance/:address', () => {
    it('should return balance for valid address with correct API key', async () => {
      const res = await request(app)
        .get('/api/balance/0x742d35Cc6634C0532925a3b844Bc454e4438f44e')
        .set('x-api-key', TEST_API_KEY);
      
      expect(res.statusCode).toEqual(200);
      expect(res.body).toHaveProperty('address', '0x742d35Cc6634C0532925a3b844Bc454e4438f44e');
      expect(res.body).toHaveProperty('balance');
      expect(res.body).toHaveProperty('formattedBalance');
      expect(res.body).toHaveProperty('unit', 'ETH');
    });

    it('should return 401 with invalid API key', async () => {
      const res = await request(app)
        .get('/api/balance/0x742d35Cc6634C0532925a3b844Bc454e4438f44e')
        .set('x-api-key', 'invalid-key');
      
      expect(res.statusCode).toEqual(401);
    });

    it('should return 400 for invalid address', async () => {
      const res = await request(app)
        .get('/api/balance/invalid-address')
        .set('x-api-key', TEST_API_KEY);
      
      expect(res.statusCode).toEqual(400);
      expect(res.body).toHaveProperty('error', 'Invalid Ethereum address');
    });
  });

  // Owner endpoint
  describe('GET /api/owner', () => {
    it('should return contract owner', async () => {
      const res = await request(app)
        .get('/api/owner')
        .set('x-api-key', TEST_API_KEY);
      
      expect(res.statusCode).toEqual(200);
      expect(res.body).toHaveProperty('owner', '0x742d35Cc6634C0532925a3b844Bc454e4438f44e');
    });
  });

  // Agent authorization endpoint
  describe('GET /api/agent/:address', () => {
    it('should return authorization status for valid address', async () => {
      const res = await request(app)
        .get('/api/agent/0x742d35Cc6634C0532925a3b844Bc454e4438f44e')
        .set('x-api-key', TEST_API_KEY);
      
      expect(res.statusCode).toEqual(200);
      expect(res.body).toHaveProperty('address', '0x742d35Cc6634C0532925a3b844Bc454e4438f44e');
      expect(res.body).toHaveProperty('isAuthorized', true);
    });

    it('should return false for unauthorized address', async () => {
      const res = await request(app)
        .get('/api/agent/0x1234567890123456789012345678901234567890')
        .set('x-api-key', TEST_API_KEY);
      
      expect(res.statusCode).toEqual(200);
      expect(res.body).toHaveProperty('isAuthorized', false);
    });
  });

  // Deposit endpoint
  describe('POST /api/deposit', () => {
    it('should process valid deposit', async () => {
      const res = await request(app)
        .post('/api/deposit')
        .set('x-api-key', TEST_API_KEY)
        .send({
          address: '0x742d35Cc6634C0532925a3b844Bc454e4438f44e',
          amount: '0.1'
        });
      
      expect(res.statusCode).toEqual(200);
      expect(res.body).toHaveProperty('success', true);
      expect(res.body).toHaveProperty('transaction');
      expect(res.body).toHaveProperty('blockNumber');
      expect(res.body).toHaveProperty('gasUsed');
      expect(res.body).toHaveProperty('address', '0x742d35Cc6634C0532925a3b844Bc454e4438f44e');
      expect(res.body).toHaveProperty('amount', '0.1');
    });

    it('should return 400 for invalid amount', async () => {
      const res = await request(app)
        .post('/api/deposit')
        .set('x-api-key', TEST_API_KEY)
        .send({
          address: '0x742d35Cc6634C0532925a3b844Bc454e4438f44e',
          amount: '-0.1'
        });
      
      expect(res.statusCode).toEqual(400);
      expect(res.body).toHaveProperty('error', 'Amount must be a positive number');
    });

    it('should return 400 for missing parameters', async () => {
      const res = await request(app)
        .post('/api/deposit')
        .set('x-api-key', TEST_API_KEY)
        .send({
          address: '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
          // Missing amount
        });
      
      expect(res.statusCode).toEqual(400);
      expect(res.body).toHaveProperty('error', 'Address and amount are required');
    });
  });

  // Withdraw endpoint
  describe('POST /api/withdraw', () => {
    it('should process valid withdrawal', async () => {
      const res = await request(app)
        .post('/api/withdraw')
        .set('x-api-key', TEST_API_KEY)
        .send({
          address: '0x742d35Cc6634C0532925a3b844Bc454e4438f44e',
          amount: '0.1'
        });
      
      expect(res.statusCode).toEqual(200);
      expect(res.body).toHaveProperty('success', true);
      expect(res.body).toHaveProperty('transaction');
      expect(res.body).toHaveProperty('blockNumber');
      expect(res.body).toHaveProperty('gasUsed');
      expect(res.body).toHaveProperty('address', '0x742d35Cc6634C0532925a3b844Bc454e4438f44e');
      expect(res.body).toHaveProperty('amount', '0.1');
    });

    it('should return 400 for invalid amount', async () => {
      const res = await request(app)
        .post('/api/withdraw')
        .set('x-api-key', TEST_API_KEY)
        .send({
          address: '0x742d35Cc6634C0532925a3b844Bc454e4438f44e',
          amount: '0'
        });
      
      expect(res.statusCode).toEqual(400);
      expect(res.body).toHaveProperty('error', 'Amount must be a positive number');
    });
  });
}); 