import requests
import math
from scipy.stats import norm
import deltacalculate.calculatedelta as delta
from scipy.optimize import brentq
from deltacalculate.kiteapp import *
import deltacalculate.kiteapp as kiteVal
from kiteconnect import KiteConnect
import pandas as pd
from datetime import datetime, date, timedelta
#import pywhatkit as payval
from decimal import Decimal
import re
import time
import sys
import pytz
from bs4 import BeautifulSoup
import yfinance as yf



logging.basicConfig(
    level=logging.INFO,  # Set the log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s"
)
TELEGRAM_BOT_TOKEN = "7196489801:AAEtN8UxDlPjO8_5RdkeVen9dfs0H7LyW2M"
CHAT_ID = "5102108402"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
    }
    response = requests.post(url, json=payload)
    return response.json()


expiryDate = ""
optionChain = ""
pedeltaVal = ""

def callEveryMinute():
   
 #logging.info(f"detail PE is :{pe}")
 #logging.info(f"detail CE is :{ce}")
 #logging.info(f"detail Expiry is :{expirydate}")
 # Fetch Nifty option chain data from NSE API
 session = requests.Session()
 india_tz = pytz.timezone('Asia/Kolkata')
 now = datetime.now(india_tz)
 logging.info(f"Task is Started to run in get option:: {now} {now.hour}")

# Example usage
 symbol = "NIFTY"
 #expiry_date = "28-Nov-2024"  # Define the expiry date you want to filter
 #expiry_date = expirydate
 #filtered_option_chain = get_option_chain_for_expiry(symbol, expiry_date)
 #logging.info(f"filtered_option_chain:: {filtered_option_chain}")

# Example usage
 # option_chain_data = fetch_nifty_option_chain()
# print(option_chain_data)

 with open("deltacalculate/enctoken.txt") as f1:
    enctoken = f1.read()
 with open("deltacalculate/userdetail.txt") as user:
    username = user.read()
 with open("deltacalculate/usercode.txt") as code:
    usercode = code.read()   
 

 kite = KiteApp(reqsession=session,api_key=username, userid=usercode, enctoken=enctoken, debug=False)

 #logging.info(f"usercode::   {usercode}")
 #logging.info(f"enctoken:: {enctoken} ")
 #logging.info(f"username:: {username} ")
# holding = kite.holdings()
 positionm = kite.positions()
 peToken = ''
 peLastPrice = ''
 ceToken = ''
 ceLastPrice = ''
 CeStrikePrice = ''
 PeStrikePrice = ''
 expiryMonth = ''
 optionTypeCE = ''
 optionTypePE = ''
 totalPNL = 0
 
 for item in positionm["net"]:
 
    tradingsymbol = item["tradingsymbol"]
    instrument_token = item["instrument_token"]
    quantity = item["quantity"]
    last_price = item["last_price"]
    pnl = item["pnl"]
    totalPNL = totalPNL + pnl
    expiry, option_type, strike_price = parse_option_symbol(tradingsymbol)
    expiryMonth = expiry
    if option_type == 'PE' and quantity != 0:
        peToken = instrument_token
        peLastPrice= last_price
        PeStrikePrice = strike_price
        optionTypePE = option_type
    if option_type == 'CE' and quantity != 0: 
        ceToken = instrument_token
        ceLastPrice= last_price
        CeStrikePrice = strike_price
        optionTypeCE = option_type
          
    print(f"Expiry: {expiry}, Option Type: {option_type}")
    print(f"Symbol: {tradingsymbol}, Token: {instrument_token}, Qty: {quantity}, LTP: {last_price}, CE: {CeStrikePrice}, PE: {PeStrikePrice}")
    #insturment_type = nifty_option.iloc[0]['instrument_type']
    
    
 print(f"ceToken: {ceToken}, ceLastPrice: {ceLastPrice}, peToken: {peToken}, peLastPrice: {peLastPrice}")
 
 if totalPNL <= -650:
     # EXIT  trade
    for item in positionm["net"]:
 
     tradingsymbol = item["tradingsymbol"]
     instrument_token = item["instrument_token"]
     quantity = item["quantity"]
     exchange = item['exchange']
     pnl = item["pnl"]
     totalPNL = totalPNL + pnl
     expiry, option_type, strike_price = parse_option_symbol(tradingsymbol)
     expiryMonth = expiry
     if quantity != 0:
        transaction_type = "SELL" if quantity > 0 else "BUY"
        exit_qty = abs(quantity)
        orderID = kite.place_order(
     variety=kite.VARIETY_REGULAR,
     exchange=exchange,  # NFO for options
     tradingsymbol=tradingsymbol,  # Expiry + Strike + CE/PE
     transaction_type=transaction_type,
     quantity=exit_qty,  # Adjust based on lot size
     order_type=kite.ORDER_TYPE_MARKET,
     product=item['product']  # Use NRML for overnight F&O
     )
     send_telegram_message(f"Trade exited  :: {orderID}")    
        
 if  now.hour == 15:
     if now.minute >= 00:
     # EXIT  trade
      for item in positionm["net"]:
 
       tradingsymbol = item["tradingsymbol"]
       instrument_token = item["instrument_token"]
       quantity = item["quantity"]
       exchange = item['exchange']
       pnl = item["pnl"]
       totalPNL = totalPNL + pnl
       expiry, option_type, strike_price = parse_option_symbol(tradingsymbol)
       expiryMonth = expiry
       if quantity != 0:
        transaction_type = "SELL" if quantity > 0 else "BUY"
        exit_qty = abs(quantity)
        orderID = kite.place_order(
        variety=kite.VARIETY_REGULAR,
        exchange=exchange,  # NFO for options
        tradingsymbol=tradingsymbol,  # Expiry + Strike + CE/PE
        transaction_type=transaction_type,
        quantity=exit_qty,  # Adjust based on lot size
        order_type=kite.ORDER_TYPE_MARKET,
        product=item['product']  # Use NRML for overnight F&O
        )  
        send_telegram_message(f"Trade exited  :: {orderID}") 
 
 

 #instrument_token1 = 12902146  # Replace with actual token PE
 #instrument_token2 = 12913922  #CE
 instrument_token1 = peToken  # Replace with actual token PE
 instrument_token2 = ceToken  #CE

 openpositionlist = []
 openpositionlist.append(16114434)
 openpositionlist.append(14021378)




# Convert the string into a datetime objec
 date_obj = pd.to_datetime(expiryMonth)
# Format the date to "DD-MMM-YYYY"
 expiry = date_obj.strftime("%d-%b-%Y")
 expiryDate = expiry
# Fetch Live NIFTY Price
def parse_option_symbol(symbol):
    # Regular expression pattern for extracting details
    pattern = r"NIFTY(\d{2})([A-Z]{3})(\d{5})([CP]E)"
    match = re.match(pattern, symbol)
    
    if match:
        year = 2000 + int(match.group(1))  # Extract year and convert to full format
        month_str = match.group(2)  # Extract month abbreviation
        strike_price = match.group(3)  # Extract strike price
        option_type = match.group(4)  # Extract CE/PE
        
        # Convert month abbreviation to month number
        month = datetime.strptime(month_str, "%b").month
        
        # Construct expiry date (assuming last Thursday of the month)
        # Get the last Thursday of the expiry month
        expiry_date = get_last_thursday(year, month)
        #expiry_date = datetime(int(year), month, 1)  # First day of the expiry month
        return expiry_date.strftime("%Y-%m-%d"), option_type, strike_price  # Returning year-month and option type
    
    return None, None , None
def get_last_thursday(year, month):
    """Returns the last Thursday of the given month and year."""
    # Find the last day of the month
    last_day = datetime(year, month + 1, 1) - timedelta(days=1)  # Last day of the given month
    
    # Move back to the last Thursday
    while last_day.weekday() != 3:  # Thursday is represented by 3 in weekday()
        last_day -= timedelta(days=1)
    
    return last_day

 

