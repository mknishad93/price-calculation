import pandas as pd
import datetime as dt
from deltacalculate.kiteapp import *
from time import sleep
import xlwings as xw  # pip install xlwings

with open("enctoken.txt") as f1:
	enctoken = f1.read()
kite = KiteApp("Mahesh", "mu", enctoken)



#wb = xw.Book("OptChain.xlsx")
#sht = wb.sheets("Sheet1")

inst = kite.instruments('NFO')
df = pd.DataFrame(inst)

index = 'NIFTY'
def get_weekly_expiry(df, index):
    df = df[df['name'] == index]
    df = df[df['segment'] == 'NFO-OPT']
    exp = df['expiry'].to_list()
    td = dt.date.today()
    zrdexp = min(exp, key=lambda x: (x - td))
    df = df[df['expiry'] == zrdexp]
    return df, zrdexp


data, exp = get_weekly_expiry(df, index)
ltp_symbol = ['NFO:' + x for x in data['tradingsymbol'].to_list()]




def get_option_chain(quote):
    opt_data = {}
    for k, v in quote.items():
        opt_data.update({k: {f'{k[-2:].lower()}-ltp': v['last_price'], f'{k[-2:].lower()}-oi': v['oi'],
                            f'{k[-2:].lower()}-open': v['ohlc']['open'],
                            f'{k[-2:].lower()}-high': v['ohlc']['high'],
                            f'{k[-2:].lower()}-low': v['ohlc']['low'],
                            f'{k[-2:].lower()}-close': v['ohlc']['close'],
                            f'{k[-2:].lower()}-volume': v['volume'],
                            'strike': k[-7:-2]}})
    return opt_data


def sort_ce_pe(opt_data):
    ce_data = {}
    pe_data = {}
    for i, j in opt_data.items():
        if i[-2:] == 'CE':
            ce_data.update({i: j})
        elif i[-2:] == 'PE':
            pe_data.update({i: j})
    return ce_data,pe_data


def crete_option_chain(bn_ce, bn_pe, name):
	cal = pd.DataFrame(bn_ce).T
	cal = cal.sort_values('strike')
	cal = cal.set_index(cal['strike'])
	cal = cal[['ce-oi', 'ce-volume', 'ce-open',
            'ce-high', 'ce-low', 'ce-close', 'ce-ltp', 'strike']]

	pt = pd.DataFrame(bn_pe).T
	pt = pt.sort_values('strike')
	pt = pt[['pe-ltp', 'pe-close', 'pe-low', 'pe-high', 'pe-open', 'pe-volume',
          'pe-oi', 'strike']]
	pt = pt.set_index('strike', drop=True)

	opt_data = pd.concat([cal, pt], axis=1)
	opt_data = opt_data.reset_index(drop=True)
	opt_data = opt_data.rename(columns={'strike': name})
	return opt_data
print("Start Option Chain Data..")
while True:
    quote = kite.quote(ltp_symbol)
    opt_data = get_option_chain(quote)
    ce_data,pe_data = sort_ce_pe(opt_data)
    df = crete_option_chain(ce_data, pe_data, index)
    sht['A1'].options(index=False).value = df
    sleep(1)


