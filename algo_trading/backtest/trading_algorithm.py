import pandas as pd
from abc import ABC, abstractmethod
from algo_trading.backtest.context import Context
from algo_trading.backtest.order import Order
from algo_trading.backtest.market_data import MarketData


class TradingAlgorithm(ABC):

    def run(self,
            date: str, # YYYY-MM-DD
            market_data: MarketData,
            context: Context) -> Order:

        order = Order()
        order = self.make_order(order, date, market_data, context)

        return order

    @abstractmethod
    def make_order(self,
                   order: Order,
                   date,
                   market_data: MarketData,
                   context: Context) -> Order:
        pass
