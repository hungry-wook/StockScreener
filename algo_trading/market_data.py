import os
import pandas as pd
from glob import glob
from tqdm import tqdm


class MarketData:
    
    def __init__(self, data_path):
        self.data, self.trading_days = self._load_data(data_path)
        self._trading_days_to_idx = {d:i for i,d in enumerate(self.trading_days)}

    def _load_data(self, data_path):

        data = pd.read_csv(data_path, dtype={'Symbol':str})
        trading_days = sorted(data['Date'].unique())
        data['Date'] = pd.to_datetime(data['Date'])
        data = data.sort_values('Date').set_index('Date')
        
        return data, trading_days

    def get_recent(self, date, symbol, n_days) -> pd.DataFrame:

        # date로부터 1일전 ~ n일전 데이터 반환

        if date > self.trading_days[-1]:
            # 데이터에 존재하는 마지막 거래일 포함, n 거래일 동안의 데이터 반환
            start_date = self.trading_days[-n_days]
            end_date = self.trading_days[-1]

        elif date <= self.trading_days[0]:
            # 빈 프레임 반환 (컬럼, 인덱스는 유지)
            return self['1900':'1900']

        else:

            if date in self._trading_days_to_idx:
                idx = self._trading_days_to_idx[date]
            else:
                for i, d in enumerate(self.trading_days):
                    if d > date:
                        idx = i
                        break

            if idx - n_days >= 0:
                start_date = self.trading_days[idx - n_days]
                end_date = self.trading_days[idx - 1]
            else:
                start_date = self.trading_days[0]
                end_date = self.trading_days[idx - 1]

        return self[start_date:end_date, symbol]

    def __getitem__(self, key):

        if isinstance(key, tuple):
            
            # market_data[from_date:to_date, symbol] 범위 양끝 날짜의 데이터 포함
            if isinstance(key[0], slice):
                from_date, to_date = key[0].start, key[0].stop
                if not from_date:
                    from_date = self.trading_days[0]
                if not to_date:
                    to_date = self.trading_days[-1]
                symbol = key[1]
                df = self.data[from_date:to_date]
                df = df.loc[df['Symbol'] == symbol]
                return df

            # market_data[date, symbol]
            else:
                date, symbol = key
                df = self.data[date:date]
                df = df.loc[df['Symbol'] == symbol].iloc[0] # pd.Series
                return df

        # market_data[from_date:to_date] 범위 양끝 날짜의 데이터 포함
        elif isinstance(key, slice):
            from_date, to_date = key.start, key.stop
            if not from_date:
                from_date = self.trading_days[0]
            if not to_date:
                to_date = self.trading_days[-1]
            return self.data[from_date:to_date]

        # market_data[date]
        else:
            date = key
            return self.data[date:date]
