class Logger:
    
    def __init__(self):
        self.order_log = []
        
    def order(self, date, stock_code, price, quantity, cash_after_order, is_success):
        log = 'date={}|stock_code={}|price={}|quantity={}|cash_after_order={}|is_success={}'.format(date, stock_code, price, quantity, cash_after_order, is_success)
        self.order_log.append(log)
        
    def clear(self):
        self.order_log.clear()
