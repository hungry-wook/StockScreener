import camelot
import pandas as pd

def get_stock_account(file):

    # 고위공직자 재산내역 pdf를 파싱하여, 주식 보유 및 증감내역을 가져온다
    tables = camelot.read_pdf(file, pages='all')
    rows = [x for table in tables for x in table.df.values]
    
#     lands = []
    stock_rows = []
    for row in rows:
        if '주식' in row[1]:
            stock_rows.append(row)
#         elif '㎡' in row[2]:
#             lands.append(row)
        else:
            continue
    stock_df = pd.DataFrame(stock_rows)
    stock_list = [x.strip().replace('\n', '') for y in stock_df.iloc[:,2] for x in y.split(', ')]

    stock_quantity = dict()
    stock_increase = dict()
    stock_decrease = dict()

    for x in stock_list:

        # LG전자보통주 3,000주(150주 증가)
        x = x.replace(',', '')
        # LG전자보통주 3000(150 증가)

        if '증가' in x:
            # (LG전자보통주, 3000)
            stock_name, quantity = x.rsplit('(', maxsplit=1)[0].split()
            quantity = float(quantity.replace('주', ''))
            # 150
            increase_quantity = float(x.rsplit('(', maxsplit=1)[1].split()[0].replace('주', ''))

            if stock_name not in stock_increase:
                stock_increase[stock_name] = increase_quantity
            else:
                stock_quantity[stock_name] += increase_quantity

        elif '감소' in x:

            stock_name, quantity = x.rsplit('(', maxsplit=1)[0].split()
            quantity = float(quantity.replace('주', ''))
            decrease_quantity = float(x.rsplit('(', maxsplit=1)[1].split()[0].replace('주', ''))

            if stock_name not in stock_decrease:
                stock_decrease[stock_name] = decrease_quantity
            else:
                stock_decrease[stock_name] += decrease_quantity

        else:
            stock_name, quantity = x.rsplit(maxsplit=1)
            quantity = float(quantity.replace('주', ''))

        if stock_name not in stock_quantity:
            stock_quantity[stock_name] = float(quantity)
        else:
            stock_quantity[stock_name] += float(quantity)

    return stock_quantity, stock_increase, stock_decrease
