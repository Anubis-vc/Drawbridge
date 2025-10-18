import numpy as np
from insightface.app import FaceAnalysis

from utils.enums import AccessLevel


class FaceRecognizer:
    def __init__(self):
        self.model = "buffalo_s"
        self.providers = ["CPUExecutionProvider"]
        self.similarity_threshold = None
        self.verified = False

        self.app = FaceAnalysis(name=self.model, providers=["CPUExecutionProvider"])
        self.app.prepare(ctx_id=0, det_size=(640, 640))

    def run_facial_recognition(
        self,
        frame,
        face_db: dict[int, np.ndarray],
        user_db: dict[int, tuple[str, AccessLevel]],
    ) -> tuple[str, float, AccessLevel]:
        faces = self.app.get(frame)
        best_match = "Unknown"
        best_score = -1
        access = AccessLevel.STRANGER

        for face in faces:
            embedding = face.normed_embedding
            for user_id, db_embedding in face_db.items():
                # simple dot product for cosine similarity since vectors are normalized
                score = np.dot(embedding, db_embedding)
                if score > self.similarity_threshold:
                    if score > best_score:
                        user_tuple = user_db[user_id]
                        best_match = user_tuple[0]
                        best_score = score
                        access = user_tuple[1]
        # changed, now multiple faces will not overwrite the verified check
        self.verified = best_score > self.similarity_threshold
        return (best_match, best_score, access)

    def update_config(self, config):
        self.model = config["model"]
        self.similarity_threshold = config["similarity_threshold"]
        print(
            f"FaceRecognizer update - Model {self.model}, Threshold {self.similarity_threshold}"
        )
        # TODO: configure model to actually change. requires adjustment to db as well

    def reset(self):
        self.verified = False
