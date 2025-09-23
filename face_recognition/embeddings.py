import cv2
import os
import pickle
from insightface.app import FaceAnalysis
import numpy as np
import argparse


if __name__ == "__main__":
    # checking which model is desired for embeddings
    parser = argparse.ArgumentParser(
        description="Program to create embeddings for facial recognition"
    )
    parser.add_argument("-s", "--small", action="store_true")
    args = parser.parse_args()

    # init FaceAnalysis object to create embeddings
    model = "buffalo_s" if args.small else "buffalo_l"
    print(f"Using model: {model}")
    app = FaceAnalysis(
        name=model, providers=["CPUExecutionProvider"]
    )  # change to gpu later
    app.prepare(ctx_id=0, det_size=(640, 640))

    # init basic db and lookup directory
    face_db = {}
    BASE_DIR = "/Users/anubis/Desktop/Personal_Projects/lock-override-face-recognition/face_recognition/known_images"

    for name in os.listdir(BASE_DIR):
        print(f"Getting embeddings for {name}")

        person_path = os.path.join(BASE_DIR, name)
        if os.path.isdir(person_path):
            embeddings = []
            for img_file in os.listdir(person_path):
                img_path = os.path.join(person_path, img_file)

                # image processing
                # https://github.com/deepinsight/insightface/blob/master/python-package/insightface/app/face_analysis.py
                image = cv2.imread(img_path)
                if image is not None:
                    faces = app.get(image)
                    if faces:
                        # take the largest face if multiple
                        face = max(
                            faces,
                            key=lambda f: (
                                (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1])
                            ),
                        )
                        embeddings.append(face.embedding)

        # take average embedding for better accuracy
        if embeddings:
            avg_embedding = np.mean(embeddings, axis=0)
            face_db[name] = avg_embedding
        else:
            print(f"No embeddings found for {name}")

    # save db to files
    with open("face_db.pkl" if not args.small else "face_db_small.pkl", "wb") as f:
        pickle.dump(face_db, f)
