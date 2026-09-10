import { network } from "hardhat";

async function main() {
  const { viem } = await network.connect();

  const riskScoring = await viem.deployContract("RiskScoring");

  console.log("RiskScoring deployed to:", riskScoring.address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});