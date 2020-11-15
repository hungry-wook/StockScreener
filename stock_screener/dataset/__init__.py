import os
import pandas as pd
import pickle
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from stock_screener.data_reader import *


DATASET_DIR = '/'.join(os.path.abspath(__file__).split('/')[:-3])
DATASET_DIR = os.path.join(DATASET_DIR, 'dataset')

FINANCIAL_SUMMARY_DATA_FILENAME = 'financial_summary_data.pkl'
STOCK_PRICE_DATA_FILENAME = 'stock_price_data.pkl'
DEPOSIT_DATA_FILENAME = 'deposit_data.pkl'

def _make_dir():
    if not os.path.exists(DATASET_DIR):
        os.mkdir(DATASET_DIR)

def download_financial_summary_data():
    
    """ data: Dict[Text, Dict[Text, pd.DataFrame]] """

    print('Start Downloading Financial Summary Data...')
    _make_dir()

    corp_data = get_corporation_data()
    data = dict()
    for code in tqdm(corp_data['종목코드']):
        a, q = get_financial_summary(code)
        if not (a is None and q is None):
            data[code] = {'annual':a, 'quarter':q}

    with open(os.path.join(DATASET_DIR, 
                           FINANCIAL_SUMMARY_DATA_FILENAME), 'wb') as f:
        pickle.dump(data, f)
    print('Download Completed!')

def load_financial_summary_data(update=False):

    path = os.path.join(DATASET_DIR, 
                        FINANCIAL_SUMMARY_DATA_FILENAME)
    if (not os.path.exists(path)) or update:
        download_financial_summary_data()

    with open(path, 'rb') as f:
        data = pickle.load(f)
    return data

def download_stock_price_data(start='2001-01-01'):

    """ data: Dict[Text, pd.DataFrame] """

    print('Start Downloading Stock Price Data...')
    _make_dir()

    corp_data = get_corporation_data()
    data = dict()
    for code in tqdm(corp_data['종목코드']):
        df = get_stock_price(code, start)
        if len(df) > 0:
            data[code] = df
    data['KOSPI'] = get_stock_price('KS11', start)
    data['KOSDAQ'] = get_stock_price('KQ11', start)

    with open(os.path.join(DATASET_DIR,
                           STOCK_PRICE_DATA_FILENAME), 'wb') as f:
        pickle.dump(data, f)
    print('Download Completed!')

def load_stock_price_data(update=False):

    path = os.path.join(DATASET_DIR,
                        STOCK_PRICE_DATA_FILENAME)
    if (not os.path.exists(path)) or update:
        download_stock_price_data()

    with open(path, 'rb') as f:
        data = pickle.load(f)
    return data

def download_deposit_data():

    """ data: pd.DataFrame """

    print('Start Downloading Deposit Data...')
    _make_dir()

    # Get Total Page Number
    r = requests.get('https://finance.naver.com/sise/sise_deposit.nhn')
    soup = BeautifulSoup(r.content, 'html.parser')
    total_page_num = int(soup.find('td', {'class': 'pgRR'})\
                         .find('a', href=True)['href']\
                         .split('=')[1])

    # Scrap each page
    dfs = []
    for i in tqdm(range(1, total_page_num + 1)):
        df = pd.read_html('https://finance.naver.com/sise/sise_deposit.nhn?page={}'.format(i),
                          encoding='euc-kr')[0]
        dfs.append(df)

    # Merge & Postprocess
    data = pd.concat(dfs).dropna()
    data = data.iloc[:,[0,1,3,5,7,9]]
    data.columns = ['날짜', '고객예탁금', '신용잔고',
                    '펀드_주식형', '펀드_혼합형', '펀드_채권형']
    data.index = pd.to_datetime(data['날짜'].apply(lambda x: '20' + x))
    data.drop('날짜', axis=1, inplace=True)
    data = data.iloc[::-1]

    with open(os.path.join(DATASET_DIR,
                           DEPOSIT_DATA_FILENAME), 'wb') as f:
        pickle.dump(data, f)
    print('Download Completed!')

def load_deposit_data(update=False):

    """ 증시자금동향 """

    path = os.path.join(DATASET_DIR,
                        DEPOSIT_DATA_FILENAME)
    if (not os.path.exists(path)) or update:
        download_deposit_data()

    with open(path, 'rb') as f:
        data = pickle.load(f)
    return data
