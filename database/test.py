

import sqlite3

def query_db():
    users_query = """PRAGMA table_info(users);"""
    images_query = """PRAGMA table_info(images);"""
    
    try:
        with sqlite3.connect('face.db') as conn:
            cursor = conn.cursor()
            cursor.execute(users_query)
            print(cursor.fetchall())
            cursor.execute(images_query)
            print()
            print(cursor.fetchall())
    except Exception as e:
        print("error creating database: ", e)


if __name__ == '__main__':
    query_db()
    