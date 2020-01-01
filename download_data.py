import pandas as pd
import FinanceDataReader as fdr
from tqdm import tqdm


start_date = '2015-01-01'
end_date = '2019-12-31'

df_list = []

# 코스피 지수 (start_date ~)
kospi_df = fdr.DataReader('KS11', start_date)
kospi_df['Symbol'] = 'KS11'
kospi_df['Date'] = kospi_df.index
kospi_df = kospi_df.reset_index(drop=True)
df_list.append(kospi_df)

# 종목정보
krx_df = fdr.StockListing('KRX')

# 각 종목별 주가 데이터
for symbol in tqdm(krx_df['Symbol']):
    df = fdr.DataReader(symbol, start_date, end_date)
    df['Symbol'] = symbol
    df['Date'] = df.index
    df = df.reset_index(drop=True)
    df_list.append(df)

# 하나의 테이블로 병합
data = pd.concat(df_list, axis=0, sort=False)
data.to_csv('stock_data.csv', index=False)
