import os
from datetime import datetime

import pandas as pd

SALES_COLUMNS = ['invoice_no', 'stock_code', 'description', 'quantity',
                 'invoice_date', 'unit_price', 'customer_id', 'country']
USERS_COLUMNS = ['id', 'name', 'username', 'email', 'phone', 'website', 'city', 'company']
POSTS_COLUMNS = ['id', 'user_id', 'title', 'body']

def make_result(check_name, passed, details):
    """Packs the answer of one check into a dictionary (used by every check below)."""
    if passed:
        status = 'PASS'
    else:
        status = 'FAIL'
    return {
        'check': check_name,
        'status': status,
        'details': details,
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }

def check_row_count(conn, table_name, expected_rows):
 actual_rows = conn.execute('SELECT COUNT(*) FROM ' + table_name).fetchone()[0]
 passed = (actual_rows == expected_rows)
 return make_result('row count' + table_name, passed, f'expected {expected_rows}, got {actual_rows}')

def check_nulls(df, table_name, columns):
   total_nulls = 0
   for col in columns:
       total_nulls = total_nulls + df[col].isna().sum()
   passed = (total_nulls == 0)
   return make_result('nulls' + table_name, passed, f'total nulls: {total_nulls}')

def check_duplicates(df, table_name, key_columns=None):
    duplicate_count = df.duplicated(subset=key_columns).sum()
    passed = (duplicate_count == 0)
    return make_result('duplicates' + table_name, passed, f'total duplicates: {duplicate_count}')

def check_referential_integrity(child_df, child_col, parent_df, parent_col, label):
    exists_in_parent = child_df[child_col].isin(parent_df[parent_col])
    orphan_count = (~exists_in_parent).sum()     
    passed = (orphan_count == 0)
    return make_result('foreign key ' + label, passed, f'{orphan_count} rows have no matching parent')

def check_positive_values(df, table_name, columns):
    negative_count = (df[columns] <= 0).sum()
    passed = (negative_count == 0)
    return make_result(f'{table_name}.{columns} > 0', passed, f'total negative values: {negative_count}')

def check_schema(df, table_name, expected_columns):
    """Does the table have exactly the columns we expect? (names only, order does not matter)"""
    actual_columns = list(df.columns)
    passed = (sorted(actual_columns) == sorted(expected_columns))
    if passed:
        details = 'all expected columns are there'
    else:
        details = f'expected {expected_columns} but found {actual_columns}'
    return make_result('schema ' + table_name, passed, details)


def run_all_checks(conn, users, posts, rows_before, removed):

    sales_db = pd.read_sql('SELECT * FROM sales', conn)
    users_db = pd.read_sql('SELECT * FROM users', conn)
    posts_db = pd.read_sql('SELECT * FROM posts', conn)

    results = []

    # row count 
    expected_sales_rows = rows_before - sum(removed.values())
    results.append(check_row_count(conn, 'sales', expected_sales_rows)) 
    results.append(check_row_count(conn, 'users', len(users)))
    results.append(check_row_count(conn, 'posts', len(posts)))

    #nulls 
    results.append(check_nulls(sales_db, 'sales',
                               ['invoice_no', 'stock_code', 'quantity', 'invoice_date', 'unit_price', 'customer_id']))
    results.append(check_nulls(users_db, 'users', ['id', 'email']))
    results.append(check_nulls(posts_db, 'posts', ['id', 'user_id']))

    #duplicates
    results.append(check_duplicates(sales_db, 'sales'))
    results.append(check_duplicates(users_db, 'users', ['id']))
    results.append(check_duplicates(posts_db, 'posts', ['id']))

    #foreign key check
    results.append(check_referential_integrity(posts_db, 'user_id', users_db, 'id', 'posts.user_id -> users.id'))

    # 5. Value range
    results.append(check_positive_values(sales_db, 'sales', 'quantity'))
    results.append(check_positive_values(sales_db, 'sales', 'unit_price'))

    # 6. Schema
    results.append(check_schema(sales_db, 'sales', SALES_COLUMNS))
    results.append(check_schema(users_db, 'users', USERS_COLUMNS))
    results.append(check_schema(posts_db, 'posts', POSTS_COLUMNS))

    return results

def write_report(results):
    """Prints the results on screen and saves them in reports/quality_report.csv"""
    print('=' * 80)
    print('DATA QUALITY REPORT')
    print('=' * 80)

    passed_count = 0
    for r in results:
        print(r['status'], '|', r['check'], '|', r['details'])
        if r['status'] == 'PASS':
            passed_count = passed_count + 1

    print('=' * 80)
    print(passed_count, 'passed,', len(results) - passed_count, 'failed,', len(results), 'checks in total')

    os.makedirs('reports', exist_ok=True)
    pd.DataFrame(results).to_csv('reports/quality_report.csv', index=False)
    print('Saved: reports/quality_report.csv')
 

