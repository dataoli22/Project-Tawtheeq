const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  const [deployer, oracle] = await hre.ethers.getSigners();

  const InvoiceToken = await hre.ethers.getContractFactory("InvoiceToken");
  const invoiceToken = await InvoiceToken.deploy(deployer.address);
  await invoiceToken.waitForDeployment();

  const INITIAL_LIQUIDITY_AED = 1_000_000n; // simulated liquidity pool
  const CreditLogic = await hre.ethers.getContractFactory("CreditLogic");
  const creditLogic = await CreditLogic.deploy(
    deployer.address,
    await invoiceToken.getAddress(),
    oracle.address,
    INITIAL_LIQUIDITY_AED
  );
  await creditLogic.waitForDeployment();

  await (await invoiceToken.setCreditLogic(await creditLogic.getAddress())).wait();

  const deployment = {
    network: hre.network.name,
    invoiceToken: await invoiceToken.getAddress(),
    creditLogic: await creditLogic.getAddress(),
    deployer: deployer.address,
    oracle: oracle.address,
    deployedAt: new Date().toISOString(),
  };

  console.log("Deployed:", deployment);

  const outDir = path.join(__dirname, "..", "..", "backend", "app", "chain_config");
  fs.mkdirSync(outDir, { recursive: true });
  fs.writeFileSync(path.join(outDir, "deployment.json"), JSON.stringify(deployment, null, 2));

  const artifactsDir = path.join(__dirname, "..", "artifacts", "contracts");
  const invoiceAbi = JSON.parse(
    fs.readFileSync(path.join(artifactsDir, "InvoiceToken.sol", "InvoiceToken.json"))
  ).abi;
  const creditAbi = JSON.parse(
    fs.readFileSync(path.join(artifactsDir, "CreditLogic.sol", "CreditLogic.json"))
  ).abi;
  fs.writeFileSync(path.join(outDir, "InvoiceToken.abi.json"), JSON.stringify(invoiceAbi, null, 2));
  fs.writeFileSync(path.join(outDir, "CreditLogic.abi.json"), JSON.stringify(creditAbi, null, 2));

  console.log(`Wrote deployment + ABIs to ${outDir}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
