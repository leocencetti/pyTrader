from dotenv import load_dotenv
import os
from binance.client import Client
from dotenv import load_dotenv



class Binance:
    def __init__(self, api_key: str, api_secret: str) -> None:
        self.key = api_key
        self.secret = api_secret
        self._client = Client(self.key, self.secret)

    def get_account_data(self):
        data = self._client.get_account()
        return data

    def get_asset_balance(self, asset: str):
        data = self._client.get_asset_balance(asset)
        return data


if __name__ == "__main__":
    load_dotenv("keys/.env")
    binance = Binance(os.getenv("BINANCE_API_TOKEN"), os.getenv("BINANCE_API_SECRET"))
    print(binance.get_account_data())
    print(binance.get_asset_balance("BTC"))
