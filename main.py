import requests
from web3 import Web3
import os
import dotenv

dotenv.load_dotenv()

node_url = "https://arb1.arbitrum.io/rpc"
privateKey = os.getenv("PRIVATE_KEY")

w3 = Web3(Web3.HTTPProvider(node_url))

account = w3.eth.account.from_key(privateKey)
usdt = "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9"
usdc = "0xaf88d065e77c8cC2239327C5EDb3A432268e5831"
arb = "0x912CE59144191C1204E64559FE8253a0e49E6548"
chain_id = w3.eth.chain_id
amount_in = 1 * 10**18


class EnsoFinance:
    base_url: str = "https://api.enso.finance/api/v1"
    key: str = "1e02632d-6feb-4a75-a157-documentation"
    url: str = "https://api.enso.finance/api/v1/shortcuts/bundle"

    def account_wallet(self, address, chain_id):
        url = f"{self.base_url}/wallet?chainId={chain_id}&fromAddress={address}"
        res = requests.get(url)

        if res.status_code != 200:
            print(res.json()["message"])
            raise ValueError("Unable to get account wallet")
        data = res.json()
        return data

    def approve(self, chain_id, account, token_address, amount):
        params = {
            "chainId": chain_id,
            "fromAddress": account.address,
            "tokenAddress": token_address,
            "amount": amount,
        }

        url = self.base_url + "/wallet/approve"
        res = requests.get(url, params=params)
        if res.status_code != 200:
            raise ValueError(res.json()["message"])

        trx = res.json()["tx"]
        trx["value"] = int(trx.get("value", 0))
        trx["gas"] = 100000000000
        trx["gasPrice"] = w3.eth.gas_price
        nonce = w3.eth.get_transaction_count(account.address)
        trx["nonce"] = nonce

        try:
            gas = w3.eth.estimate_gas(trx)
        except Exception as e:
            raise ValueError("Failed to estimate gas for approve transaction")

        trx["gas"] = gas
        tnx = w3.eth.account.sign_transaction(trx, privateKey)
        res = w3.eth.send_raw_transaction(tnx.rawTransaction)
        w3.eth.wait_for_transaction_receipt(res)
        return True

    def swap_one(self, chain_id, account, token_in, amount, token_out):
        self.approve(chain_id, account, token_in, amount)
        _url = f"{self.base_url}/shortcuts/route"
        print(account.address)
        print(self.key)
        print(chain_id)
        params = {
            "chainId": chain_id,
            "fromAddress": account.address,
            "slippage": 300,
            "tokenIn": token_in,
            "tokenOut": token_out,
            "amountIn": amount,
            "tokenInAmountToApprove": amount,
            "toEoa": True,
        }

        res = requests.get(
            _url,
            params=params,
            headers={"Authorization": f"Bearer {self.key}"},
        )

        if res.status_code != 200:
            raise ValueError(res.json()["message"])

        data = res.json()
        trx = data["tx"]
        trx["value"] = int(trx["value"])
        trx["gas"] = 5500000000
        trx["gasPrice"] = w3.eth.gas_price
        nonce = w3.eth.get_transaction_count(account.address)
        trx["nonce"] = nonce

        try:
            gas = w3.eth.estimate_gas(trx)
        except Exception as e:
            raise ValueError("Failed to estimate gas for transaction ")

        trx["gas"] = gas
        tnx = w3.eth.account.sign_transaction(trx, privateKey)
        res = w3.eth.send_raw_transaction(tnx.rawTransaction)
        print(f"Swap done: trx hash: {res.hex()}")


enso = EnsoFinance()
enso.swap_one(chain_id, account, arb, amount_in, usdt)
