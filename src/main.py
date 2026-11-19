import sqlite3
from src.extract import extract_csv, extract_api
from src.transform import clean_sales, clean_users, clean_posts
from src.load import load_to_database
from src.quality_checks import run_all_checks, write_report 

CSV_PATH = 'data/raw/online_retail.csv'
DB_PATH = 'etl.db'

def main():
    #step 1: Extract data from CSV and API
    print ('Extracting data from CSV...')
    raw_sales_data = extract_csv(CSV_PATH)
    raw_posts_data = extract_api('posts')
    raw_users_data = extract_api('users')

    #step 2: transform raw data into clean data
    print ('Transforming data...')
    sales, removed, rows_before = clean_sales(raw_sales_data)
    users = clean_users(raw_users_data)
    posts = clean_posts(raw_posts_data)

    print('sales rows before cleaning: ', rows_before)
    for reason, count in removed.items():
        print('removed', count , 'rows', reason)
    print('sales rows after cleaning: ', len(sales))

    #step 3: load clean data into database
    print('loading data into database...')
    load_to_database(sales, users, posts, DB_PATH)
    conn = sqlite3.connect(DB_PATH)

    #step 4: quality checks
    results = run_all_checks(conn,users, posts, rows_before, removed)
    conn.close()

    print(' REPORT')
    write_report(results)


if __name__ == '__main__':
    main()





    