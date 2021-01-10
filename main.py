# источник: https://forum.goodservice.su/threads/%D0%98%D0%BC%D0%BF%D0%BE%D1%80%D1%82-%D0%BF%D0%BE%D0%BB%D0%BD%D0%BE%D0%B9-%D0%B8%D0%BD%D1%84%D0%BE%D1%80%D0%BC%D0%B0%D1%86%D0%B8%D0%B8-%D0%BF%D0%BE-%D0%BB%D1%8E%D0%B1%D0%BE%D0%B9-%D0%BA%D1%80%D0%B8%D0%BF%D1%82%D0%BE%D0%B2%D0%B0%D0%BB%D1%8E%D1%82%D0%B5-%D1%81-binance-%D0%B8-bitmex-%D0%B8%D1%81%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D1%83%D1%8F-api-python.8911/
# IMPORTS
import pandas as pd
import math
import os.path
import time
from binance.client import Client
from datetime import timedelta, datetime
from dateutil import parser
#from tqdm import tqdm_notebook  # (Optional, used for progress-bars)

### API
binanceApiKey = 'eM5XndcOvPOYaeuH62pQVBBa4QhKsxDbolR0eMPDrEBWrP1YCdbgTZ774mT0ZAYR'  # Enter your own API-key here
binanceApiSecret = 'uEgTORCoB8pWcSXzro3xUKcxxroeunq4GMEbqfSRhOix91mGxE5WUbymz3hFBeXG'  # Enter your own API-secret here

### CONSTANTS
binSizes = {"1m": 1, "5m": 5, "1h": 60, "1d": 1440}
binanceClient = Client(api_key=binanceApiKey, api_secret=binanceApiSecret)
startDate = '1 Jun 2018'


### FUNCTIONS
def minutesOfNewData(symbol, klineSize, data):
    if len(data) > 0:
        old = parser.parse(data["timestamp"].iloc[-1]) + timedelta(minutes=binSizes[klineSize])
    else:
        old = datetime.strptime(startDate, '%d %b %Y')
    new = pd.to_datetime(binanceClient.get_klines(symbol=symbol, interval=klineSize)[-1][0], unit='ms')
    return old, new


def getAllBinance(symbol, klineSize, save=False):
    fileName = '%s-%s.csv' % (symbol, klineSize)
    if os.path.isfile(fileName):
        dataDf = pd.read_csv(fileName)
    else:
        dataDf = pd.DataFrame()
    oldestPoint, newestPoint = minutesOfNewData(symbol, klineSize, dataDf)
    deltaMin = (newestPoint - oldestPoint + timedelta(minutes=binSizes[klineSize])).total_seconds() / 60
    availableData = math.ceil(deltaMin / binSizes[klineSize])
    if oldestPoint == datetime.strptime(startDate, '%d %b %Y'):
        print('Downloading all available %s data for %s. Be patient..!' % (klineSize, symbol))
    else:
        print('Downloading %d minutes of new data available for %s, i.e. %d instances of %s data.' % (
            deltaMin, symbol, availableData, klineSize))
    klines = binanceClient.get_historical_klines(symbol, klineSize, oldestPoint.strftime("%d %b %Y %H:%M:%S"),
                                                 newestPoint.strftime("%d %b %Y %H:%M:%S"))
    data = pd.DataFrame(klines,
                        columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av',
                                 'trades', 'tb_base_av', 'tb_quote_av', 'ignore'])
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
    #data.drop(columns=['quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore'], inplace=True)
    if len(dataDf) > 0:
        tempDf = pd.DataFrame(data)
        dataDf = dataDf.append(tempDf)
    else:
        dataDf = data
    dataDf.set_index('timestamp', inplace=True)
    if save:
        dataDf.to_csv(fileName)
    print('Downloaded %d rows of %s!' % (dataDf['open'].count(), symbol))
    return dataDf


simbols = ["BTCUSDT", "XRPBTC", "XRPUSDT", "ETHUSDT", "ETHBTC", "EOSUSDT", "EOSBTC", "LTCBTC", "LTCUSDT", "BNBUSDT", "BNBBTC"]
for simbol in simbols:
    data = getAllBinance(simbol, '1h', save = True)