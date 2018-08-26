import pandas as pd
import numpy as np
import datetime

class Martingale(object):
    def __init__(self, G7, currency, start='2007/01/01', end=str(datetime.date.today()), interval=0.002, maxRange=30 ):
        self.G7=G7
        self.currency=currency
        self.start=start
        self.end=end
        self.df=G7[(self.currency,'Rate')][self.start:self.end]
        self.interval=interval
        self.maxRange=maxRange


    def position_mtg(self):
        position = pd.DataFrame(columns=['direction'])
        position.loc[0, 'direction'] = 0
        entry_price=self.df[0]

        def set_triger(entry_price, interval, maxRange):
            triger = pd.DataFrame()
            for i in range(maxRange):
                triger.loc[i, 'Sell'] = entry_price + interval * i
                triger.loc[i, 'Buy'] = entry_price - interval * i
            return triger

        entry_price = self.df[0]
        triger = set_triger(entry_price, self.interval, self.maxRange)

        for i in range(1, len(self.df)):
            if self.df[i] > entry_price:
                if self.df[i] >= self.df[i - 1]:
                    index = np.argmin(self.df[i] - triger['Sell'][(self.df[i] - triger.Sell) > 0])
                    if index != 0:
                        position.loc[i, 'direction'] = -(2 ** index - 1)
                    else:
                        position.loc[i, 'direction'] = np.nan
                else:
                    if np.argmin(self.df[i] - triger['Sell'][(self.df[i] - triger.Sell) > 0]) < (
                        np.argmin(self.df[i - 1] - triger['Sell'][(self.df[i - 1] - triger.Sell) > 0]) + 1):
                        position.loc[i, 'direction'] = 0
                        entry_price = self.df[i]
                        triger = set_triger(entry_price, self.interval, self.maxRange)
            elif self.df[i] < entry_price:
                if self.df[i] <= self.df[i - 1]:
                    index = np.argmin(triger['Buy'][(triger.Buy - self.df[i]) > 0] - self.df[i])
                    if index != 0:
                        position.loc[i, 'direction'] = (2 ** index - 1)
                    else:
                        position.loc[i, 'direction'] = np.nan
                else:
                    if np.argmin(triger['Buy'][(triger.Buy - self.df[i]) > 0] - self.df[i]) < (
                        np.argmin(triger['Buy'][(triger.Buy - self.df[i - 1]) > 0] - self.df[i - 1]) + 1):
                        position.loc[i, 'direction'] = 0
                        entry_price = self.df[i]
                        triger = set_triger(entry_price, self.interval, self.maxRange)
            else:
                position.loc[i, 'direction'] = np.nan
        self.position = position.fillna(method='ffill')
        return self.position
