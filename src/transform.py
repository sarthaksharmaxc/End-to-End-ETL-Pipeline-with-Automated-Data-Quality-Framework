import pandas as pd

def clean_sales(df):
    df = df.rename(columns={
        'InvoiceNo': 'invoice_no',
        'StockCode': 'stock_code',
        'Description': 'description',
        'Quantity': 'quantity',
        'InvoiceDate': 'invoice_date',
        'UnitPrice': 'unit_price',
        'CustomerID': 'customer_id',
        'Country': 'country'
    })
    rows_before = len(df)
    removed = {}
    # rule 1 : drop duplicates
    count_before = len(df)
    df = df.drop_duplicates()
    removed['duplicates'] = count_before - len(df)

    # rule 2 : drop rows with missing values
    count_before = len(df)
    df = df.dropna(subset=['customer_id'])
    removed['missing_values'] = count_before - len(df)

    # Rule 3: remove cancelled orders. Their invoice number starts with the letter C.
    count_before = len(df)
    df = df[~df['invoice_no'].str.startswith('C', na=False)]
    removed['cancelled invoices'] = count_before - len(df)

    #rule 4 & 5: quantity and unit price should be positive
    count_before = len(df)
    df = df[df['quantity'] > 0]
    removed['quantity is 0 or negative'] = count_before - len(df)

    count_before = len(df)
    df = df[df['unit_price'] > 0] 
    removed['unit price is 0 or negative'] = count_before - len(df)

    #rule 6 : bad dates become empty and are removed 
    df = df.copy()
    df['invoice_date'] = pd.to_datetime(df['invoice_date'], format='%m/%d/%Y %H:%M', errors='coerce')
    count_before = len(df)
    df = df.dropna(subset=['invoice_date'])
    removed['bad dates'] = count_before - len(df)

    # Fix data types and formats now that the data is clean.
    df['customer_id'] = df['customer_id'].astype(int)                         
    df['invoice_date'] = df['invoice_date'].dt.strftime('%Y-%m-%d %H:%M:%S')  
    df['stock_code'] = df['stock_code'].str.upper()     
    
    return df, removed, rows_before 

def clean_users(df):
    df = df[['id', 'name', 'username', 'email', 'phone', 'website', 'address.city', 'company.name']].copy()       
    df = df.rename(columns={'address.city': 'city', 'company.name': 'company'})               
    df = df.drop_duplicates(subset=['id'])
    df['email'] = df['email'].str.lower().str.strip()
    return df

def clean_posts(df):
    df = df.rename(columns={'userId': 'user_id'})    
    df = df[['id', 'user_id', 'title', 'body']].copy()
    df = df.drop_duplicates(subset=['id'])            
    return df   


