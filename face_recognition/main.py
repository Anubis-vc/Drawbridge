import cv2
import mediapipe as mp
import pickle
import numpy as np
from numpy.linalg import norm
from insightface.app import FaceAnalysis
import argparse


# allowing usage of small model during dev since i don't have a gpu yet
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--small", action="store_true")
    args = parser.parse_args()

    model = "buffalo_s" if args.small else "buffalo_l"
    print(f"Using model {model}")


    # load the embeddings
    with open("face_db.pkl" if not args.small else "face_db_small.pkl", "rb") as f:
        face_db = pickle.load(f)


    # initialize recognition things
    def cosine_similarity(a, b):
        return np.dot(a, b) / (norm(a) * norm(b))


    app = FaceAnalysis(name=model, providers=["CPUExecutionProvider"])
    app.prepare(ctx_id=0, det_size=(640, 640))


    # init mediapipe objects for detection and drawing
    mp_face_mesh = mp.solutions.face_mesh
    # mp_drawing = mp.solutions.drawing_utils
    # mp_drawing_styles = mp.solutions.drawing_styles

    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,  # using attention
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7,
    )


    # init video capture and get lower res for faster processing
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    print(f"Width: {cap.get(cv2.CAP_PROP_FRAME_WIDTH)}")
    print(f"Height: {cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")


    # vars for text
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    GREEN = (0, 255, 0)
    RED = (0, 0, 255)
    font_thickness = 2


    # vars to help with verification and tracking
    verified = False
    name = "Unknown"


    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame")
            break

        # convert to rgb for mediapipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # run through detection algorithm
        results = face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            for landmarks in results.multi_face_landmarks:
                # https://mediapipe.readthedocs.io/en/latest/solutions/face_mesh.html
                # TODO: use mediapipe landmarks to implement liveness detection

                # get bounding coordinates for framing
                img_height, img_width, _ = frame.shape
                # taking [0,1] normalized coordinates and finding the bounding box
                x_coords = [int(lm.x * img_width) for lm in landmarks.landmark]
                y_coords = [int(lm.y * img_height) for lm in landmarks.landmark]
                x1, y1, x2, y2 = (
                    max(min(x_coords) - 15, 0),
                    max(min(y_coords) - 15, 0),
                    min(max(x_coords) + 15, img_width),
                    min(max(y_coords), img_height),
                )

                # draw frame and show text
                cv2.rectangle(frame, (x1, y1), (x2, y2), GREEN if verified else RED, 2)
                (text_width, text_height), baseline = cv2.getTextSize(
                    name, font, font_scale, font_thickness
                )
                cv2.putText(
                    frame,
                    name,
                    ((x1 + x2 - text_width) // 2, y2 + text_height + 15),
                    font,
                    font_scale,
                    GREEN if verified else RED,
                    font_thickness,
                )

                # get embeddings from image
                faces = app.get(frame)

                for face in faces:
                    embedding = face.embedding

                    # compare against db
                    best_match = "Unknown"
                    best_score = -1
                    for db_name, db_embedding in face_db.items():
                        score = cosine_similarity(embedding, db_embedding)
                        if score > 0.5 and score > best_score:
                            best_match = db_name
                            best_score = score
                            verified = True
                            name = db_name
            
        # reset flags and names if face disappears
        else:
            verified = False
            name = "Unknown"
            

        cv2.imshow("Face Detection Mesh", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break


    # housekeeping
    cap.release()
    cv2.destroyAllWindows()
