###
# File created by Leonardo Cencetti on 2/6/21
###
from datetime import datetime
from time import sleep
import os


from support.SQL_api import Database
from binance.client import Client as Binance
from dotenv import load_dotenv
import pandas as pd


targets = ["BTC", "BNB", "ETH", "EUR"]

currencies = ['EUR', 'USD', 'CHF']
class Dashboard:
    def __init__(self) -> None:
        # initialize database connection
        self.database = Database("/mnt/c/Users/Leonardo Cencetti/Desktop/binance.db")
        # initialize Binance API
        self.binance = Binance(
            os.getenv("BINANCE_API_TOKEN"), os.getenv("BINANCE_API_SECRET")
        )
        self.currency = "EUR"

    def fetch_binance(self):
        account_data = self.binance.get_account()
        portfolio = []
        # for entry in account_data["balances"]:
        balances = pd.DataFrame(account_data["balances"])
        non_zero = balances.loc[balances[['free', 'locked']].astype(float).sum(axis=1) != 0]
        
        for ticker in non_zero['asset']:
            if ticker in currencies:
                data = dict(price = 1)
            else:
                data = self.binance.get_symbol_ticker(symbol=ticker + self.currency)
            asset = self.binance.get_asset_balance(ticker)
            portfolio.append(
                dict(
                    timestamp=datetime.now(),
                    name=ticker,
                    quantity=float(asset["free"]) + float(asset["locked"]),
                    value=(float(asset["free"]) + float(asset["locked"]))
                    * float(data["price"]),
                )
            )
        
        portfolio = pd.DataFrame(portfolio)

        self.database.insert(portfolio, "portfolio")

    def run(self):
        while True:
            self.fetch_binance()
            sleep(10)


if __name__ == "__main__":
    load_dotenv("keys/.env")
    dashboard = Dashboard()
    dashboard.run()
