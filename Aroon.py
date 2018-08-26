import pandas as pd
import numpy as np

def Aroon(prices, freq='M', U=70, D=30):
    stat = pd.DataFrame()
    stat['mH'] = prices.resample(freq, how='max')
    stat['mL'] = prices.resample(freq, how='min')
    stat['mU'] = (prices.diff() > 0).resample(freq, how='sum')
    stat['mD'] = (prices.diff() < 0).resample(freq, how='sum')
    # stat['#d']=EURUSD.resample('M',how='count')
    stat['#d'] = stat['mU'] + stat['mD']
    stat['dateH'] = pd.to_datetime(prices.groupby(pd.TimeGrouper(freq=freq)).apply(np.argmax))
    stat['dateL'] = pd.to_datetime(prices.groupby(pd.TimeGrouper(freq=freq)).apply(np.argmin))
    stat['firstdate'] = pd.to_datetime(prices.groupby(pd.TimeGrouper(freq=freq)).head(1).index)
    stat['lastdate'] = pd.to_datetime(prices.groupby(pd.TimeGrouper(freq=freq)).tail(1).index)

    stat['HtoLast'] = np.nan
    for i in range(len(stat)):
        stat['HtoLast'][i] = np.busday_count(stat['dateH'][i], stat['lastdate'][i])
    stat['LtoLast'] = np.nan
    for i in range(len(stat)):
        stat['LtoLast'][i] = np.busday_count(stat['dateL'][i], stat['lastdate'][i])

    stat['ARON_U'] = (stat['#d'] - stat['HtoLast']) / stat['#d'] * 100
    stat['ARON_D'] = (stat['#d'] - stat['LtoLast']) / stat['#d'] * 100
    stat['ARON'] = stat['ARON_U'] - stat['ARON_D']

    stat['trend'] = np.nan
    # stat['trend'][(stat['ARON'] > 0) & (stat['ARON_U'] > 70) & (stat['ARON_D'] < 30)] = 1
    # stat['trend'][(stat['ARON'] < 0) & (stat['ARON_D'] > 70) & (stat['ARON_U'] < 30)] = -1
    # stat['trend'] = stat['trend'].fillna(0)
    stat['trend']=np.where(((stat['ARON']>0) & (stat['ARON_U']>U) & (stat['ARON_D']<D)),1,
                           np.where(((stat['ARON'] < 0) & (stat['ARON_D'] > U) & (stat['ARON_U'] < D)), -1, 0))


    def last_first(df):
        return (df[-1] - df[0]) / df[0]

    stat['mChange'] = prices.groupby(pd.TimeGrouper(freq=freq)).apply(last_first)
    stat['std'] = prices.groupby(pd.TimeGrouper(freq=freq)).apply(np.std)
    return stat