import pickle
import numpy as np
from numpy.linalg import norm
from insightface.app import FaceAnalysis


class FaceRecognizer:
    def __init__(
        self,
        model: str,
        similarity_threshold: float = 0.65,
        providers: list[str] = ["CPUExecutionProvider"] # TODO: configure providers
    ):
        self.model = model
        self.providers = providers
        self.similarity_threshold = similarity_threshold
        self.verified = False

        self.app = FaceAnalysis(name=model, providers=["CPUExecutionProvider"])
        self.app.prepare(ctx_id=0, det_size=(640, 640))

        self.face_db = self.__load_embeddings(model)
    
    def __load_embeddings(self, model):
        with open(
            "face_db.pkl" if model == "buffalo_l" else "face_db_small.pkl", "rb"
        ) as f:
            return pickle.load(f)  # TODO: replace eventually with vector db

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
                if score > self.similarity_threshold:
                    if score > best_score:
                        best_match = db_name
                        best_score = score
                    self.verified = True
                else:
                    self.verified = False
        return (best_match, best_score)
    
    def update_config(self, model, similarity_threshold):
        if self.model != model:
            self.app = FaceAnalysis(name=model, providers=["CPUExecutionProvider"])
            self.face_db = self.__load_embeddings(model)
            print("updated model")
        
        if self.similarity_threshold != similarity_threshold:
            self.similarity_threshold = similarity_threshold
            print("updated similarity threshold")

    def reset(self):
        self.verified = False
