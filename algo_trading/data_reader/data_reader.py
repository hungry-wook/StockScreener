import pandas as pd
import FinanceDataReader as fdr


class DataReader:
        
    def get_corporation_data(self):
        url = 'http://kind.krx.co.kr/corpgeneral/corpList.do?method=download'
        corp_data = pd.read_html(url, header=0)[0]
        corp_data['종목코드'] = corp_data['종목코드'].map('{:06d}'.format)
        return corp_data

    def get_stock_price(self, code, start=None, end=None):
        return fdr.DataReader(code, start, end)

    def get_financial_summary(self, code):

        def postprocess_df(df, data_type):
            _df = df[data_type].copy()
            _df = _df[[x for x in _df.columns if '(' not in x]].T
            _df.columns = df['IFRS(연결)'].values.flatten()
            return _df

        data = pd.read_html('https://comp.fnguide.com/SVO2/asp/SVD_Main.asp?gicode=A{}'.format(code))
        annual_data = postprocess_df(data[11], 'Annual') # 최근 5개년
        quarter_data = postprocess_df(data[12], 'Net Quarter') # 최근 5분기

        return annual_data, quarter_data

    def get_financial_report(self, code):

        def postprocess_name(x):
            x = x.replace('계산에 참여한 계정 펼치기', '')
            x = x.replace(' ', '')
            x = x.replace('*', '')
            x = x.strip()
            if x[0] == '(' and x[-1] == ')':
                x = x[1:-1]
            return x

        def postprocess_df(df):
            df = df.reset_index(drop=True)
            df['IFRS(연결)'] = df['IFRS(연결)'].apply(lambda x: postprocess_name(x))
            df.drop(['전년동기', '전년동기(%)'], axis=1, inplace=True)
            df = df.set_index('IFRS(연결)').T
            df.columns.name = ''
            return df

        url = 'https://comp.fnguide.com/SVO2/asp/SVD_Finance.asp?gicode=A{}'.format(code)
        data = pd.read_html(url)

        # 연간 포괄손익계산서 / 연간 재무상태표 / 연간 현금흐름표 (최근 4년)
        annual_data = pd.concat((data[0], data[2], data[4]), sort=False)
        annual_data = postprocess_df(annual_data)

        # 분기 포괄손익계산서 / 분기 재무상태표 / 분기 현금흐름표 (최근 4분기)
        quarter_data = pd.concat((data[1], data[3], data[5]), sort=False)
        quarter_data = postprocess_df(quarter_data)

        return annual_data, quarter_data
