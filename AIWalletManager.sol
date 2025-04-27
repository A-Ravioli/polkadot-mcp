// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title AIWalletManager
 * @dev A simple wallet manager that allows AI agents to deposit, withdraw and check balances of tokens
 */
contract AIWalletManager {
    mapping(address => uint256) private balances;
    mapping(address => bool) private authorizedAgents;
    address public owner;
    
    event Deposit(address indexed account, uint256 amount);
    event Withdrawal(address indexed account, uint256 amount);
    event AgentAuthorized(address indexed agent);
    event AgentDeauthorized(address indexed agent);
    
    /**
     * @dev Sets the contract deployer as the owner
     */
    constructor() {
        owner = msg.sender;
    }
    
    /**
     * @dev Throws if called by any account other than the owner
     */
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }
    
    /**
     * @dev Throws if called by any account other than the owner or an authorized agent
     */
    modifier onlyAuthorized() {
        require(msg.sender == owner || authorizedAgents[msg.sender], "Not authorized");
        _;
    }
    
    /**
     * @dev Authorizes an AI agent to make withdrawals
     * @param agent The address of the agent to authorize
     */
    function authorizeAgent(address agent) external onlyOwner {
        require(agent != address(0), "Invalid agent address");
        authorizedAgents[agent] = true;
        emit AgentAuthorized(agent);
    }
    
    /**
     * @dev Deauthorizes an AI agent
     * @param agent The address of the agent to deauthorize
     */
    function deauthorizeAgent(address agent) external onlyOwner {
        authorizedAgents[agent] = false;
        emit AgentDeauthorized(agent);
    }
    
    /**
     * @dev Deposits tokens to an account
     * @param account The address to deposit tokens to
     */
    function deposit(address account) external payable {
        require(msg.value > 0, "Amount must be greater than 0");
        require(account != address(0), "Invalid account address");
        
        balances[account] += msg.value;
        emit Deposit(account, msg.value);
    }
    
    /**
     * @dev Withdraws tokens from an account
     * @param account The address to withdraw tokens from
     * @param amount The amount of tokens to withdraw
     */
    function withdraw(address payable account, uint256 amount) external onlyAuthorized {
        require(amount > 0, "Amount must be greater than 0");
        require(account != address(0), "Invalid account address");
        require(balances[account] >= amount, "Insufficient balance");
        
        balances[account] -= amount;
        (bool success, ) = account.call{value: amount}("");
        require(success, "Transfer failed");
        
        emit Withdrawal(account, amount);
    }
    
    /**
     * @dev Gets the balance of an account
     * @param account The address to check the balance of
     * @return The balance of the account
     */
    function getBalance(address account) external view returns (uint256) {
        return balances[account];
    }
    
    /**
     * @dev Checks if an address is an authorized agent
     * @param agent The address to check
     * @return True if the address is an authorized agent, false otherwise
     */
    function isAuthorizedAgent(address agent) external view returns (bool) {
        return authorizedAgents[agent];
    }
    
    /**
     * @dev Gets the contract owner
     * @return The address of the contract owner
     */
    function getOwner() external view returns (address) {
        return owner;
    }
    
    /**
     * @dev Transfers ownership of the contract
     * @param newOwner The address of the new owner
     */
    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "Invalid owner address");
        owner = newOwner;
    }
}