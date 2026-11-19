import pandas as pd
import requests 

def extract_csv(path):
    df = pd.read_csv(path, encoding='ISO-8859-1', dtype={'InvoiceNo': str, 'StockCode': str}) 
    #encoding is set to ISO-8859-1 to handle special characters in the data    print('csv loaded is ', len(df))
    return df

def extract_api(endpoint):
    url = 'https://jsonplaceholder.typicode.com/' + endpoint
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers, timeout=10) 
    response.raise_for_status()

    data = response.json() # the api gives us a list of dictionaries, so we can use json_normalize to convert it to a dataframe
    df = pd.json_normalize(data)
    print('api data loaded is ', len(df))
    return df

