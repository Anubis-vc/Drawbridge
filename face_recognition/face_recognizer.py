import pickle
import numpy as np
from numpy.linalg import norm
from insightface.app import FaceAnalysis


class FaceRecognizer:
    def __init__(
        self,
        model: str,
        providers: list[str] = ["CPUExecutionProvider"],
        similarity_threshold: float = 0.65,
    ):
        self.model = model
        self.providers = providers
        self.similarity_threshold = similarity_threshold
        self.verified = False

        self.app = FaceAnalysis(name=model, providers=["CPUExecutionProvider"])
        self.app.prepare(ctx_id=0, det_size=(640, 640))

        with open(
            "face_db.pkl" if model == "buffalo_l" else "face_db_small.pkl", "rb"
        ) as f:
            self.face_db = pickle.load(f)  # TODO: replace eventually with vector db
            print("loaded embeddings")

    def cosine_similarity(self, a, b):
        return np.dot(a, b) / (norm(a) * norm(b))

    def run_facial_recognition(self, frame) -> tuple[str, int]:
        faces = self.app.get(frame)
        best_match = "Unknown"
        best_score = -1

        for face in faces:
            embedding = face.embedding
            for db_name, db_embedding in self.face_db.items():
                score = self.cosine_similarity(embedding, db_embedding)
                print(score)
                if (
                    score > self.similarity_threshold and score > best_score
                ):  # TODO: allow configurable strictness
                    best_match = db_name
                    best_score = score
                    self.verified = True
        return (best_match, best_score)

    def reset(self):
        self.verified = False
