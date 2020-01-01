import os
import pandas as pd
from glob import glob
from tqdm import tqdm


class MarketData:
    
    def __init__(self, data_path):
        self.data, self.trading_days = self._load_data(data_path)

    def _load_data(self, data_path):

        data = pd.read_csv(data_path)
        trading_days = sorted(data['Date'].unique())
        data['Date'] = pd.to_datetime(data['Date'])
        data = data.sort_values('Date').set_index('Date')
        
        return data, trading_days

    def __getitem__(self, key):

        if isinstance(key, tuple):
            
            # market_data[from_date:to_date, symbol]
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

        # market_data[from_date:to_date]
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
