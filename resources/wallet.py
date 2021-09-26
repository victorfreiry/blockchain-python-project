# Import dependencies
import subprocess
import json
from dotenv import load_dotenv
import os
from constants import *
# from bipwallet import wallet
from web3 import Web3
from eth_account import Account
from bit import PrivateKeyTestnet
from bit.network import NetworkAPI
from web3.middleware import geth_poa_middleware
from web3.gas_strategies.time_based import medium_gas_price_strategy

# Load and set environment variables
load_dotenv()
mnemonic=os.getenv("key")
print(mnemonic)
PRIVKEY = 'privkey'

# connect to local ETH/ geth
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
w3.eth.setGasPriceStrategy(medium_gas_price_strategy)
 
# Create a function called `derive_wallets`
def derive_wallets(mnemonic, coin, numderive):
    command = f'php ./hd-wallet-derive/hd-wallet-derive.php -g --mnemonic="{mnemonic}" --numderive="{numderive}" --coin="{coin}" --format=json'
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    # p_status = p.wait()
    return json.loads(output)

# Create a dictionary object called coins to store the output from `derive_wallets`.
coins = {ETH, BTC, BTCTEST}
numderive=3

# Just testing the derive wallets function
# print(derive_wallets(mnemonic, BTC, numderive))

wallets = {}
for coin in coins:
    wallets[coin] = derive_wallets(mnemonic, coin, numderive)

# print(wallets)

eth_key = wallets[ETH][0][PRIVKEY]
btc_key = wallets[BTC][0][PRIVKEY]
btctest_key = wallets[BTCTEST][0][PRIVKEY]

# print(f'ETH key {eth_key}')
# print(f'BTC key {btc_key}')
# print(f'BTCTEST key {btctest_key}')

# Create a function called `priv_key_to_account` that converts privkey strings to account objects.
def priv_key_to_account(coin, privkey):
    if coin == ETH:
        return Account.privateKeyToAccount(privkey)
    elif coin == BTCTEST:
        return PrivateKeyTestnet(privkey)


eth_account = priv_key_to_account(ETH, eth_key)
btctest_acc = priv_key_to_account(BTCTEST, btctest_key)

# print(eth_account.address)
# print(btctest_acc.address)

# Create a function called `create_tx` that creates an unsigned transaction appropriate metadata.
def create_tx(coin, account, recipient, amount):
    if coin == ETH:
        estimate = w3.eth.estimateGas({"from": eth_account.address, "to": recipient, "value": amount})

        return {
            "from": eth_account.address,
            "to": recipient,
            "value": amount,
            "gasPrice": w3.eth.gasPrice,
            "gas": estimate,
            "nonce": w3.eth.getTransactionCount(eth_account.address)
        }

    elif coin == BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(recipient, amount, BTC)])

# print(create_tx(ETH, eth_account, <receiver address>, 1000))


# Create a function called `send_tx` that calls `create_tx`, signs and sends the transaction.
def send_txn(coin, account, recipient, amount):
    txn = create_tx(coin, account, recipient, amount)
    if coin == ETH:
        signed_txn = eth_account.sign_transaction(txn)
        result = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        print(result.hex())
        return result.hex()
    elif coin == BTCTEST:
        signed_txn = account.sign_transaction(txn)
        print(signed_txn)
        return NetworkAPI.broadcast_tx_testnet(signed_txn)

# print(send_txn(ETH, eth_account, <reciever address>, 1000))

