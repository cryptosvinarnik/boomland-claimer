from loguru import logger
from web3 import Web3
from web3.middleware import geth_poa_middleware


def init_web3(RPC_URL: str) -> Web3:
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    return w3


def send_tx(w3: Web3, private_key: str, contract_address, data) -> str:
    account = w3.eth.account.privateKeyToAccount(private_key)
    nonce = w3.eth.get_transaction_count(account.address, "pending")

    tx = {
        "nonce": nonce,
        "chainId": w3.eth.chain_id,
        "to": contract_address,
        "from": account.address,
        "value": 0,
        "gas": 60_000,
        "gasPrice": w3.eth.gas_price,
        "data": data
    }

    signed_tx = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction).hex()

    return tx_hash


def main():
    w3 = init_web3(input("RPC URL >> "))

    if not w3.isConnected():
        logger.error("Can't connect to RPC")
        return
    
    BOOMLAND_CONTRACT = Web3.toChecksumAddress("0x3a1f862d8323138f14494f9fb50c537906b12b81")
    BOOMLAND_CLAIM_DATA = "0x359cf2b7"

    private_keys = open(input("File with private keys >> ")).read().splitlines()

    for private_key in private_keys:
        try:
            tx_hash = send_tx(w3, private_key, BOOMLAND_CONTRACT, BOOMLAND_CLAIM_DATA)
            logger.success(f"Sent tx from {private_key} with {tx_hash=}")
        except Exception as e:
            logger.error(f"Error sending tx from {private_key}: {e}")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception as e:
        logger.error(e)
