const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("AIWalletManager", function () {
  let walletManager;
  let owner;
  let agent;
  let user1;
  let user2;
  
  // Set up test environment before each test
  beforeEach(async function () {
    // Get signers (accounts)
    [owner, agent, user1, user2] = await ethers.getSigners();
    
    // Deploy the contract
    const AIWalletManager = await ethers.getContractFactory("AIWalletManager");
    walletManager = await AIWalletManager.deploy();
    await walletManager.deployed();
  });
  
  // Test the constructor
  describe("Deployment", function () {
    it("Should set the right owner", async function () {
      expect(await walletManager.owner()).to.equal(owner.address);
    });
    
    it("Should initialize with zero balances", async function () {
      expect(await walletManager.getBalance(user1.address)).to.equal(0);
    });
  });
  
  // Test authorization functionality
  describe("Authorization", function () {
    it("Should allow the owner to authorize an agent", async function () {
      await walletManager.authorizeAgent(agent.address);
      expect(await walletManager.isAuthorizedAgent(agent.address)).to.equal(true);
    });
    
    it("Should allow the owner to deauthorize an agent", async function () {
      await walletManager.authorizeAgent(agent.address);
      await walletManager.deauthorizeAgent(agent.address);
      expect(await walletManager.isAuthorizedAgent(agent.address)).to.equal(false);
    });
    
    it("Should revert when a non-owner tries to authorize an agent", async function () {
      await expect(
        walletManager.connect(agent).authorizeAgent(user1.address)
      ).to.be.revertedWith("Only owner can call this function");
    });
    
    it("Should revert when authorizing the zero address", async function () {
      await expect(
        walletManager.authorizeAgent(ethers.constants.AddressZero)
      ).to.be.revertedWith("Invalid agent address");
    });
  });
  
  // Test deposit functionality
  describe("Deposits", function () {
    it("Should allow anyone to deposit tokens", async function () {
      const depositAmount = ethers.utils.parseEther("1.0");
      
      await walletManager.connect(user1).deposit(user1.address, {
        value: depositAmount
      });
      
      expect(await walletManager.getBalance(user1.address)).to.equal(depositAmount);
    });
    
    it("Should emit a Deposit event", async function () {
      const depositAmount = ethers.utils.parseEther("0.5");
      
      await expect(
        walletManager.connect(user1).deposit(user2.address, {
          value: depositAmount
        })
      )
        .to.emit(walletManager, "Deposit")
        .withArgs(user2.address, depositAmount);
    });
    
    it("Should revert when depositing zero tokens", async function () {
      await expect(
        walletManager.connect(user1).deposit(user1.address, {
          value: 0
        })
      ).to.be.revertedWith("Amount must be greater than 0");
    });
    
    it("Should revert when depositing to zero address", async function () {
      await expect(
        walletManager.connect(user1).deposit(ethers.constants.AddressZero, {
          value: ethers.utils.parseEther("1.0")
        })
      ).to.be.revertedWith("Invalid account address");
    });
  });
  
  // Test withdrawal functionality
  describe("Withdrawals", function () {
    beforeEach(async function () {
      // Authorize the agent and deposit tokens to user1
      await walletManager.authorizeAgent(agent.address);
      const depositAmount = ethers.utils.parseEther("2.0");
      await walletManager.connect(user1).deposit(user1.address, {
        value: depositAmount
      });
    });
    
    it("Should allow the owner to withdraw tokens", async function () {
      const withdrawAmount = ethers.utils.parseEther("1.0");
      const initialBalance = await ethers.provider.getBalance(user1.address);
      
      await walletManager.withdraw(user1.address, withdrawAmount);
      
      const newBalance = await ethers.provider.getBalance(user1.address);
      expect(newBalance.sub(initialBalance)).to.equal(withdrawAmount);
      expect(await walletManager.getBalance(user1.address)).to.equal(withdrawAmount); // Should have 1 ETH left
    });
    
    it("Should allow an authorized agent to withdraw tokens", async function () {
      const withdrawAmount = ethers.utils.parseEther("1.0");
      const initialBalance = await ethers.provider.getBalance(user1.address);
      
      await walletManager.connect(agent).withdraw(user1.address, withdrawAmount);
      
      const newBalance = await ethers.provider.getBalance(user1.address);
      expect(newBalance.sub(initialBalance)).to.equal(withdrawAmount);
    });
    
    it("Should emit a Withdrawal event", async function () {
      const withdrawAmount = ethers.utils.parseEther("1.0");
      
      await expect(
        walletManager.withdraw(user1.address, withdrawAmount)
      )
        .to.emit(walletManager, "Withdrawal")
        .withArgs(user1.address, withdrawAmount);
    });
    
    it("Should revert when a non-authorized user tries to withdraw", async function () {
      const withdrawAmount = ethers.utils.parseEther("1.0");
      
      await expect(
        walletManager.connect(user2).withdraw(user1.address, withdrawAmount)
      ).to.be.revertedWith("Not authorized");
    });
    
    it("Should revert when withdrawing more than the balance", async function () {
      const withdrawAmount = ethers.utils.parseEther("3.0"); // More than the 2 ETH deposited
      
      await expect(
        walletManager.withdraw(user1.address, withdrawAmount)
      ).to.be.revertedWith("Insufficient balance");
    });
    
    it("Should revert when withdrawing zero tokens", async function () {
      await expect(
        walletManager.withdraw(user1.address, 0)
      ).to.be.revertedWith("Amount must be greater than 0");
    });
  });
  
  // Test ownership functionality
  describe("Ownership", function () {
    it("Should allow transferring ownership", async function () {
      await walletManager.transferOwnership(user1.address);
      expect(await walletManager.owner()).to.equal(user1.address);
    });
    
    it("Should revert when transferring ownership to zero address", async function () {
      await expect(
        walletManager.transferOwnership(ethers.constants.AddressZero)
      ).to.be.revertedWith("Invalid owner address");
    });
    
    it("Should revert when a non-owner tries to transfer ownership", async function () {
      await expect(
        walletManager.connect(user1).transferOwnership(user2.address)
      ).to.be.revertedWith("Only owner can call this function");
    });
  });
}); 