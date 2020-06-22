import os
import pickle
from tqdm import tqdm
from algo_trading.data_reader import DataReader


DATASET_DIR = '/'.join(os.path.abspath(__file__).split('/')[:-3])
DATASET_DIR = os.path.join(DATASET_DIR, 'dataset')

FINANCIAL_SUMMARY_DATA_FILENAME = 'financial_summary_data.pkl'
STOCK_PRICE_DATA_FILENAME = 'stock_price_data.pkl'

def _make_dir():
    if not os.path.exists(DATASET_DIR):
        os.mkdir(DATASET_DIR)

def download_financial_summary_data():
    
    """ data: Dict[Text, Dict[Text, pd.DataFrame]] """

    print('Start Downloading Financial Summary Data...')
    _make_dir()

    dr = DataReader()
    corp_data = dr.get_corporation_data()
    data = dict()
    for code in tqdm(corp_data['종목코드']):
        a, q = dr.get_financial_summary(code)
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

    dr = DataReader()
    corp_data = dr.get_corporation_data()
    data = dict()
    for code in tqdm(corp_data['종목코드']):
        df = dr.get_stock_price(code, start)
        if len(df) > 0:
            data[code] = df
    data['KOSPI'] = dr.get_stock_price('KS11', start)
    data['KOSDAQ'] = dr.get_stock_price('KQ11', start)

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
