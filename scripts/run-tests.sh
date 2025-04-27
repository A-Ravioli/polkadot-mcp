#!/bin/bash

# Run-Tests script for Polkadot MCP
# This script runs all tests for the Polkadot MCP project

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting Polkadot MCP Test Suite${NC}"
echo "=================================="

# Run API tests
echo -e "\n${YELLOW}Running API Tests:${NC}"
echo "----------------------------------"
npm run test:api
if [ $? -eq 0 ]; then
  echo -e "${GREEN}API Tests Passed!${NC}"
else
  echo -e "${RED}API Tests Failed!${NC}"
  exit 1
fi

# Run Smart Contract tests
echo -e "\n${YELLOW}Running Smart Contract Tests:${NC}"
echo "----------------------------------"
npm run test:contract
if [ $? -eq 0 ]; then
  echo -e "${GREEN}Smart Contract Tests Passed!${NC}"
else
  echo -e "${RED}Smart Contract Tests Failed!${NC}"
  exit 1
fi

# Run Python AI Agent tests
echo -e "\n${YELLOW}Running Python AI Agent Tests:${NC}"
echo "----------------------------------"
npm run test:python
if [ $? -eq 0 ]; then
  echo -e "${GREEN}Python AI Agent Tests Passed!${NC}"
else
  echo -e "${RED}Python AI Agent Tests Failed!${NC}"
  exit 1
fi

echo -e "\n${GREEN}All tests passed successfully!${NC}"
echo "==================================" 