import json
import numpy as np
import pandas as pd
import requests


def get_recent_biz_day():
    # 가장 최근 거래일을 YYYYMMDD 형태로 반환한다
    df = pd.read_html('https://finance.naver.com/sise/sise_index_day.nhn?code=KOSPI', 
                      encoding='euc-kr')[0].dropna()
    return df['날짜'].iloc[0].replace('.', '')

def get_per_pbr_dividend(date):
    
    # Input: date(str): 최근 거래일, YYYYMMDD format
    # Output: 해당 일자 기준, KOSPI/KOSDAQ 종목별 PER/PBR/배당률 정보

    # Get OTP
    otp = requests.get('http://marketdata.krx.co.kr/contents/COM/GenerateOTP.jspx', 
                   headers={'User-Agent': 'Mozilla/5.0'},
                   params=dict(name='form', 
                               bld='MKD/13/1302/13020401/mkd13020401'))
    # Get Data (with OTP generated above)
    result = requests.post('http://marketdata.krx.co.kr/contents/MKD/99/MKD99000001.jspx',
                           headers={'User-Agent': 'Mozilla/5.0'},
                           params=dict(market_gubun='ALL', 
                                       gubun=1, 
                                       schdate=date, 
                                       code=otp.text))
    
    if not result.content:
        raise ValueError('Empty Result!')

    # Make DataFrame
    df = pd.DataFrame(json.loads(result.content)['result'])

    # Rename Columns, Remove unused columns
    columns={
        'dvd_yld':'배당수익률',
        'end_pr':'종가',
        'isu_cd':'종목코드',
        'isu_nm':'종목명',
        'pbr':'PBR',
        'per':'PER',
        'work_dt':'기준일'
    }
    df = df.rename(columns=columns)
    df =df[['종목명', '종목코드', '기준일', '종가',
            'PER', 'PBR', '배당수익률']]

    # Preprocess Variables
    df['기준일'] = df['기준일'].apply(lambda x: x.replace('/', ''))
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

def pass_criteria(code):

    # 재무제표 데이터에서 원하는 조건을 만족하는 경우 True, 아니면 False 반환
    annual_data, quarter_data = get_financial_summary(code)

    try:
        # 최근 3개년 영업이익 흑자
        num_year = 3
        annual_profit = annual_data['영업이익'].tail(num_year)
        if not all(x > 0 for x in annual_profit):
            return False

        # 최근 3개년 ROE >= 8
        num_year = 3
        annual_roe = annual_data['ROE'].tail(num_year)
        if not all(x >= 8 for x in annual_roe):
            return False

        # 최근 3개년 배당수익률 >= 2
        num_year = 3
        annual_dvd = annual_data['배당수익률'].tail(num_year)
        if not all(x >= 2 for x in annual_dvd):
            return False

        # 최근 4분기 영업이익 흑자
        num_quarter = 4
        quarter_profit = quarter_data['영업이익'].tail(num_quarter)
        if not all(x > 0 for x in quarter_profit):
            return False
    except:
        # 체크하려는 값이 nan인 경우거나, 데이터가 불충분한 경우
        return False

    return True
