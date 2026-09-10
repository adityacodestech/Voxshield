from web3 import Web3
from contract_abi import CONTRACT_ABI
import sys

sys.path.append("..")
from risk_scoring import calculate_risk

print("Blockchain integration started")

contract_address = Web3.to_checksum_address(
    "0x5fbdb2315678afecb367f032d93f642f64180aa3"
)

print("Contract address:", contract_address)

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

if w3.is_connected():
    print("Connected to blockchain!")
else:
    print("Blockchain connection failed!")

contract = w3.eth.contract(
    address=contract_address,
    abi=CONTRACT_ABI
)

user_address = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"

score, level, action = calculate_risk(
    85,
    True,
    True,
    True
)

print("Calculated Risk Score:", score)
print("Calculated Risk Level:", level)
print("Calculated Action:", action)

tx = contract.functions.calculateRisk(score).transact({
    "from": user_address
})

w3.eth.wait_for_transaction_receipt(tx)

print("Transaction Hash:", tx.hex())
print("Risk score saved to blockchain!")

risk_data = contract.functions.getRisk(user_address).call()

print("Risk score:", risk_data[0])
print("Risk level:", risk_data[1])
print("Timestamp:", risk_data[2])