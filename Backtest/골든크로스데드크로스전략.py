# Backtrader 라이브러리를 사용.
# yfinance 모듈을 사용하여 주가 데이터를 불러온다.
# 5일 이동평균선이 30일 이동평균선을 초과할 때 매수.
# 5일 이동평균선이 30일 이동평균선을 뚫고 내려갈 때 매도.

from datetime import datetime
import backtrader as bt
import locale
import yfinance as yf


locale.setlocale(locale.LC_ALL, 'ko_KR')

# Create a subclass of Strategy to define the indicators and logic
class SmaCross(bt.Strategy):
    # list of parameters which are configurable for the strategy
    params = dict(
        pfast=5,  # period for the fast moving average
        pslow=30  # period for the slow moving average
    )

    def __init__(self):
        sma1 = bt.ind.SMA(period=self.p.pfast)  # fast moving average
        sma2 = bt.ind.SMA(period=self.p.pslow)  # slow moving average
        self.crossover = bt.ind.CrossOver(sma1, sma2)  # crossover signal

        self.holding = 0

    def next(self):
        current_stock_price = self.data.close[0]

        if not self.position:  # not in the market
            if self.crossover > 0:  # if fast crosses slow to the upside
                available_stocks = self.broker.getcash() / current_stock_price
                self.buy(size=1)

        elif self.crossover < 0:  # in the market & cross to the downside
            self.close()  # close long position

    def notify_order(self, order):
        if order.status not in [order.Completed]:
            return

        if order.isbuy():
            action = 'Buy'
        elif order.issell():
            action = 'Sell'

        stock_price = self.data.close[0]
        cash = self.broker.getcash()
        value = self.broker.getvalue()
        self.holding += order.size

        print('%s[%d] holding[%d] price[%d] cash[%.2f] value[%.2f]'
              % (action, abs(order.size), self.holding, stock_price, cash, value))

cerebro = bt.Cerebro()  # create a "Cerebro" engine instance
cerebro.broker.setcash(100000)
cerebro.broker.setcommission(0.002)

# Create a data feed
# data = bt.feeds.YahooFinanceData(dataname='005930.KS',
#                                 fromdate=datetime(2019, 1, 1),
#                                 todate=datetime.now())

#data = bt.feeds.PandasData(dataname=yf.download('TSLA', '2022-1-1', '2022-5-28'))
data = bt.feeds.PandasData(dataname=yf.download('005930.KS', '2020-3-1', '2022-5-28'))

cerebro.adddata(data)  # Add the data feed

cerebro.addstrategy(SmaCross)  # Add the trading strategy

start_value = cerebro.broker.getvalue()
cerebro.run()  # run it all
final_value = cerebro.broker.getvalue()

print('* start value : %s won' % locale.format_string('%d', start_value, grouping=True))
print('* final value : %s won' % locale.format_string('%d', final_value, grouping=True))
print('* earning rate : %.2f %%' % ((final_value - start_value) / start_value * 100.0))

cerebro.plot()  # and plot it with a single command
