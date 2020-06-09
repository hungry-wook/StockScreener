import pandas as pd
from datetime import date

if __name__ == '__main__':
    
    dfs = pd.read_html('https://finance.naver.com/sise/theme.nhn', encoding='euc-kr')
    df = dfs[0].dropna()
    df.columns = ['테마명', '전일대비', '최근3일등락률(평균)', '상승', '보합', '하락', '주도주1', '주도주2']
    today = str(date.today())
    df.to_csv('{}.csv'.format(today), index=False)
