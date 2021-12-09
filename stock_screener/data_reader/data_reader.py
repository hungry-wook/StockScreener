import json
import requests
import numpy as np
import pandas as pd
import FinanceDataReader as fdr


def get_corporation_data():
    url = 'http://kind.krx.co.kr/corpgeneral/corpList.do?method=download'
    corp_data = pd.read_html(url, header=0)[0]
    corp_data['종목코드'] = corp_data['종목코드'].map('{:06d}'.format)
    return corp_data

def get_stock_price(code, start=None, end=None):
    return fdr.DataReader(code, start, end)

def get_financial_summary(code, remove_estimation=True):

    # Input
    # - code: 종목코드(6자리)
    # - remove_estimation: 컨센서스, 확정되지 않은 실적 제거

    # Output
    # - annual_data: 최근 5년 연단위 재무제표
    # - quarter_data: 최근 5분기 분기 단위 재무제표

    def postprocess_df(df, data_type):
        _df = df[data_type].copy()
        _df = _df.T
        _df.columns = df['IFRS(연결)'].values.flatten()
        return _df

    url = 'https://comp.fnguide.com/SVO2/asp/SVD_Main.asp?gicode=A{}'.format(code)
    try:
        data = pd.read_html(url)
    except:
        return None, None

    try:
        annual_data = postprocess_df(data[11], 'Annual') # 최근 5개년
    except:
        annual_data = None
    try:
        quarter_data = postprocess_df(data[12], 'Net Quarter') # 최근 5분기
    except:
        quarter_data = None

    if remove_estimation:
        # len('2020/06') == 7, len('2020/09(E)') != 7
        try:
            annual_data = annual_data.loc[[len(x) == 7 for x in annual_data.index]]
        except:
            annual_data = None
        try:
            quarter_data = quarter_data.loc[[len(x) == 7 for x in quarter_data.index]]
        except:
            quarter_data = None

    return annual_data, quarter_data

def get_financial_report(code):

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
    try:
        data = pd.read_html(url)
    except:
        return None, None

    # 연간 포괄손익계산서 / 연간 재무상태표 / 연간 현금흐름표 (최근 4년)
    try:
        annual_data = pd.concat((data[0], data[2], data[4]), sort=False)
        annual_data = postprocess_df(annual_data)
    except:
        annual_data = None

    # 분기 포괄손익계산서 / 분기 재무상태표 / 분기 현금흐름표 (최근 4분기)
    try:
        quarter_data = pd.concat((data[1], data[3], data[5]), sort=False)
        quarter_data = postprocess_df(quarter_data)
    except:
        quarter_data = None

    return annual_data, quarter_data

def get_kospi200_price():
    dfs = []
    for i in range(1, 20 + 1):
        df = pd.read_html('https://finance.naver.com/sise/entryJongmok.nhn?&page={}'.format(i))[0]
        dfs.append(df)
    kospi200_price = pd.concat(dfs).dropna().reset_index(drop=True)
    return kospi200_price

def get_recent_biz_day():
    # 가장 최근 거래일을 YYYYMMDD 형태로 반환한다
    df = pd.read_html('https://finance.naver.com/sise/sise_index_day.nhn?code=KOSPI', 
                      encoding='euc-kr')[0].dropna()
    return df['날짜'].iloc[0].replace('.', '')

def get_per_pbr_dividend(date):

    # Input: date(str): 최근 거래일, YYYYMMDD format
    # Output: 해당 일자 기준, KOSPI/KOSDAQ 종목별 PER/PBR/배당률 정보

    result = requests.post("http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd",
                           headers = {'User-Agent': 'Mozilla/5.0'},
                           params = dict(bld= 'dbms/MDC/STAT/standard/MDCSTAT03501',
                                         searchType=1,
                                         mktId='ALL',
                                         trdDd=date,
                                         isuCd='KR7005930003'))

    if not result.content:
        raise ValueError('Empty Result!')

    # Make DataFrame
    df = pd.DataFrame(json.loads(result.content)['output'])

    # Rename Columns, Remove unused columns
    columns={
        'DVD_YLD':'배당수익률',
        'TDD_CLSPRC':'종가',
        'ISU_SRT_CD':'종목코드',
        'ISU_ABBRV':'종목명'
    }
    df = df.rename(columns=columns)
    df =df[['종목명', '종목코드', '종가', 'PER', 'PBR', '배당수익률']]

    # Preprocess Variables
    for col in ['종가', 'PER', 'PBR', '배당수익률']:
        df[col] = df[col].apply(lambda x: x.replace(',', ''))
    df = df.replace(to_replace='-', value=np.NaN)
    df = df.replace(to_replace='', value=np.NaN)
    df = df.astype({
        '종목명':str,
        '종목코드':str,
        '종가':np.int,
        'PER':np.float,
        'PBR':np.float,
        '배당수익률':np.float
    })

    return df

def get_sector(date):

    # WiseIndex에서 제공하는 WICS 섹터 분류를 가져옴
    # 섹터 분류는 조회일(date) 기준이며, 개장 일자에 대해서만 조회 가능하다

    data = dict()

    for sec_cd in ['G1010', 'G1510', 'G2010', 'G2020', 'G2030', 
                   'G2510', 'G2520', 'G2530', 'G2550', 'G2560', 
                   'G3010', 'G3020', 'G3030', 'G3510', 'G3520',
                   'G4010', 'G4020', 'G4030', 'G4040', 'G4050',
                   'G4510', 'G4520', 'G4530', 'G4535', 'G4540', 
                   'G5010', 'G5020', 'G5510']:

        url = 'http://www.wiseindex.com/Index/GetIndexComponets?ceil_yn=0&dt={}&sec_cd={}'
        url = url.format(date, sec_cd)
        r = requests.get(url)
        df = pd.DataFrame(json.loads(r.content.decode('utf-8'))['list'])

        # Rename Columns, Remove unused columns
        columns={
            'CMP_CD':'종목코드',
            'CMP_KOR':'종목명',
            'IDX_NM_KOR':'섹터명'
        }
        df = df.rename(columns=columns)
        df = df[['종목명', '종목코드', '섹터명']]

        data[sec_cd] = df

    return data

