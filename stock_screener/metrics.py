import numpy as np
import pandas as pd


def rim_price(annual_data: pd.DataFrame, year:int,
              required_return=0.08, n_lookback_year=3):

    """
    Residual Income Model를 활용하여 적정주가를 계산한다

    Inputs:
        - year: 현재 시점 기준으로 직전년도 (i.e. 현재 2020년 7월 -> 2019 입력)
            - 직전년도 이외에는 의미 없음. 주어진 ROE 값이 컨센서스 추정치가 아니라 실제값이기 때문
        - required_return: 요구 수익률 (RIM 모델 참고)
        - n_lookback_year: ROE에 대한 컨센서스가 없는 경우, ROE 추정에 활용할 데이터 개수

    Output
        - 적정 주가(int)
        - RIM 계산에 필요한 데이터가 불충분한 경우에는 exception을 발생시킨다
    """

    ##### 분석 대상 제외하는 종목 #####

    # 장부가치 체크
    try:
        book_value = int(annual_data.loc['{}/12'.format(year)]['지배주주지분'])
    except:
        raise ValueError('장부가치 오류')

    # 발행주식수 체크
    try:
        _num_stock = int(annual_data.loc['{}/12'.format(year)]['발행주식수'])
    except:
        raise ValueError('발행주식수 오류')
    num_stock = _num_stock * 1000

    # ROE 체크
    for x in list(annual_data['ROE']):
        try:
            float(x)
        except:
            raise ValueError('ROE 오류')
    ##############################

    next_year = '{}/12(E)'.format(year+1)
    # 내년도 컨센서스 존재하는 경우
    if (next_year in annual_data.index) and \
        not np.isnan(annual_data.loc[next_year]['ROE']):
        return_on_equity = float(annual_data.loc[next_year]['ROE'])

    # 내년도 컨센서스가 없는 경우. 직전 N개 년도 데이터 가중평균하여 추정
    else:
        return_on_equity = 0
        denominator = 0
        for i in range(0, n_lookback_year):
            _return_on_equity = float(annual_data.loc['{}/12'.format(year-i)]['ROE'])
            if np.isnan(_return_on_equity):
                continue
            else:
                return_on_equity += (n_lookback_year - i) * _return_on_equity
                denominator += (i+1)
        if denominator == 0:
            # RIM 계산에 필요한 데이터가 불충분한 경우
            raise ValueError('ROE 추정 불가능')

        return_on_equity /= denominator

    return_on_equity /= 100

    excess_return = book_value * (return_on_equity - required_return)
    company_value = book_value + excess_return / required_return
    stock_value = int(company_value * 1e8 / num_stock)

    return stock_value

def check_metric_increasing(annual_data: pd.DataFrame,
                            start_year: int, end_year: int,
                            metric: str,
                            should_be_positive=False):

    """
    최근 n년간의 특정 재무지표의 값이 단조 증가했는지 체크한다
    Inputs
        - annual_data: 연단위 재무제표 데이터
        - start_year: 고려 대상 데이터 시작년도
        - end_year: 고려 대상 데이터 종료년도
        - metric: 재무지표 명 (i.e. 영업이익)
        - should_be_positive: 재무지표의 값이 항상 0보다 커야함을 조건에 추가
    """
    if metric not in annual_data:
        raise ValueError('Available metrics = [{}]'.format(list(annual_data.columns)))
        
    prev_value = annual_data[metric].loc['{}/12'.format(start_year)]

    for i in range(end_year - start_year + 1):

        value = annual_data[metric].loc['{}/12'.format(start_year + i)]
 
        if should_be_positive:
            if value < 0:
                return False

        if np.isnan(value):
            return False
        elif value < prev_value:
            return False
        else:
            prev_value = value

    return True

def check_metric_decreasing(annual_data: pd.DataFrame,
                            start_year: int, end_year: int,
                            metric: str,
                            should_be_positive=False):

    """
    최근 n년간의 특정 재무지표의 값이 단조 감소했는지 체크한다
    Inputs
        - annual_data: 연단위 재무제표 데이터
        - start_year: 고려 대상 데이터 시작년도
        - end_year: 고려 대상 데이터 종료년도
        - metric: 재무지표 명 (i.e. 영업이익)
        - should_be_positive: 재무지표의 값이 항상 0보다 커야함을 조건에 추가
    """
    if metric not in annual_data:
        raise ValueError('Available metrics = [{}]'.format(list(annual_data.columns)))

    prev_value = annual_data[metric].loc['{}/12'.format(start_year)]

    for i in range(end_year - start_year + 1):

        value = annual_data[metric].loc['{}/12'.format(start_year + i)]

        if should_be_positive:
            if value < 0:
                return False

        if np.isnan(value):
            return False
        elif value >= prev_value:
            return False
        else:
            prev_value = value

    return True
