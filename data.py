import os
import pandas as pd
from glob import glob
from tqdm import tqdm


class MarketData:
    
    def __init__(self, dir_path, stock_codes=[]):
        self.data, self.trading_days = self._load_data(dir_path, stock_codes)

    def _load_data(self, dir_path, stock_codes):

        files = []
        for fp in glob(os.path.join(dir_path, '*')):
            stock_code = str(os.path.basename(fp).split('.')[0])
            # 종목코드 지정한 경우, 해당 종목 데이터만 로드한다
            if stock_codes:
                if stock_code in stock_codes:
                    files.append((stock_code, fp))
            else:
                files.append((stock_code, fp))

        df_list = []
        for stock_code, fp in tqdm(files):
            _df = pd.read_csv(fp)
            _df['stock_code'] = stock_code
            df_list.append(_df)
            
        data = pd.concat(df_list)
        assert all([(col in data) for col in ['date', 'open', 'high', 'low', 'close']])

        trading_days = sorted(data['date'].unique())

        data['date'] = pd.to_datetime(data['date'])
        data = data.sort_values('date').set_index('date')
        
        return data, trading_days

    def __getitem__(self, key):

        if isinstance(key, tuple):
            
            # market_data[from_date:to_date, stock_code]
            if isinstance(key[0], slice):
                from_date, to_date = key[0].start, key[0].stop
                if not from_date:
                    from_date = self.trading_days[0]
                if not to_date:
                    to_date = self.trading_days[-1]
                stock_code = key[1]
                df = self.data[from_date:to_date]
                df = df.loc[df['stock_code'] == stock_code]
                return df

            # market_data[date, stock_code]
            else:
                date, stock_code = key
                df = self.data[date:date]
                df = df.loc[df['stock_code'] == stock_code].iloc[0] # pd.Series
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
