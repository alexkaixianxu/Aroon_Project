import numpy as np
import pandas as pd
import quandl
import datetime
quandl.ApiConfig.api_key = '8qNu5k13WLNT-6tRKj9M'

def data_download(start='2007-01-01',end=datetime.date.today()):
    frame_ticker = ['EURUSD', 'EURUSD', 'EURUSD', 'USDJPY', 'USDJPY', 'USDJPY', 'GBPUSD', 'GBPUSD', 'GBPUSD', 'USDCAD',
                    'USDCAD', 'USDCAD', 'AUDUSD', 'AUDUSD', 'AUDUSD', 'NZDUSD', 'NZDUSD', 'NZDUSD']
    ohlc = ['Rate', 'High (est)', 'Low (est)']
    G7 = pd.DataFrame(columns=[frame_ticker, ohlc * 6])
    for ticker, x in zip(frame_ticker, ohlc * 6):
        G7[(ticker, x)] = quandl.get('CURRFX/{}'.format(ticker), start_date=start, end_date=end)[x]
    usd_index=quandl.get('FRED/DTWEXM', start_date=start,end_date=G7.tail(1).index)
    G7['USD']=usd_index
    return G7.dropna(axis=0)
