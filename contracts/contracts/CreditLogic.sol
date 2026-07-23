// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/Ownable.sol";
import "./InvoiceToken.sol";

/// @notice Reads the off-chain Tawtheeq Score (pushed by the FastAPI scoring
/// engine, acting as a simple push-oracle since no paid oracle network is
/// used) and applies the funding rule described in the PRD: score >= threshold
/// AND invoice amount <= simulated liquidity pool -> auto-approve and
/// disburse. Repayments top the pool back up (plus the simulated take rate)
/// and are what drives the persona's score trajectory upward.
contract CreditLogic is Ownable {
    InvoiceToken public immutable invoiceToken;

    address public oracle; // backend signer allowed to push scores + record repayments

    uint256 public scoreThreshold = 60; // 0-100 scale
    uint256 public liquidityPoolAed; // simulated available capital
    uint256 public takeRateBps = 150; // 1.50%, per deck's 0.5-2% take rate

    mapping(string => uint256) public personaScores; // personaId -> latest score (0-100)

    event ScorePushed(string personaId, uint256 score);
    event FundingApproved(uint256 indexed tokenId, string personaId, uint256 amountAed, uint256 scoreAtApproval);
    event FundingDenied(uint256 indexed tokenId, string personaId, string reason);
    event RepaymentRecorded(uint256 indexed tokenId, string personaId, uint256 feeAed);

    modifier onlyOracle() {
        require(msg.sender == oracle, "CreditLogic: not oracle");
        _;
    }

    constructor(address initialOwner, address _invoiceToken, address _oracle, uint256 initialLiquidityAed)
        Ownable(initialOwner)
    {
        invoiceToken = InvoiceToken(_invoiceToken);
        oracle = _oracle;
        liquidityPoolAed = initialLiquidityAed;
    }

    function setOracle(address _oracle) external onlyOwner {
        oracle = _oracle;
    }

    function setScoreThreshold(uint256 _threshold) external onlyOwner {
        scoreThreshold = _threshold;
    }

    function pushScore(string calldata personaId, uint256 score) external onlyOracle {
        require(score <= 100, "CreditLogic: score out of range");
        personaScores[personaId] = score;
        emit ScorePushed(personaId, score);
    }

    /// @notice Applies the funding rule to a minted-but-pending invoice.
    function requestFunding(uint256 tokenId) external onlyOracle {
        InvoiceToken.InvoiceData memory inv = invoiceToken.getInvoice(tokenId);
        require(inv.status == InvoiceToken.Status.Pending, "CreditLogic: invoice not pending");

        uint256 score = personaScores[inv.personaId];

        if (score < scoreThreshold) {
            emit FundingDenied(tokenId, inv.personaId, "score below threshold");
            return;
        }
        if (inv.amountAed > liquidityPoolAed) {
            emit FundingDenied(tokenId, inv.personaId, "insufficient simulated liquidity");
            return;
        }

        liquidityPoolAed -= inv.amountAed;
        invoiceToken.setStatus(tokenId, InvoiceToken.Status.Financed);
        emit FundingApproved(tokenId, inv.personaId, inv.amountAed, score);
    }

    /// @notice Simulates a successful repayment: principal + fee return to the
    /// pool, invoice marked repaid. Score recomputation happens off-chain in
    /// the scoring engine, which then calls pushScore with the new value.
    function recordRepayment(uint256 tokenId) external onlyOracle {
        InvoiceToken.InvoiceData memory inv = invoiceToken.getInvoice(tokenId);
        require(inv.status == InvoiceToken.Status.Financed, "CreditLogic: invoice not financed");

        uint256 fee = (inv.amountAed * takeRateBps) / 10000;
        liquidityPoolAed += inv.amountAed + fee;

        invoiceToken.setStatus(tokenId, InvoiceToken.Status.Repaid);
        emit RepaymentRecorded(tokenId, inv.personaId, fee);
    }

    function topUpLiquidity(uint256 amountAed) external onlyOwner {
        liquidityPoolAed += amountAed;
    }
}
