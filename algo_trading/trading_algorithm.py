import pandas as pd
from abc import ABC, abstractmethod
from algo_trading.context import Context
from algo_trading.order import Order


class TradingAlgorithm(ABC):

    def run(self,
            market_data: pd.DataFrame,
            context: Context) -> Order:

        order = Order()
        order = self.make_order(order, market_data, context)
        return order

    @abstractmethod
    def make_order(self,
                   order: Order,
                   market_data: pd.DataFrame,
                   context: Context) -> Order:
        pass
