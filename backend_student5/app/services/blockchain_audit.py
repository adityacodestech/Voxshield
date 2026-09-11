import os
from pathlib import Path

from web3 import Web3


RPC_URL = os.getenv(
    "VOXSHIELD_BLOCKCHAIN_RPC",
    "http://127.0.0.1:8545",
)

CONTRACT_ADDRESS = os.getenv(
    "VOXSHIELD_CONTRACT_ADDRESS",
    "0x5fbdb2315678afecb367f032d93f642f64180aa3",
)

ACCOUNT_ADDRESS = os.getenv(
    "VOXSHIELD_BLOCKCHAIN_ACCOUNT",
    "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
)

PRIVATE_KEY = os.getenv("VOXSHIELD_BLOCKCHAIN_PRIVATE_KEY")


CONTRACT_ABI = [
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "score",
                "type": "uint256",
            }
        ],
        "name": "calculateRisk",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
]


def record_risk_score(risk_score: int) -> dict:
    """
    Store the Student 3 risk score on the Student 4 blockchain.

    Blockchain failure does not crash the voice-analysis pipeline.
    """

    if not isinstance(risk_score, int):
        raise ValueError("risk_score must be an integer")

    if not 0 <= risk_score <= 100:
        raise ValueError("risk_score must be between 0 and 100")

    if not PRIVATE_KEY:
        return {
            "status": "unavailable",
            "reason": "Blockchain private key is not configured",
            "risk_score": risk_score,
        }

    web3 = Web3(Web3.HTTPProvider(RPC_URL))

    if not web3.is_connected():
        return {
            "status": "unavailable",
            "reason": "Blockchain node is not connected",
            "risk_score": risk_score,
        }

    contract = web3.eth.contract(
        address=Web3.to_checksum_address(CONTRACT_ADDRESS),
        abi=CONTRACT_ABI,
    )

    account = Web3.to_checksum_address(ACCOUNT_ADDRESS)

    nonce = web3.eth.get_transaction_count(account)

    transaction = contract.functions.calculateRisk(
        risk_score
    ).build_transaction(
        {
            "from": account,
            "nonce": nonce,
            "chainId": web3.eth.chain_id,
            "gas": 200000,
            "gasPrice": web3.eth.gas_price,
        }
    )

    signed_transaction = web3.eth.account.sign_transaction(
        transaction,
        PRIVATE_KEY,
    )

    transaction_hash = web3.eth.send_raw_transaction(
        signed_transaction.raw_transaction
    )

    receipt = web3.eth.wait_for_transaction_receipt(
        transaction_hash
    )

    return {
        "status": "recorded",
        "risk_score": risk_score,
        "transaction_hash": transaction_hash.hex(),
        "block_number": receipt.blockNumber,
    }