from tqdm import tqdm
from algo_trading.market_data import MarketData
from algo_trading.context import Context
from algo_trading.logger import Logger
from algo_trading.order import Order
from algo_trading.trading_algorithm import TradingAlgorithm


class BackTester:

    def __init__(self, 
                 market_data: MarketData,
                 initial_cash: float,
                 start_date=None, # YYYY-MM-DD
                 end_date=None, # YYYY-MM-DD
                 commission_buy=0.0,
                 commission_sell=0.033,
                 benchmark_symbol='KS11'):

        ##### 테스트 데이터 (전체 기간) #####
        self.market_data = market_data
        
        ##### 현금 / 보유 주식 #####
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.holding_stocks = dict() # 보유중인 주식. key:주식코드, value:보유한 주 개수

        ##### 테스트 기간 #####
        if not start_date:
            start_date = market_data.trading_days[0]
        if not end_date:
            end_date = market_data.trading_days[-1]
        self.trading_days = [d for d in market_data.trading_days if start_date <= d <= end_date]

        ##### 수수료 설정 #####
        self.commission_buy = commission_buy # 퍼센트 수수료
        self.commission_sell = commission_sell # 퍼센트 수수료

        ##### 컨텍스트 변수 #####
        self.context = Context() # TradingAlgorithm이 read/write 할 수 있는 컨텍스트 정보

        ##### Order Log #####
        self.logger = Logger()

        ##### 벤치마킹 대상 #####
        self.benchmark_symbol = benchmark_symbol

        #### 테스트 결과 #####
        self.result = dict()

    def run(self, trading_algo: TradingAlgorithm):

        self._init()

        for date in tqdm(self.trading_days):

            order = trading_algo.run(date, self.market_data, self.context)

            # 주문 처리. 매수 / 매도 가능한지 확인 후 처리함. 성공/실패 내역은 logger에 기록
            self._handle_order(order, date)

            # 현재 자산(현금, 보유 주식)을 context에 기록
            self._record_asset(date)

        result = self._evaluate_performance()

        return result

    def _init(self):
        self.cash = self.initial_cash
        self.holding_stocks.clear()
        self.context.clear()
        self.logger.clear()
        self.result.clear()

    def _handle_order(self, order: Order, date):

        for symbol, quantity in order:

            # Price unavailable
            try:
                price = self.market_data[date, symbol].Close # 종가
            except:
                self.logger.info('[fail(2)]:({},{},{})'.format(date, symbol, quantity))
                continue

            # sell
            if quantity < 0: 

                # 보유 주식량 >= 매도량인지 체크
                if self.holding_stocks.get(symbol, 0) >= (-quantity):
                    self.cash += (-quantity) * price * (1 - self.commission_sell)
                    self.holding_stocks[symbol] += quantity                    
                    self.logger.info('[success(0)]:({},{},{})'.format(date, symbol, quantity))

                else:
                    self.logger.info('[fail(1)]:({},{},{})'.format(date, symbol, quantity))

            # buy
            else:

                # 매수 가능한 현금이 있는지 체크
                if self.cash >= quantity * price * (1 + self.commission_buy):

                    self.cash -= quantity * price * (1 + self.commission_buy)

                    if symbol not in self.holding_stocks:
                        self.holding_stocks[symbol] = 0
                    self.holding_stocks[symbol] += quantity
                    self.logger.info('[success(0)]:({},{},{})'.format(date, symbol, quantity))

                else:
                    self.logger.info('[fail(1)]:({},{},{})'.format(date, symbol, quantity))

    def _record_asset(self, date):
        self.context.record_asset(date, self.cash, self.holding_stocks)

    def _evaluate_performance(self):

        result = dict()
        portfolio_value = 0

        # TODO: 포트폴리오 가치 변화를 일별로 볼 수 있게. 변동성도
        for symbol, quantity in self.holding_stocks.items():
            price = self.market_data[self.trading_days[-1], symbol].Close # 종가
            portfolio_value += quantity * price * (1 - self.commission_sell)

        # 포트폴리오 수익률
        portfolio_value += self.cash
        portfolio_return = (portfolio_value - self.initial_cash) / self.initial_cash
        result['return'] = portfolio_return

        # 벤치마크 수익률
        benchmark_initial_value = self.market_data[self.trading_days[0], self.benchmark_symbol].Close
        benchmark_end_value = self.market_data[self.trading_days[-1], self.benchmark_symbol].Close
        benchmark_return = (benchmark_end_value - benchmark_initial_value) / benchmark_initial_value

        # 조정 수익률 = 포트폴리오 수익률 - 벤치마크 수익률
        result['adjusted_return'] = portfolio_return - benchmark_return
        return result
