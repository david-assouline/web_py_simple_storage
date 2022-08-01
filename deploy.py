from http.cookies import SimpleCookie
import os
from solcx import compile_standard, install_solc
import json
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

# Compile solidity
install_solc("0.6.0")
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.6.0",
)
with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# connect ganache
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
chain_id = 1337
my_address = "0x37E3cd1aD4972d83Ad2413E598c246E3805033b0"
private_key = os.getenv("PRIVATE_KEY")

# create contract
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

# get latest transaction
nonce = w3.eth.getTransactionCount(my_address)

# 1. build transaction
# 2. sign transaction
# 3. send transaction
transaction = SimpleStorage.constructor().buildTransaction(
    {"gasPrice": w3.eth.gas_price, "chainId": chain_id, "from": my_address, "nonce": nonce}
)
print(transaction)

signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
# send signed transaction
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

# work with contract
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
print(simple_storage.functions.retrieve().call())
store_transaction = simple_storage.functions.store(69).buildTransaction({"chainId": chain_id, "from": my_address, "nonce": nonce + 1})
signed_store_txn = w3.eth.account.sign_transasction(store_transaction, private_key=private_key)
send_store_tx = w3.eth.send_raw_trnsaction(signed_store_txn.rawTransasction)
tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)