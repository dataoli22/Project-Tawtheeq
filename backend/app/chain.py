"""web3.py wrapper around the deployed InvoiceToken / CreditLogic contracts.

Reads the address + ABI files written by `contracts/scripts/deploy.js` into
backend/app/chain_config/. Two signers are used, mirroring the contracts'
access control: the deployer key (contract owner, mints invoices) and the
oracle key (pushes scores, requests funding, records repayments) — matching
the PRD's "off-chain-to-on-chain push" oracle pattern (Section 6.2).
"""
import json
import os
from pathlib import Path

from web3 import Web3

CHAIN_CONFIG_DIR = Path(__file__).resolve().parent / "chain_config"


class ChainClient:
    def __init__(self):
        rpc_url = os.environ.get("RPC_URL", "http://127.0.0.1:8545")
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))

        deployment = json.loads((CHAIN_CONFIG_DIR / "deployment.json").read_text())
        invoice_abi = json.loads((CHAIN_CONFIG_DIR / "InvoiceToken.abi.json").read_text())
        credit_abi = json.loads((CHAIN_CONFIG_DIR / "CreditLogic.abi.json").read_text())

        self.invoice_token = self.w3.eth.contract(
            address=deployment["invoiceToken"], abi=invoice_abi
        )
        self.credit_logic = self.w3.eth.contract(
            address=deployment["creditLogic"], abi=credit_abi
        )

        self.deployer_key = os.environ["DEPLOYER_PRIVATE_KEY"]
        self.oracle_key = os.environ["ORACLE_PRIVATE_KEY"]
        self.deployer_account = self.w3.eth.account.from_key(self.deployer_key)
        self.oracle_account = self.w3.eth.account.from_key(self.oracle_key)

    def _send(self, fn, account_key):
        account = self.w3.eth.account.from_key(account_key)
        tx = fn.build_transaction({
            "from": account.address,
            "nonce": self.w3.eth.get_transaction_count(account.address),
        })
        signed = self.w3.eth.account.sign_transaction(tx, account_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        return receipt

    def mint_invoice(self, to: str, persona_id: str, counterparty: str,
                      amount_aed: int, due_date_unix: int, score_at_mint: int):
        fn = self.invoice_token.functions.mintInvoice(
            to, persona_id, counterparty, amount_aed, due_date_unix, score_at_mint
        )
        receipt = self._send(fn, self.deployer_key)
        minted = self.invoice_token.events.InvoiceMinted().process_receipt(receipt)
        token_id = minted[0]["args"]["tokenId"]
        return token_id, receipt.transactionHash.hex()

    def push_score(self, persona_id: str, score: int) -> str:
        fn = self.credit_logic.functions.pushScore(persona_id, score)
        receipt = self._send(fn, self.oracle_key)
        return receipt.transactionHash.hex()

    def request_funding(self, token_id: int):
        fn = self.credit_logic.functions.requestFunding(token_id)
        receipt = self._send(fn, self.oracle_key)
        approved = self.credit_logic.events.FundingApproved().process_receipt(receipt)
        denied = self.credit_logic.events.FundingDenied().process_receipt(receipt)
        return {
            "tx_hash": receipt.transactionHash.hex(),
            "approved": bool(approved),
            "denied_reason": denied[0]["args"]["reason"] if denied else None,
        }

    def record_repayment(self, token_id: int) -> str:
        fn = self.credit_logic.functions.recordRepayment(token_id)
        receipt = self._send(fn, self.oracle_key)
        return receipt.transactionHash.hex()

    def get_invoice(self, token_id: int):
        return self.invoice_token.functions.getInvoice(token_id).call()

    def get_persona_score_onchain(self, persona_id: str) -> int:
        return self.credit_logic.functions.personaScores(persona_id).call()


_client: ChainClient | None = None


def get_chain_client() -> ChainClient:
    global _client
    if _client is None:
        _client = ChainClient()
    return _client
