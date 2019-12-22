class Context:
    
    def __init__(self):
        self._asset_by_date = dict()
        self._custom_data = dict()

    @property
    # 일자별 보유 자산에 대해 기록하는 변수. 알고리즘의 Return 계산에 활용된다
    # 외부에서 해당 property 접근 시에는 read-only
    def asset_by_date(self):
        return self._asset_by_date
    
    def record_asset(self, date, cash, holding_stocks:dict):
        self._asset_by_date[date] = {
            'cash': cash,
            'holding_stocks': holding_stocks
        }        
    
    ##### custom_data에 대한 operation #####
    def get(self, key):
        if key not in self._custom_data:
            raise ValueError('key:{} does not exist in context!'.format(key))
        return self._custom_data[key]

    def add(self, key, val):
        if key in self._custom_data:
            raise ValueError('key:{} already exists in context!'.format(key))
        self._custom_data[key] = val

    def update(self, key, val):
        if key not in self._custom_data:
            raise ValueError('key:{} does not exist in context!'.format(key))
        self._custom_data[key] = val

    def delete(self, key):
        if key not in self._custom_data:
            raise ValueError('key:{} does not exist in context!'.format(key))    
        del self._custom_data[key]
    ######################################
