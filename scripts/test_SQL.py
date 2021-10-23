import numpy as np
import pandas as pd
import pandas_datareader.data as web
from progressbar import progressbar as bar
from progressbar.bar import ProgressBar
from support.SQL_api import Database

if __name__ == "__main__":
    database = Database("/mnt/c/Users/Leonardo Cencetti/Desktop/test.db")

    exchange_data = pd.read_csv(
        "https://www.iso20022.org/sites/default/files/ISO10383_MIC/ISO10383_MIC.csv",
        encoding="iso-8859-1",
    )

    exchange_data = exchange_data[
        [
            "ISO COUNTRY CODE (ISO 3166)",
            "MIC",
            "NAME-INSTITUTION DESCRIPTION",
            "ACRONYM",
        ]
    ]
    exchange_data.rename(
        columns={
            "ISO COUNTRY CODE (ISO 3166)": "country_code",
            "MIC": "code",
            "NAME-INSTITUTION DESCRIPTION": "name",
            "ACRONYM": "acronym",
        },
        inplace=True,
    )

    exchange_data["id"] = exchange_data.index
    mapper = {"US": "USD", "GB": "GBP", "DE": "EUR"}
    exchange_data["currency"] = exchange_data["country_code"].map(mapper)
    database.insert(exchange_data[["id", "name", "currency", "code"]], "exchange")

    # scrape wiki table with symbols and details of Dow Jones constituents
    dj_constituents = pd.read_html(
        "https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average#Components"
    )[1]
    dj_constituents.rename(
        columns={"Company": "name", "Industry": "industry", "Symbol": "ticker"},
        inplace=True,
    )
    dj_constituents["ticker"] = dj_constituents["ticker"].apply(
        lambda x: x[::-1].partition(":")[0][::-1]
    )
    dj_constituents["ticker"] = dj_constituents["ticker"].str.strip()

    # scrape wiki table with symbols and details of s&P500 constituents
    sp_constituents = pd.read_html(
        "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    )[
        0
    ]  # .to_csv('constintuents_current.csv', index=False)
    sp_constituents.rename(
        columns={
            "Symbol": "ticker",
            "Security": "name",
            "Headquarters Location": "hq_location",
            "GICS Sector": "sector",
            "GICS Sub-Industry": "industry",
        },
        inplace=True,
    )

    company_table = pd.concat(
        [
            sp_constituents[["name", "industry", "sector", "hq_location"]],
            dj_constituents[["name", "industry"]],
        ]
    ).reset_index(drop=True)
    company_table.drop_duplicates(inplace=True)
    company_table.sort_values("name", inplace=True)
    company_table.reset_index(inplace=True, drop=True)
    company_table["id"] = company_table.index
    # security_table
    sp_security_table = sp_constituents[["ticker", "name"]].copy()

    dj_security_table = dj_constituents[["ticker", "name"]].copy()

    security_table = pd.concat([sp_security_table, dj_security_table]).reset_index(
        drop=True
    )
    security_table.drop_duplicates(subset="ticker", inplace=True)
    security_table.sort_values("ticker", inplace=True)
    security_table.reset_index(inplace=True, drop=True)
    security_table["id"] = security_table.index

    company_id_mapper = pd.Series(
        company_table.id.values, index=company_table.name
    ).to_dict()
    security_table["company_id"] = security_table["name"].map(company_id_mapper)

    security_id_mapper = pd.Series(
        security_table.id.values, index=security_table.name
    ).to_dict()
    company_table["security_id"] = company_table["name"].map(security_id_mapper)

    # load symbols from CSVs
    nyse = pd.read_csv("data/nyse.csv")
    nasdaq = pd.read_csv("data/nasdaq.csv")

    security_table["exchange_id"] = None
    security_table["exchange_id"] = np.where(
        security_table["ticker"].isin(nyse["Symbol"].values), 1300, ""
    )
    security_table["exchange_id"] = np.where(
        security_table["ticker"].isin(nasdaq["Symbol"].values),
        367,
        security_table["exchange_id"],
    )

    database.insert(security_table, "security")
    database.insert(company_table, "company")

    # download and store the price histories for each of our companies and tickers

    from threading import Thread
    from queue import Queue

    def handle_request(input_queue: Queue, data_queue: Queue, progress: bar):
        while not input_queue.empty():
            stock_id = input_queue.get()
            ticker = security_table.iloc[stock_id]["ticker"]
            print(f">>> Downloading data for {ticker}")
            try:
                stock_pricing_df = web.DataReader(
                    ticker,
                    start="2010-1-1",
                    data_source="yahoo",
                )
                stock_pricing_df["security_id"] = stock_id
                data_queue.put(stock_pricing_df)
                input_queue.task_done()
                progress.update(data_queue.qsize())
                print("<<< Done")
            except:
                print("!!! Error")

    iq = Queue()
    oq = Queue()
    pb = ProgressBar(max_value=len(security_table["id"]), redirect_stdout=True)
    T1 = Thread(target=handle_request, args=(iq, oq, pb), daemon=True)
    T2 = Thread(target=handle_request, args=(iq, oq, pb), daemon=True)
    T3 = Thread(target=handle_request, args=(iq, oq, pb), daemon=True)
    T4 = Thread(target=handle_request, args=(iq, oq, pb), daemon=True)
    T5 = Thread(target=handle_request, args=(iq, oq, pb), daemon=True)

    for stock_id in security_table["id"]:
        iq.put(stock_id)

    T1.start()
    T2.start()
    T3.start()
    T4.start()
    T5.start()

    T1.join()
    T2.join()
    T3.join()
    T4.join()
    T5.join()

    stock_pricing_dfs = list(oq.queue)
    security_price_table = pd.concat(stock_pricing_dfs)
    security_price_table.columns = [
        "high",
        "low",
        "open",
        "close",
        "volume",
        "adj_close",
        "security_id",
    ]

    security_price_table.reset_index(inplace=True)

    security_price_table["id"] = security_price_table.index

    database.insert(security_price_table, "security_price")

    database.connection.close()
