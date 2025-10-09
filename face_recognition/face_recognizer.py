import numpy as np
from insightface.app import FaceAnalysis


class FaceRecognizer:
    def __init__(self):
        self.model = "buffalo_s"
        self.providers = ["CPUExecutionProvider"]
        self.similarity_threshold = None
        self.verified = False

        self.app = FaceAnalysis(name=self.model, providers=["CPUExecutionProvider"])
        self.app.prepare(ctx_id=0, det_size=(640, 640))

    def run_facial_recognition(self, frame, face_db) -> tuple[str, int]:
        faces = self.app.get(frame)
        best_match = "Unknown"
        best_score = -1

        for face in faces:
            embedding = face.normed_embedding
            for db_name, db_embedding in face_db.items():
                # simple dot product for cosine similarity since vectors are normalized
                score = np.dot(embedding, db_embedding)
                if score > self.similarity_threshold:
                    if score > best_score:
                        best_match = db_name
                        best_score = score
                    self.verified = True
                else:
                    self.verified = False
        return (best_match, best_score)

    def update_config(self, config):
        self.model = config["model"]
        self.similarity_threshold = config["similarity_threshold"]
        print(
            f"FaceRecognizer update - Model {self.model}, Threshold {self.similarity_threshold}"
        )
        # TODO: configure model to actually change. requires adjustment to db as well

    def reset(self):
        self.verified = False
