import io
import numpy as np

from utils.enums import AccessLevel


class EmebeddingManager:
    def __init__(self, db):
        self._db = db
        self.embeddings: dict[int, np.ndarray] = {}
        self.users: dict[int, tuple[str, AccessLevel]] = {}
        self._load()

    def _load(self):
        for row in self._db.get_all_users():
            # user always gets added
            access = AccessLevel(row["access_level"])
            self.users[row["id"]] = (row["name"], access)

            # process embeddings separately
            blob = row["embedding"]
            if blob is None:
                continue
            try:
                embedding = np.load(io.BytesIO(blob), allow_pickle=False)
            except (ValueError, OSError):
                # Skip corrupt or truncated blobs; they will be regenerated on next update.
                continue
            self.embeddings[row["id"]] = embedding

    # listener callback to update embeddings on database changes
    def on_embedding_update(self, user_id: int, embedding: np.ndarray | None):
        if embedding is not None:
            self.embeddings[user_id] = embedding
        else:
            self.embeddings.pop(user_id, None)
        print(
            f"Updated embeddings for {user_id}. Total embeddings: {len(self.embeddings)}"
        )

    def on_user_update(
        self,
        user_id: int,
        name: str | None = None,
        access: AccessLevel | None = None,
        new_user: tuple[str, AccessLevel] | None = None,
        delete_user: bool = False,
    ):
        if delete_user:
            self.users.pop(user_id, None)
            self.embeddings.pop(user_id, None)
        elif new_user:
            self.users[user_id] = new_user
        else:
            old = self.users.get(user_id)
            if old is None:
                # Cache miss; fetch from DB to stay in sync
                row = self._db.get_user(user_id)
                if row is None:
                    return
                old = (row["name"], row["access_level"])
            new_name = name if name is not None else old[0]
            new_access = access if access is not None else old[1]
            self.users[user_id] = (new_name, new_access)
