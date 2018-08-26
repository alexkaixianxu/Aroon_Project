import pandas as pd
import numpy as np
from Martingale import *
from Backtest import *
from G7 import *
import quandl
from scipy.stats import norm
quandl.ApiConfig.api_key = '8qNu5k13WLNT-6tRKj9M'
import sys

if __name__=='main':
    print('The default date range is [Jan/1/2007 ~ today], set another date range? y/n \n Loading data may take a while')
    if input().lower() == 'y':
        print('New date range (YYYY-MM-DD, YYYY-MM-DD): ')
        start, end = input().split(',')
        nofyears = (datetime.datetime.strptime(end, '%Y-%m-%d') - datetime.datetime.strptime(start,
                                                                                             '%Y-%m-%d')).days / 365
    else:
        start,end='2007-1-1',str(datetime.date.today())
        nofyears = (datetime.datetime.strptime(end, '%Y-%m-%d') - datetime.datetime.strptime(start,
                                                                                             '%Y-%m-%d')).days / 365

    G7=data_download(start,end)

    print('Currency you want to backtest: ')
    currency = input().upper()
    while currency not in ['EURUSD','GBPUSD','USDCAD','USDJPY','AUDUSD','NZDUSD']:
        print('Not G7 currency! Try again.')
        currency = input().upper()

    print('Portfolio capital (default=1,000,000): ')
    initial_capital=input()
    if initial_capital=='':
        initial_capital=1000000.0
    else:
        initial_capital=float(initial_capital)


    print('Select strategy you would like to backtest:\n 1. Martingale')
    if input()=='1':
        print('Set interval (in number of pip): ')
        if currency=='USDJPY':
            interval=int(input())/100
        else:
            interval=int(input())/10000

        print('Set max number of grids: ')
        maxRange=int(input())

        strategy = Martingale(G7, currency, start=start, end= end,interval=interval, maxRange=maxRange)
        position = strategy.position_mtg()
        portfolio_class = MarketOnClosePortfolio(currency, G7, position, Strategy=strategy,initial_capital=initial_capital)
        portfolio = portfolio_class.backtest_portfolio()


    print('Show max drawdow? y/n')
    yn=input()
    if yn.lower()=='y':
        portfolio_class.draw()


        print('In terms of value or percent? v/p')
        vorp=input()
        portfolio_class.max_drawdown(vorp)
    else:
        portfolio_class.draw()


    print ('Report Risk Metrics? y/n')
    if input().lower()=='y':
        p1=int(np.floor(len(portfolio)*0.01))
        if p1==0:
            p1=1
        p5=int(np.floor(len(portfolio)*0.05))
        p10=int(np.floor(len(portfolio)*0.1))

        Total_returns=(portfolio['cumulative'][len(portfolio)-1]-initial_capital)/initial_capital
        annualized_return=(1+Total_returns)**(1/nofyears)-1

        pnl=portfolio.pnl
        Mean=pnl.mean()
        Var=pnl.var()
        Vol=portfolio['cumulative'].pct_change().std()
        Std=pnl.std()
        i = np.argmax((portfolio['cumulative'].cummax() - portfolio['cumulative']) / portfolio['cumulative'].cummax())
        j = np.argmax(portfolio['cumulative'][:i])

        Benchmark_return=(portfolio['benchmark'][len(portfolio)-1]-portfolio['benchmark'][0])/portfolio['benchmark'][0]
        pnl_benchmark=portfolio['benchmark']-portfolio['benchmark'].shift(1)
        benchmark_pct=portfolio['benchmark'].pct_change()

        print(48 * '-')
        print('%24s %22s' % ('Forx Pair:', portfolio_class.currency))
        print('%24s %22s' % ('Initial Capital: ', "{:,}".format(initial_capital)))
        print('%24s %22s' % ('Benchmark: ', 'Fred/Weighted US Dollar Index'))
        print(48*'-')
        print('%24s %20s'%('Risk Measures','Value'))
        print(48*'-')
        print('%24s %20.2f' % ('Total Return',Total_returns *100),'%')
        print('%24s %20.2f' % ('Annualized Return', annualized_return*100),'%')
        print('%24s %20.2f' % ('Benchmark Return', Benchmark_return * 100), '%')
        print('%24s %20.2f' % ('Volatility', Vol*100),'%')
        print('%24s %20.2f' % ('VaR-99%', sorted(pnl)[p1-1]))
        print('%24s %20.2f' % ('VaR-95%', sorted(pnl)[p5-1]))
        print('%24s %20.2f' % ('VaR-90%', sorted(pnl)[p10-1]))
        print('%24s %20.2f' % ('Expected Shortfall-5%',sum(sorted(pnl.dropna())[:p5])/p5))
        #print('%20s %20.2f' % ('VaR-99%', abs(Mean - 2.33 * Std)))
        #print('%20s %20.2f' % ('VaR-95%', abs(Mean - 1.645 * Std)))
        #print('%20s %20.2f' % ('VaR-90%', abs(Mean - 1.282 * Std)))
        print('%24s %20.2f' % ('Sharpe', (annualized_return-0.03)/(portfolio['cumulative'].pct_change().std()*np.sqrt(1/nofyears))))
        print('%24s %20.2f' % ('Information Ratio',
                               (Total_returns-Benchmark_return) / ((portfolio['cumulative'].pct_change()-benchmark_pct).std()*np.sqrt(1/nofyears))))
        print('%24s %20.2f' % ('Max Drawdown',
                               (portfolio['cumulative'][j] - portfolio['cumulative'][i]) / portfolio['cumulative'][j] *100),'%')
        #print('%14s %14.3f' % ('Information Ratio', (Total_returns - 0.02) / Std))
        print(48 * '-')

