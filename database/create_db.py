import sqlite3

def create_db():
    users_query = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            access_level TEXT NOT NULL,
            embedding BLOB
        )
    """
    
    images_query = """
        CREATE TABLE IF NOT EXISTS images (
            img_name TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            embedding BLOB NOT NULL,
            PRIMARY KEY (img_name, user_id),
            FOREIGN KEY (user_id)
                REFERENCES users (id)
                ON DELETE CASCADE
                ON UPDATE NO ACTION
        )
    """
    
    try:
        with sqlite3.connect('face.db') as conn:
            cursor = conn.cursor()
            cursor.execute(users_query)
            cursor.execute(images_query)
            conn.commit()
    except Exception as e:
        print("error creating database: ", e)


if __name__ == '__main__':
    create_db()
    