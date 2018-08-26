import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from G7 import *
import datetime
from Martingale import *

class MarketOnClosePortfolio(object):
    def __init__(self, currency, G7, positions, Strategy, signals=None,initial_capital=100000.0,interest_rate=0.02,trading_fees=0.002):
        self.currency = currency
        self.G7 = G7
        self.positions = positions
        if self.currency=='EURUSD' or self.currency=='USDJPY':
            self.basic_point =12.5
        elif self.currency=='GBPUSD':
            self.basic_point=6.25
        elif self.currency=='USDCAD' or self.currency=='AUDUSD'or self.currency=='NZDUSD':
            self.basic_point=10.0
        self.Strategy=Strategy
        # self.signals = signals
        self.initial_capital = float(initial_capital)
        self.interest_rate=interest_rate
        self.trading_fees=trading_fees
        self.portfolio=self.backtest_portfolio()

    def set_portfolio(self):
        print('Portfolio size: ')
        self.initial_capital=int(input())

    # def generate_positions(self):
    #     # Generate a pandas DataFrame to store quantity held at any “bar” timeframe
    #     positions = pd.DataFrame(index=self.bars.index)
    #     positions[self.symbol] = self.initial_capital/(float(self.bars['Adj Close'].head(1))) * self.signals['signal']
    #     return positions

    def backtest_portfolio(self):
        # Create a new DataFrame ‘portfolio’ to store the market value of an open position
        #portfolio = self.positions * self.bars['Adj Close']
        portfolio=pd.DataFrame()
        pos_diff = self.positions.diff()
        price=self.G7[(self.currency,'Rate')]
        currency_frame = price.to_frame()
        currency_frame.columns = ['Rate']
        currency_with_position = pd.DataFrame(
            {'%s'%self.currency: currency_frame['Rate'].values, 'position_mtg': self.positions['direction'].values},
            index=currency_frame.index)
        portfolio=pd.DataFrame({'%s'%self.currency: currency_frame['Rate'].values,
                                '%s_change'%self.currency:currency_frame['Rate'].diff().values,
                                'position':self.positions['direction'].values},
                               index=currency_frame.index)
        portfolio['pnl']=portfolio['%s_change'%self.currency]*10000*portfolio.position.shift(1)*self.basic_point
        portfolio['cumulative']=portfolio['pnl'].cumsum()+self.initial_capital
        portfolio['benchmark']=self.G7['USD']
        # EUR_change_position = pd.DataFrame(
        #     {'EURUSD_chg': EURUSD_frame['Rate'].diff().values, 'position': position_mar['direction'].values},
        #     index=EURUSD_frame.index)
        # EUR_change_position['pnl'] = EUR_change_position.EURUSD_chg * EUR_change_position.position.shift(1)
        #
        # portfolio['holdings'] = (self.positions[self.symbol] * self.bars['Adj Close'])
        # portfolio['cash'] = self.initial_capital - (pos_diff[self.symbol] * self.bars['Adj Close']).cumsum()
        # portfolio['trading fees']=pos_diff[self.symbol].abs() * self.bars['Adj Close'] *self.trading_fees
        # portfolio['overnight interests']=portfolio['cash']*self.interest_rate/365
        #
        # portfolio['total'] = portfolio['cash'] + portfolio['holdings']-portfolio['trading fees'].fillna(0.0)+portfolio['overnight interests']
        # portfolio['returns'] = portfolio['total'].pct_change()
        # portfolio['total'][0]=self.initial_capital
        # portfolio['benchmark']=self.benchmark
        return portfolio.drop(portfolio.head(1).index)

    def max_drawdown(self,vorp):
        if vorp.lower()=='v':
            i = np.argmax(self.portfolio['cumulative'].cummax() - self.portfolio['cumulative'])
            j = np.argmax(self.portfolio['cumulative'][:i])
            print('max value drawdown in value: ', self.portfolio['cumulative'][j] - self.portfolio['cumulative'][i])
            print('drawdown in percent: ',
                  (self.portfolio['cumulative'][j] - self.portfolio['cumulative'][i]) / self.portfolio['cumulative'][j] * 100, '%')
            plt.plot(self.portfolio['cumulative'])
            plt.plot([i, j], [self.portfolio['cumulative'][i], self.portfolio['cumulative'][j]], 'o', color='Blue', markersize=10)

        if vorp.lower()=='p':
            i = np.argmax((self.portfolio['cumulative'].cummax() - self.portfolio['cumulative'])/self.portfolio['cumulative'].cummax())  # end of the period
            j = np.argmax(self.portfolio['cumulative'][:i])  # start of period
            print('max percent drawdown in percent: ',
                  (self.portfolio['cumulative'][j] - self.portfolio['cumulative'][i]) / self.portfolio['cumulative'][j] * 100, '%')
            print('drawdown in value: ', self.portfolio['cumulative'][j] - self.portfolio['cumulative'][i])

            # plt.plot(self.portfolio['cumulative'])
            plt.plot([i, j], [self.portfolio['cumulative'][i], self.portfolio['cumulative'][j]], 'o', color='Blue', markersize=10)

    def draw(self):
        fig = plt.figure()
        fig.patch.set_facecolor('white')
        ax1 = fig.add_subplot(211, ylabel='Forex Rate')
        self.G7[(self.currency, 'Rate')].plot(ax=ax1, color='black', lw=2.)
        # self.signals[['short_mavg', 'long_mavg']].plot(ax=ax1, lw=1.)
        index_buy=self.portfolio.position>0
        index_sell=self.portfolio.position<0
        ax1.plot(self.G7.drop(self.G7.head(1).index).loc[index_buy].index,
                 self.G7.drop(self.G7.head(1).index)[(self.currency, 'Rate')].loc[index_buy],
                 '^', markersize=8, color='g', label='buy')
        ax1.plot(self.G7.drop(self.G7.head(1).index).loc[index_sell].index,
                 self.G7.drop(self.G7.head(1).index)[(self.currency, 'Rate')].loc[index_sell],
                 'v', markersize=8, color='r', label='sell')
        try:
            plt.title('Interval: %s \n Max Grid: %s'%(self.Strategy.interval, self.Strategy.maxRange))
        except:
            pass
        plt.legend()

        ax2 = fig.add_subplot(212, ylabel='Portfolio value in $')
        self.portfolio['cumulative'].plot(ax=ax2, lw=2.)
        # ax2.plot(self.portfolio.loc[self.signals.positions == 1.0].index,
        #          self.returns.total[self.signals.positions == 1.0],
        #          '^', markersize=10, color='g')
        ax2.plot(self.portfolio['cumulative'].index,self.portfolio['cumulative'],color='b',lw=2.0)

        # ax3=fig.add_subplot(313)
        # ax3.hist(self.portfolio.pnl, bins=100)

        fig.show()

