import json
import kiteconnect.exceptions as ex
import logging,requests
from urllib.parse import urljoin
import pandas as pd
from io import StringIO
from kiteconnect import KiteConnect, KiteTicker
log = logging.getLogger(__name__)
#https://kite.zerodha.com/oms

class KiteApp(KiteConnect):
    def __init__(self,reqsession, api_key, userid, enctoken,debug=False):
        self.api_key = api_key
        self.reqsession = reqsession
        self.user_id = userid
        self.enctoken = enctoken
        self.debug = debug 
        self.session_expiry_hook = None
        self.root2 = "https://kite.zerodha.com/oms"
        self.headers = {
            "x-kite-version": "3",
            'Authorization': 'enctoken {}'.format(self.enctoken)
        }
        KiteConnect.__init__(self, api_key=api_key)

    def kws(self):
        return KiteTicker(api_key='kitefront', access_token=self.enctoken+"&user_id="+self.user_id, root='wss://ws.kite.trade')

    def _request(self, route, method, url_args=None,query_params=None, params=None, is_json=False):
        """Make an HTTP request."""
        # Form a restful URL
        if url_args:
            uri = self._routes[route].format(**url_args)
        else:
            uri = self._routes[route]
        if uri.endswith("positions"):
             
             
             url = self.root2 +uri
        else:
             self.root = self.root2
             url = self.root+uri# urljoin(self.root, uri)
             #uriIn = 'https://api.kite.trade';
             #url = uriIn+uri# urljoin(self.root, uri)
          
        #https://api.kite.trade
        
       # url = self.root+uri# urljoin(self.root, uri)
        headers = self.headers
        if self.debug:
            log.debug("Request: {method} {url} {params} {headers}".format(method=method, url=url, params=params, headers=headers))
        try:
            json_data = params if (method in ["POST", "PUT"] and is_json) else None
            data = params if (method in ["POST", "PUT"] and not is_json) else None
            timeout = self.timeout if self.timeout else 10
            verify_ssl = not self.disable_ssl if self.disable_ssl is not None else True
            r = self.reqsession.request(method,
                                        url,
                                        json=json_data,
                                        data=data,
                                        params=params if method in ["GET", "DELETE"] else None,
                                        headers=headers,
                                        verify=verify_ssl,
                                        allow_redirects=True,
                                        timeout=timeout,
                                        proxies=self.proxies)
        # Any requests lib related exceptions are raised here - http://docs.python-requests.org/en/master/_modules/requests/exceptions/
        except Exception as e:
            raise e

        if self.debug:
            log.info("Response: {code} {content}".format(code=r.status_code, content=r.content))

        # Validate the content type.
        #log.info("Response: {code} {content}".format(code=r.status_code, content=r.content))
        if "json" in r.headers["content-type"]:
            try:
                data = json.loads(r.content.decode("utf8"))
            except ValueError:
                raise ex.DataException("Couldn't parse the JSON response received from the server: {content}".format(
                    content=r.content))

            # api error
            if data.get("error_type"):
                # Call session hook if its registered and TokenException is raised
                if self.session_expiry_hook and r.status_code == 403 and data["error_type"] == "TokenException":
                    self.session_expiry_hook()

                # native Kite errors
                exp = getattr(ex, data["error_type"], ex.GeneralException)
                raise exp(data["message"], code=r.status_code)

            return data["data"]
        elif "csv" in r.headers["content-type"]:
            return r.content
        else:
            raise ex.DataException("Unknown Content-Type ({content_type}) with response: ({content})".format(
                content_type=r.headers["content-type"],
                content=r.content))
    def fetch_nse_instruments(self):
        """
        Fetches the instrument list for NSE from the Kite API.
        Returns a list of instruments in CSV format.
        """
        url = "https://api.kite.trade/instruments"
        method = "GET"
        headers = {"Content-Type": "application/json"}

        if self.debug:
            self.log.debug(f"Request: {method} {url} {headers}")

        try:
            timeout = self.timeout if self.timeout else 10
            verify_ssl = not self.disable_ssl if self.disable_ssl is not None else True

            response = self.reqsession.request(
                method=method,
                url=url,
                headers=headers,
                verify=verify_ssl,
                allow_redirects=True,
                timeout=timeout,
                proxies=self.proxies
            )

        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")

        if self.debug:
            self.log.info(f"Response: {response.status_code} {response.content}")

        # Check response status
        if response.status_code != 200:
            raise Exception(f"HTTP Error {response.status_code}: {response.text}")

        # Since the instrument list is in CSV format, return the raw text
        return response.text
    def get_nifty_option_chain(self):
        """
        Fetch NIFTY 50 option chain from the instrument list.
        Returns a Pandas DataFrame.
        """
        # Fetch the instrument list
        csv_data = self.fetch_nse_instruments()

        # Convert CSV to DataFrame
        df = pd.read_csv(StringIO(csv_data))
        json_data = df.to_json(orient="records")
        

        # Filter for NIFTY 50 options (OPTIDX)
        nifty_options = df[(df["segment"] == "NFO") & 
                           (df["name"] == "NIFTY") & 
                           (df["instrument_type"] == "OPTIDX")]

        return nifty_options  # Returns a DataFrame with filtered option data    
    def get_nifty_50_token(self):
        #"""
        #Fetch NIFTY 50 instrument token from the instrument list.
        #Returns the token for fetching live prices.
        #"""
        csv_data = self.fetch_nse_instruments()
        df = pd.read_csv(StringIO(csv_data))

        # Filter for NIFTY 50 Index
        nifty_index = df[(df["segment"] == "INDICES") & 
                         (df["name"] == "NIFTY 50") & 
                         (df["instrument_type"] == "EQ")]

        if nifty_index.empty:
            raise Exception("NIFTY 50 Instrument Token not found")

        return int(nifty_index.iloc[0]["instrument_token"])  # Return the first token found 
    def get_nifty_50_price(self):
        """
        Fetches the current market price of NIFTY 50 using its instrument token.
        """
        nifty_token = self.get_nifty_50_token()
        instrument_key = f"{nifty_token}"

        try:
            quote = self.quote(instrument_key)
            print(f"Quote response: {quote}")
            return quote[instrument_key]["last_price"]  # Extract the last traded price
        except Exception as e:
            raise Exception(f"Failed to fetch NIFTY 50 price: {str(e)}")
        
    def quote(self, instruments):
        """Fetch market quotes for given instruments."""
        if isinstance(instruments, list):
            instruments = ",".join(instruments)  # Convert list to comma-separated string

        #headers = {'Authorization':f'Enctoken {self.enctoken}'}
        self.enctoken = self.enctoken.strip()
        headers = {'Authorization': f'enctoken {self.enctoken}'}
        url = f"https://api.kite.trade/user/profile"
        print(f"Fetching data from: {url}")  
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error fetching quote: {response.text}")

def login_with_credentials(userid, password, twofa):
    reqsession = requests.Session()
    r = reqsession.post('https://kite.zerodha.com/api/login', data={
        "user_id": userid,
        "password": password
    })

    r = reqsession.post('https://kite.zerodha.com/api/twofa', data={
        "request_id": r.json()['data']['request_id'],
        "twofa_value": twofa,
        "user_id": r.json()['data']['user_id']
    })
    enctoken = r.cookies.get('enctoken')
    with open('utils/enctoken.txt', 'w') as wr:
        wr.write(enctoken)
        
    