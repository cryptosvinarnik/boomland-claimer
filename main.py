from loguru import logger
from web3 import Account, Web3
from web3.exceptions import ContractLogicError
from web3.middleware import geth_poa_middleware


def init_web3(RPC_URL: str) -> Web3:
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    return w3


def init_accounts(w3: Web3, private_keys: list) -> list[Account]:
    return [w3.eth.account.privateKeyToAccount(private_key) for private_key in private_keys]


def send_tx(w3: Web3, account: Account, contract_address, data) -> str:
    nonce = w3.eth.get_transaction_count(account.address, "pending")

    tx = {
        "nonce": nonce,
        "chainId": w3.eth.chain_id,
        "to": contract_address,
        "from": account.address,
        "value": 0,
        "gas": 100_000,
        "gasPrice": w3.eth.gas_price,
        "data": data
    }

    gas = w3.eth.estimate_gas(tx)

    if gas > tx["gas"]:
        tx["gas"] = gas

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

    logger.info("Initializing accounts...")
    try:
        accounts = init_accounts(w3, private_keys)
    except Exception as e:
        logger.error(f"Error initializing accounts: {e}")
        return

    for account in accounts:
        try:
            tx_hash = send_tx(w3, account, BOOMLAND_CONTRACT, BOOMLAND_CLAIM_DATA)
            logger.success(f"Sent tx from {account.address} with {tx_hash=}")
        except ContractLogicError as e:
            logger.warning(f"Error simulate tx from {account.address}: {e}. Maybe, claim for this address unavailable.")
        except Exception as e:
            logger.error(f"Error sending tx from {account.address}: {e}")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception as e:
        logger.error(e)
