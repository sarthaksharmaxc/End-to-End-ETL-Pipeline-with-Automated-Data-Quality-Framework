import sqlite3

def load_to_database(sales,users,posts,db_path):
    conn = sqlite3.connect(db_path)
    sales.to_sql('sales',conn, if_exists='replace', index=False)
    users.to_sql('users',conn, if_exists='replace', index=False)
    posts.to_sql('posts',conn, if_exists='replace', index=False)

    conn.close()
    print('Saved tables sales, users and posts to database at ', db_path)