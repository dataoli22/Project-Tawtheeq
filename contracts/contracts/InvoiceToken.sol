// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/// @notice One ERC-721 per verified SME invoice. Minted by the backend oracle
/// once the Phase 1/2 scoring engine has computed a score for the persona.
/// The CreditLogic contract is granted mint/status-update rights so the two
/// contracts can be deployed and wired together at deploy time.
contract InvoiceToken is ERC721, Ownable {
    enum Status {
        Pending,
        Financed,
        Repaid,
        Overdue
    }

    struct InvoiceData {
        string personaId;
        string counterparty;
        uint256 amountAed;
        uint256 dueDate; // unix timestamp
        uint256 scoreAtMint;
        Status status;
    }

    uint256 private _nextTokenId = 1;

    mapping(uint256 => InvoiceData) public invoices;

    address public creditLogic;

    event InvoiceMinted(uint256 indexed tokenId, string personaId, uint256 amountAed, uint256 scoreAtMint);
    event InvoiceStatusChanged(uint256 indexed tokenId, Status status);

    modifier onlyOwnerOrCreditLogic() {
        require(msg.sender == owner() || msg.sender == creditLogic, "InvoiceToken: not authorised");
        _;
    }

    constructor(address initialOwner) ERC721("Tawtheeq Invoice", "TWQINV") Ownable(initialOwner) {}

    function setCreditLogic(address _creditLogic) external onlyOwner {
        creditLogic = _creditLogic;
    }

    function mintInvoice(
        address to,
        string calldata personaId,
        string calldata counterparty,
        uint256 amountAed,
        uint256 dueDate,
        uint256 scoreAtMint
    ) external onlyOwner returns (uint256 tokenId) {
        tokenId = _nextTokenId++;
        _safeMint(to, tokenId);
        invoices[tokenId] = InvoiceData({
            personaId: personaId,
            counterparty: counterparty,
            amountAed: amountAed,
            dueDate: dueDate,
            scoreAtMint: scoreAtMint,
            status: Status.Pending
        });
        emit InvoiceMinted(tokenId, personaId, amountAed, scoreAtMint);
    }

    function setStatus(uint256 tokenId, Status status) external onlyOwnerOrCreditLogic {
        require(_ownerOf(tokenId) != address(0), "InvoiceToken: nonexistent token");
        invoices[tokenId].status = status;
        emit InvoiceStatusChanged(tokenId, status);
    }

    function getInvoice(uint256 tokenId) external view returns (InvoiceData memory) {
        require(_ownerOf(tokenId) != address(0), "InvoiceToken: nonexistent token");
        return invoices[tokenId];
    }
}
