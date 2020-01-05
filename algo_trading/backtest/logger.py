class Logger:
    
    # TODO: use logging module
    
    def __init__(self):
        self.order_log = []
        
    def info(self, log):
        """
        - success code: 0
        - fail code
            - 1: 매도의 경우 (보유 주식 < 매도량)인 경우. 매수의 경우 (구매가 > 보유현금)인 경우
            - 2: 거래일에 주문한 종목의 가격정보가 없는 경우
        """
        self.order_log.append(log)

    def clear(self):
        self.order_log.clear()
