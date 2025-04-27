// This script deploys the AIWalletManager contract to the network

async function main() {
  console.log("Deploying AIWalletManager contract...");
  
  // Get the contract factory
  const AIWalletManager = await ethers.getContractFactory("AIWalletManager");
  
  // Deploy the contract
  const walletManager = await AIWalletManager.deploy();
  
  // Wait for deployment to finish
  await walletManager.deployed();
  
  console.log("AIWalletManager deployed to:", walletManager.address);
  
  // For verification purposes
  console.log("Contract owner:", await walletManager.owner());
  
  // Display additional info
  const network = await ethers.provider.getNetwork();
  console.log("Network:", network.name);
  console.log("Chain ID:", network.chainId);
  
  // Verify the contract on the block explorer if applicable
  if (network.name === "moonbase") {
    console.log("Verify on block explorer with:");
    console.log(`npx hardhat verify --network moonbase ${walletManager.address}`);
  }
  
  return walletManager;
}

// Run the deployment
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  }); 