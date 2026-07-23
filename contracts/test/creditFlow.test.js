const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("Tawtheeq mint -> score -> fund -> repay loop", function () {
  let invoiceToken, creditLogic, deployer, oracle, smeWallet;

  beforeEach(async function () {
    [deployer, oracle, smeWallet] = await ethers.getSigners();

    const InvoiceToken = await ethers.getContractFactory("InvoiceToken");
    invoiceToken = await InvoiceToken.deploy(deployer.address);
    await invoiceToken.waitForDeployment();

    const CreditLogic = await ethers.getContractFactory("CreditLogic");
    creditLogic = await CreditLogic.deploy(
      deployer.address,
      await invoiceToken.getAddress(),
      oracle.address,
      1_000_000n
    );
    await creditLogic.waitForDeployment();

    await invoiceToken.setCreditLogic(await creditLogic.getAddress());
  });

  it("runs the full loop end to end", async function () {
    const tx = await invoiceToken.mintInvoice(
      smeWallet.address,
      "P1_expat_operator",
      "Al Abbar Group",
      50000,
      Math.floor(Date.now() / 1000) + 30 * 86400,
      68
    );
    const receipt = await tx.wait();
    const tokenId = 1;

    await creditLogic.connect(oracle).pushScore("P1_expat_operator", 68);
    expect(await creditLogic.personaScores("P1_expat_operator")).to.equal(68n);

    await expect(creditLogic.connect(oracle).requestFunding(tokenId))
      .to.emit(creditLogic, "FundingApproved")
      .withArgs(tokenId, "P1_expat_operator", 50000n, 68n);

    const invoice = await invoiceToken.getInvoice(tokenId);
    expect(invoice.status).to.equal(1n); // Financed

    await expect(creditLogic.connect(oracle).recordRepayment(tokenId))
      .to.emit(creditLogic, "RepaymentRecorded");

    const repaid = await invoiceToken.getInvoice(tokenId);
    expect(repaid.status).to.equal(2n); // Repaid

    await creditLogic.connect(oracle).pushScore("P1_expat_operator", 72);
    expect(await creditLogic.personaScores("P1_expat_operator")).to.equal(72n);
  });

  it("denies funding below the score threshold", async function () {
    await invoiceToken.mintInvoice(
      smeWallet.address,
      "P2_thin_file_sme",
      "Some Contractor",
      20000,
      Math.floor(Date.now() / 1000) + 30 * 86400,
      40
    );
    await creditLogic.connect(oracle).pushScore("P2_thin_file_sme", 40);

    await expect(creditLogic.connect(oracle).requestFunding(1))
      .to.emit(creditLogic, "FundingDenied")
      .withArgs(1, "P2_thin_file_sme", "score below threshold");
  });
});
