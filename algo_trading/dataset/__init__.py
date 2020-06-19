import os
import pickle
from tqdm import tqdm
from algo_trading.data_reader import DataReader


DATASET_DIR = '/'.join(os.path.abspath(__file__).split('/')[:-3])
DATASET_DIR = os.path.join(DATASET_DIR, 'dataset')

FINANCIAL_SUMMARY_DATA_FILENAME = 'financial_summary_data.pkl'

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

def load_financial_summary_data():

    path = os.path.join(DATASET_DIR, 
                        FINANCIAL_SUMMARY_DATA_FILENAME)
    if not os.path.exists(path):
        download_financial_summary_data()

    with open(path, 'rb') as f:
        data = pickle.load(f)
    return data
