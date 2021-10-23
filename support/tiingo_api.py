###
# File created by Leonardo Cencetti on 2/8/21
###
from datetime import datetime

from tiingo import TiingoClient

from support.alpha_vantage_api import AVReply, RequestType, Interval, SeriesType


def get_intraday(symbol, key, interval="1Min", outputsize="compact"):
    config = {
        # 'api_key': key_generator(),
        "api_key": key,
        "session": False,  # Reuse HTTP sessions across API calls for better performance
    }
    client = TiingoClient(config)
    data = client.get_dataframe(
        symbol,
        startDate="2021-02-01",
        endDate=datetime.now().strftime("%Y-%m-%d"),
        frequency="1Min",
        fmt="csv",
    )
    # reverse order (intraday is returned in descendent order
    # data = data[::-1]
    return AVReply(
        type=RequestType("full_intraday"),
        interval=Interval("1min"),
        symbol=symbol,
        series=SeriesType.ALL,
        data=data,
        timezone=None,
    )
