class Order:
    
    def __init__(self):
        self._queue = []
        
    def add(self, stock_code: str, quantity: int):
        # 매수: + quantity, 매도: - quantity
        self._queue.append((stock_code, quantity))
    
    def pop(self):
        # FIFO
        if self._queue:
            order = self._queue[0]
            self._queue = self._queue[1:]
            return order
        else:
            return None
        
    def __iter__(self):
        i = 0
        while i < len(self._queue):
            yield self._queue[i]
            i += 1
