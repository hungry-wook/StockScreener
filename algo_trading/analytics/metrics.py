import pandas as pd


def rim_price(annual_data: pd.DataFrame, year:int,
              required_return=0.08, n_lookback_year=3):

    #FIXME: 바운더리 케이스 처리. (E) 존재 여부. 과거의 경우 ROE가 추정치가 아닌 실제값. 인퍼런스 타임과 좀 다름
   
    """
    Residual Income Model
    
    n_lookback_year: ROE에 대한 컨센서스가 없는 경우, ROE 추정에 활용할 데이터 개수
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
