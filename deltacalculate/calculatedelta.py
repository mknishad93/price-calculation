import math
from math import log, sqrt, exp
from scipy.stats import norm
from datetime import datetime
from scipy.optimize import brentq



# Function to calculate Delta for a Call or Put option using Black-Scholes
def calculate_delta(S, K, T, r, sigma, option_type):
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    
    if option_type == 'call':
        return norm.cdf(d1)  # Delta for Call Option
    elif option_type == 'put':
        return norm.cdf(d1) - 1  # Delta for Put Option
    else:
        raise ValueError("Invalid option type. Use 'call' or 'put'.")

# Example input values for Delta calculation
S = 17500  # Nifty current price (spot price)
K = 17600  # Strike price of the option
T = 0.25   # Time to expiration (in years, e.g., 3 months = 0.25)
r = 0.06   # Risk-free interest rate (6%)
sigma = 0.18  # Implied volatility (18%)

# Calculate Delta for a Call option
#delta = calculate_delta(S, K, T, r, sigma, option_type='call')
#print(f"Delta: {delta}")



# nifty spot price S
# K strike price 24000
#market price for spot 
# expiry_date_str '28-Nov-2024
# Parse the option chain data to calculate Delta for each option
def parse_and_calculate_delta(option_chain_data,formatted_date,strikeprice,insturment_type):
    #records = option_chain_data['records']['data']
    Dict = {}
    records= option_chain_data
    for record in records:
        strike_price = record['strikePrice']
        expiry = record['expiryDate']
       
        if formatted_date == expiry and strike_price==strikeprice:
         ce_data = record.get('CE')  # Call option data
         pe_data = record.get('PE')  # Put option data
         
         if 'CE'==insturment_type:
            S = ce_data['underlyingValue']  # Nifty spot price
            K = strike_price
           # T = ce_data['expiryDate']  # Calculate the time to expiry in years
            T = 3
            market_price = ce_data['lastPrice']  # This is the observed market price
            expiry_date_str = ce_data['expiryDate']  # Nifty expiry date as a string
            time_to_expiry_years = calculate_time_to_expiry(expiry_date_str)
            r = 0.10  # Risk-free interest rate
            #sigma = ce_data['impliedVolatility']
            sigma = 0.093  # Implied volatility (can be estimated)
            iv_call = implied_volatility(S, K, time_to_expiry_years, r, market_price, option_type='call')
            if(iv_call=="None"):iv_call = 0.10
            delta_call = calculate_delta(S, K, time_to_expiry_years, r, iv_call, option_type='call')
            print(f"Call Option - Strike Price: {strike_price}, Delta: {delta_call}")
            Dict['CE'] = delta_call
        
         if 'PE'==insturment_type:
            S = pe_data['underlyingValue']  # Nifty spot price
            K = strike_price
           # T = pe_data['expiryDate']  # Calculate the time to expiry in years
            T = 3
            market_price = pe_data['lastPrice']
            expiry_date_str = pe_data['expiryDate']  # Nifty expiry date as a string
            time_to_expiry_years = calculate_time_to_expiry(expiry_date_str)
            r = 0.10  # Risk-free interest rate
            #sigma = pe_data['impliedVolatility']
            sigma =  0.093  # Implied volatility (can be estimated)
            iv_call = implied_volatility(S, K, time_to_expiry_years, r, market_price, option_type='put')
            if(iv_call==""):iv_call = 0.10
            delta_put = calculate_delta(S, K, time_to_expiry_years, r, iv_call, option_type='put')
            print(f"Put Option - Strike Price: {strike_price}, Delta: {delta_put}")
            Dict['PE'] = delta_put
    
    return Dict

# nifty spot price S
# K strike price 24000
#market price for spot 
# expiry_date_str '28-Nov-2024
# Parse the option chain data to calculate Delta for each option
def parse_and_calculate_delta_static(niftySpotPrice, strikepriceint, strikepriceSpot,expiry, insturment_type):
    #records = option_chain_data['records']['data']
    Dict = {}
 

       
 
          # Call option data
          # Put option data
         
    if 'CE'==insturment_type:
            S = niftySpotPrice  # Nifty spot price
            K = strikepriceint
           # T = ce_data['expiryDate']  # Calculate the time to expiry in years
            T = 3
            market_price = strikepriceSpot  # This is the observed market price
            expiry_date_str =expiry  # Nifty expiry date as a string
            time_to_expiry_years = calculate_time_to_expiry(expiry_date_str)
            r = 0.10  # Risk-free interest rate
            #sigma = ce_data['impliedVolatility']
            sigma = 0.093  # Implied volatility (can be estimated)
            iv_call = implied_volatility(S, K, time_to_expiry_years, r, market_price, option_type='call')
            if(iv_call=="None"):iv_call = 0.10
            delta_call = calculate_delta(S, K, time_to_expiry_years, r, iv_call, option_type='call')
            print(f"Call Option - Strike Price: {strikepriceint}, Delta: {delta_call}")
            Dict['CE'] = delta_call
        
    if 'PE'==insturment_type:
            S = niftySpotPrice  # Nifty spot price
            K = strikepriceint
           # T = pe_data['expiryDate']  # Calculate the time to expiry in years
            T = 3
            market_price = strikepriceSpot
            expiry_date_str =expiry  # Nifty expiry date as a string
            time_to_expiry_years = calculate_time_to_expiry(expiry_date_str)
            r = 0.10  # Risk-free interest rate
            #sigma = pe_data['impliedVolatility']
            sigma =  0.093  # Implied volatility (can be estimated)
            iv_call = implied_volatility(S, K, time_to_expiry_years, r, market_price, option_type='put')
            if(iv_call==""):iv_call = 0.10
            delta_put = calculate_delta(S, K, time_to_expiry_years, r, iv_call, option_type='put')
            print(f"Put Option - Strike Price: {strikepriceint}, Delta: {delta_put}")
            Dict['PE'] = delta_put
    
    return Dict


# find option chain  Delta for each option
def parse_and_find_delta(option_chain_data,formatted_date,insturment_type, deltaprice):
    #records = option_chain_data['records']['data']
    Dict = {}
    records= option_chain_data
    
    
    option_data = [item for item in option_chain_data["records"]["data"]]
    for record in option_data:
       
        expiry = record['expiryDate']
        strike_price = record['strikePrice']
        #expiry_dates = filtered_option_chain["records"]["expiryDates"]
        #strike_prices = [item["strikePrice"] for item in filtered_option_chain["records"]["data"] if "strikePrice" in item]
        if formatted_date == expiry:
         ce_data = record.get('CE')  # Call option data
         pe_data = record.get('PE')  # Put option data
         
         if 'CE'==insturment_type:
            S = ce_data['underlyingValue']  # Nifty spot price
            K = strike_price
           # T = ce_data['expiryDate']  # Calculate the time to expiry in years
            T = 3
            market_price = ce_data['lastPrice']  # This is the observed market price
            expiry_date_str = pe_data['expiryDate']  # Nifty expiry date as a string
            time_to_expiry_years = calculate_time_to_expiry(expiry_date_str)
            r = 0.10  # Risk-free interest rate
            #sigma = ce_data['impliedVolatility']
            sigma = 0.093  # Implied volatility (can be estimated)
            iv_call = implied_volatility(S, K, time_to_expiry_years, r, market_price, option_type='call')
            #iv_call = ce_data['impliedVolatility']
            if(iv_call=="None"):iv_call = 0.10
            delta_call = calculate_delta(S, K, time_to_expiry_years, r, iv_call, option_type='call')
            delta_call_round = round(delta_call, 2)
            delta_price_round = abs(round(deltaprice, 2))                      
            diff = abs(delta_price_round - delta_call_round)
            #print(f"Call Option - Strike Price: {strike_price}, Delta: {delta_call}")
            if delta_price_round >= delta_call_round and diff <= 2:
               print(f"New Call Option - Strike Price: {strike_price}, Delta: {delta_call}")
               return strike_price
        
         if 'PE'==insturment_type:
            S = pe_data['underlyingValue']  # Nifty spot price
            K = strike_price
           # T = pe_data['expiryDate']  # Calculate the time to expiry in years
            T = 3
            market_price = pe_data['lastPrice']
            expiry_date_str = pe_data['expiryDate']  # Nifty expiry date as a string
            time_to_expiry_years = calculate_time_to_expiry(expiry_date_str)
            r = 0.10  # Risk-free interest rate
            #sigma = pe_data['impliedVolatility']
            sigma =  0.093  # Implied volatility (can be estimated)
            iv_call = implied_volatility(S, K, time_to_expiry_years, r, market_price, option_type='put')
            if(iv_call==""):iv_call = 0.10
            delta_put = calculate_delta(S, K, time_to_expiry_years, r, iv_call, option_type='put')
            delta_put_round = round(delta_put, 2)
            delta_put_roundabs = abs(delta_put_round)
            delta_price_round = round(deltaprice, 2)
            diff = abs(delta_price_round - delta_put_roundabs)
            #print(f"Put Option - Strike Price: {strike_price}, Delta: {delta_put}")
            if delta_price_round >= delta_put_roundabs and diff <= 0.03:
               print(f"New Call Option - Strike Price: {strike_price}, Delta: {delta_put}")
               return strike_price  
    




# Function to calculate time to expiry in years
def calculate_time_to_expiry(expiry_date_str, date_format="%d-%b-%Y"):
    """
    Calculates the time to expiry in years.
    
    Parameters:
    - expiry_date_str: Expiry date as a string (e.g., '28-Oct-2023')
    - date_format: Format of the expiry date string (default: '%d-%b-%Y')
    
    Returns:
    - Time to expiry in years (float)
    """
    # Current date (today)
    current_date = datetime.now()

    # Convert the expiry date string to a datetime object
    expiry_date = datetime.strptime(expiry_date_str, date_format)
    
    # Calculate the difference in days
    time_difference = expiry_date - current_date
    days_to_expiry = time_difference.days

    # Calculate the time to expiry in years
    time_to_expiry_years = days_to_expiry / 365.0

    return max(time_to_expiry_years, 0)  # Return 0 if the expiry date is in the past

# Example usage
#expiry_date_str = "26-Sep-2024"  # Nifty expiry date as a string
#time_to_expiry_years = calculate_time_to_expiry(expiry_date_str)
#print(f"Time to expiry (in years): {time_to_expiry_years}")




'''
# Function to calculate time to expiry in years
def calculate_time_to_expiry(expiry_date_str, date_format="%d-%b-%Y"):
    current_date = datetime.now()
    expiry_date = datetime.strptime(expiry_date_str, date_format)
    time_to_expiry_days = (expiry_date - current_date).days
    return time_to_expiry_days / 365.0

    '''

# Example function to apply IV calculation to the option chain
def calculate_iv_for_option_chain(option_chain_data):
    for record in option_chain_data['records']['data']:
        strike_price = record['strikePrice']
        
        if 'CE' in record:
            ce_data = record['CE']
            market_price = ce_data['lastPrice']  # This is the observed market price
            S = ce_data['underlyingValue']  # Nifty spot price
            T = calculate_time_to_expiry(ce_data['expiryDate'])  # Time to expiry in years
            K = strike_price
            r = 0.06  # Assume 6% risk-free rate
            
            iv_call = implied_volatility(S, K, T, r, market_price, option_type='call')
            print(f"Call Option - Strike Price: {strike_price}, Implied Volatility: {iv_call:.4f}")

        if 'PE' in record:
            pe_data = record['PE']
            market_price = pe_data['lastPrice']  # This is the observed market price
            S = pe_data['underlyingValue']
            T = calculate_time_to_expiry(pe_data['expiryDate'])
            K = strike_price
            r = 0.06  # Assume 6% risk-free rate
            
            iv_put = implied_volatility(S, K, T, r, market_price, option_type='put')
            print(f"Put Option - Strike Price: {strike_price}, Implied Volatility: {iv_put:.4f}")

# Assuming option_chain_data is your JSON from the NSE API
# calculate_iv_for_option_chain(option_chain_data)

# Function to calculate implied volatility
def implied_volatility(S, K, T, r, market_price, option_type):
    # Define a function that computes the difference between the Black-Scholes price and the market price
    def difference_in_price(sigma):
        return black_scholes_price(S, K, T, r, sigma, option_type) - market_price
    
    # Use Brent's method to find the root of the difference_in_price function
    # (i.e., the value of sigma that makes the difference_in_price zero)
    try:
        implied_vol = brentq(difference_in_price, 1e-6, 5.0)  # bounds for volatility [0.000001, 5]
    except Exception as e:
        print(f"Could not calculate implied volatility: {e}")
        implied_vol = 0.10
    
    return implied_vol

# Black-Scholes function to calculate the option price
def black_scholes_price(S, K, T, r, sigma, option_type):
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    
    if option_type == 'call':
        option_price = S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    elif option_type == 'put':
        option_price = K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    else:
        raise ValueError("Invalid option type. Use 'call' or 'put'.")
    
    return option_price