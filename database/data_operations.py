import sqlite3
from contextlib import contextmanager
import numpy as np
import io

from utils.enums import AccessLevel


class Database:
    def __init__(self, db_path="./database/faces.db"):
        self.db_path = db_path
        self._init_db()
        self._listener = None

    def _init_db(self):
        users_query = """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                access_level TEXT NOT NULL,
                num_embeddings INTEGER,
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
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(users_query)
                cursor.execute(images_query)
                conn.commit()
        except Exception as e:
            print("error creating database: ", e)

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Access columns by name
        conn.execute(
            "PRAGMA foreign_keys = ON"
        )  # needed per connection to make fk checks work
        try:
            yield conn
        finally:
            conn.close()

    def register_listener(self, listener):
        self._listener = listener

    def _notify_embedding_listener(self, user_id: int, embedding: np.ndarray):
        if self._listener:
            self._listener.on_embedding_update(user_id, embedding)

    def _notify_user_listener(
        self,
        user_id: int,
        name: str | None = None,
        access: AccessLevel | None = None,
        new_user: tuple[str, AccessLevel] | None = None,
        delete_user: bool = False,
    ):
        if self._listener:
            self._listener.on_user_update(user_id, name, access, new_user, delete_user)

    def add_user(self, name, access_level):
        with self._get_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO users (name, access_level, num_embeddings, embedding)
                VALUES (?, ?, 0, NULL)""",
                (name, access_level),
            )
            user_id = cursor.lastrowid
            conn.commit()
        access_enum = AccessLevel(access_level)
        self._notify_user_listener(user_id, new_user=(name, access_enum))
        return user_id

    def get_user(self, user_id):
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            return cursor.fetchone()

    def get_all_users(self):
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM users ORDER BY name ASC")
            return cursor.fetchall()

    def delete_user(self, user_id):
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
            deleted = cursor.rowcount
            conn.commit()
        if deleted:
            self._notify_user_listener(user_id, delete_user=True)
            self._notify_embedding_listener(user_id, None)
        else:
            raise ValueError(f"User {user_id} not found")

    def update_name(self, user_id: int, name: str):
        with self._get_connection() as conn:
            cursor = conn.execute(
                "UPDATE users SET name = ? WHERE id = ?", (name, user_id)
            )
            if cursor.rowcount == 0:
                raise ValueError(f"User {user_id} not found")
            conn.commit()
            user_row = conn.execute(
                "SELECT * FROM users WHERE id = ?", (user_id,)
            ).fetchone()
        if user_row is None:
            raise ValueError(f"User {user_id} not found after update")
        access_enum = AccessLevel(user_row["access_level"])
        self._notify_user_listener(user_id, name=user_row["name"], access=access_enum)
        return user_row

    def update_access_level(self, user_id, access_level: AccessLevel):
        with self._get_connection() as conn:
            cursor = conn.execute(
                "UPDATE users SET access_level = ? WHERE id = ?",
                (access_level.value, user_id),
            )
            if cursor.rowcount == 0:
                raise ValueError(f"User {user_id} not found")
            conn.commit()
        access_enum = AccessLevel(access_level)
        self._notify_user_listener(user_id, access=access_enum)

    def get_images_for_user(self, user_id: int):
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT img_name FROM images WHERE user_id = ?", (user_id,)
            )
            if cursor.rowcount == 0:
                raise ValueError(f"User {user_id} not found")
            return cursor.fetchall()

    def add_image(self, img_name, user_id, normed_embedding: np.ndarray):
        """Creates an embedding for an image and updates the users avg embedding"""
        buffer = io.BytesIO()
        np.save(buffer, normed_embedding, allow_pickle=False)
        blob = buffer.getvalue()

        with self._get_connection() as conn:
            # first add to images table
            conn.execute(
                "INSERT INTO images (img_name, user_id, embedding) VALUES (?, ?, ?)",
                (img_name, user_id, blob),
            )

            # then recompute average for user
            cursor = conn.execute(
                "SELECT name, num_embeddings, embedding FROM users WHERE id= ?",
                (user_id,),
            )
            user_row = cursor.fetchone()
            old_avg = (
                np.load(io.BytesIO(user_row[2]), allow_pickle=False)
                if user_row[2]
                else None
            )
            num_embeddings = user_row[1] or 0

            if old_avg is None or num_embeddings == 0:
                new_avg = normed_embedding
                num_embeddings += 1
            else:
                new_avg = ((old_avg * num_embeddings) + normed_embedding) / (
                    num_embeddings + 1
                )
                num_embeddings += 1
                new_avg /= np.linalg.norm(new_avg)  # must renormalize after averaging

            avg_buffer = io.BytesIO()
            np.save(avg_buffer, new_avg, allow_pickle=False)
            conn.execute(
                "UPDATE users SET num_embeddings = ?, embedding = ? WHERE id = ?",
                (num_embeddings, avg_buffer.getvalue(), user_id),
            )

            # commit only if everything succeeds
            conn.commit()
            self._notify_embedding_listener(user_id, new_avg)

    def delete_image(self, img_name, user_id):
        """Delete the image embedding then update the user info"""
        with self._get_connection() as conn:
            # first get the embedding
            cursor = conn.execute(
                "SELECT embedding FROM images WHERE img_name = ? AND user_id = ?",
                (img_name, user_id),
            )
            img_row = cursor.fetchone()
            embedding_to_delete = np.load(io.BytesIO(img_row[0]), allow_pickle=False)

            # update user embeddings
            cursor = conn.execute(
                "SELECT name, num_embeddings, embedding FROM users WHERE id = ?",
                (user_id,),
            )
            user = cursor.fetchone()
            old_avg = (
                np.load(io.BytesIO(user[2]), allow_pickle=False) if user[2] else None
            )
            num_embeddings = user[1]

            new_avg = None
            if num_embeddings <= 1:
                conn.execute(
                    "UPDATE users SET num_embeddings = 0, embedding = NULL WHERE id = ?",
                    (user_id,),
                )
            else:
                new_avg = (old_avg * num_embeddings - embedding_to_delete) / (
                    num_embeddings - 1
                )
                num_embeddings -= 1
                new_avg /= np.linalg.norm(new_avg)
                avg_buffer = io.BytesIO()
                np.save(avg_buffer, new_avg, allow_pickle=False)
                conn.execute(
                    "UPDATE users SET num_embeddings = ?, embedding = ? WHERE id = ?",
                    (num_embeddings, avg_buffer.getvalue(), user_id),
                )

            # delete embedding from old table
            conn.execute(
                "DELETE FROM images WHERE img_name = ? AND user_id = ?",
                (img_name, user_id),
            )

            # commit only if everything else succeeds
            conn.commit()
            self._notify_embedding_listener(user_id, new_avg)


db = Database()  # another singleton to be used around the project
