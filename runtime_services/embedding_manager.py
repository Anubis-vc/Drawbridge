import io
import numpy as np


class EmebeddingManager:
    def __init__(self, db):
        self._db = db
        self.embeddings: dict[str, np.ndarray] = self._load_all_embeddings()

    def _load_all_embeddings(self) -> dict[str, np.ndarray]:
        cache: dict[str, np.ndarray] = {}
        for row in self._db.get_all_users():
            blob = row["embedding"]
            if blob is None:
                continue
            try:
                embedding = np.load(io.BytesIO(blob), allow_pickle=False)
            except (ValueError, OSError):
                # Skip corrupt or truncated blobs; they will be regenerated on next update.
                continue
            cache[row["name"]] = embedding
        return cache

    # listener callback to update embeddings on database changes
    def on_embedding_update(self, user_name: str, embedding: np.ndarray | None):
        if embedding is not None:
            self.embeddings[user_name] = embedding
        else:
            self.embeddings.pop(user_name, None)
        print(f"Updated embeddings for {user_name}. Total embeddings: {len(self.embeddings)}")