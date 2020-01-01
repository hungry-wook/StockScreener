from context import Context
from order import Order


class TradingAlgorithm:

    # 트레이딩 로직
    def make_order(self, 
                   date,
                   market_data, # pandas dataframe
                   cash: float,
                   holding_stocks: dict,
                   context: Context):
        
        order = Order()
        
#         if market_data[date:date-3] TODO: 특정 주식의 최근 N일간 가격 정보를 가져오는 인터페이스

# 특정 조건을 만족하는 종목 가져오는 함수

        order.add(stock_code, 3)
        
        # Implement Trading Logic Here!
        

        return order