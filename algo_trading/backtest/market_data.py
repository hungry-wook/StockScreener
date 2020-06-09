import os
import pandas as pd
from glob import glob
from tqdm import tqdm


class MarketData:
    
    def __init__(self, data_path):
        self.data, self.trading_days = self._load_data(data_path)
        self._trading_days_to_idx = {d:i for i,d in enumerate(self.trading_days)}

    def _load_data(self, data_path):

        df = pd.read_csv(data_path, dtype={'Symbol':str})
        trading_days = sorted(df['Date'].unique())

        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date').set_index('Date')

        data = {k: v for k, v in df.groupby('Symbol')}

        return data, trading_days

    def get_recent(self, symbol, date, n_days) -> pd.DataFrame:

        # date로부터 1일전 ~ n일전 데이터 반환

        if date > self.trading_days[-1]:
            # 데이터에 존재하는 마지막 거래일 포함, n 거래일 동안의 데이터 반환
            start_date = self.trading_days[-n_days]
            end_date = self.trading_days[-1]

        elif date <= self.trading_days[0]:
            # 빈 프레임 반환 (컬럼, 인덱스는 유지)
            return self[symbol, '1900':'1900']

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

        return self[symbol, start_date:end_date]

    def __getitem__(self, key):

        if isinstance(key, tuple):
            
            # market_data[symbol, from_date:to_date] (범위 양끝 날짜의 데이터 포함)
            if isinstance(key[1], slice):
                symbol = key[0]
                from_date, to_date = key[1].start, key[1].stop
                if not from_date:
                    from_date = self.trading_days[0]
                if not to_date:
                    to_date = self.trading_days[-1]
                df = self.data[symbol][from_date:to_date]
                return df # pd.DataFrame

            # market_data[symbol, date]
            else:
                symbol, date = key
                df = self.data[symbol][date:date].iloc[0]
                return df # pd.Series

        # market_data[symbol]
        else:
            symbol = key
            return self.data[symbol] # pd.DataFrame
