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
        - 적정 주가(float)
    """
    book_value = annual_data.loc['{}/12'.format(year)]['지배주주지분']
    try:
        # 내년도 컨센서스 존재하는 경우
        return_on_equity = annual_data.loc['{}/12(E)'.format(year+1)]['ROE']
    except:
        # 내년도 컨센서스가 없는 경우. N개년 가중평균하여 추정
        return_on_equity = 0
        denominator = 0
        for i in range(0, n_lookback_year):
            _return_on_equity = annual_data.loc['{}/12'.format(year-i)]['ROE']
            return_on_equity += (n_lookback_year - i) * _return_on_equity
            denominator += (i+1)
        return_on_equity /= denominator

    return_on_equity /= 100

    num_stock = annual_data.loc['{}/12'.format(year)]['발행주식수'] * 1000

    excess_return = book_value * (return_on_equity - required_return)
    company_value = book_value + excess_return / required_return
    stock_value = company_value * 1e8 / num_stock

    return stock_value
