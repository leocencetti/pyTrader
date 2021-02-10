###
# File created by Leonardo Cencetti on 2/8/21
###
from datetime import datetime

import degiroapi
from degiroapi.utils import pretty_json

if __name__ == '__main__':
    degiro = degiroapi.DeGiro()
    degiro.login(auth2fa=True)

    cashfunds = degiro.getdata(degiroapi.Data.Type.CASHFUNDS)
    for data in cashfunds:
        print(data)

    portfolio = degiro.getdata(degiroapi.Data.Type.PORTFOLIO, True)
    for data in portfolio:
        print(data)

    transactions = degiro.transactions(datetime(2019, 1, 1), datetime.now())
    print(pretty_json(transactions))

    degiro.logout()
