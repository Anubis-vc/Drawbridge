import cv2
import mediapipe as mp
import pickle
import numpy as np
from numpy.linalg import norm
from insightface.app import FaceAnalysis
import argparse
from liveness import Liveness

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
    
    
    # init liveness detection 
    liveness = Liveness()


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
    YELLOW = (0, 255, 255)
    font_thickness = 2


    # vars to help with verification and tracking
    verified = False
    name = "Unknown"
    liveness_checked = False


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
                
                # get embeddings from image
                faces = app.get(frame)

                for face in faces:
                    embedding = face.embedding

                    # compare against db
                    best_match = "Unknown"
                    best_score = -1
                    for db_name, db_embedding in face_db.items():
                        score = cosine_similarity(embedding, db_embedding)
                        if score > 0.6 and score > best_score:
                            best_match = db_name
                            best_score = score
                            verified = True
                            name = db_name
                
                # https://mediapipe.readthedocs.io/en/latest/solutions/face_mesh.html
                # get bounding coordinates for framing and liveness detection
                img_height, img_width, _ = frame.shape
                # need pixel values to pass to liveness detection, mediapipe returns "normalized landmarks"
                landmarks_dict = {}
                x1, y1, x2, y2 = img_width, img_height, 0, 0
                for i, lm in enumerate(landmarks.landmark):
                    x = int(lm.x * img_width)
                    y = int(lm.y * img_height)
                    landmarks_dict[i] = (x, y)
                    x1 = min(x1, x)
                    y1 = min(y1, y)
                    x2 = max(x2, x)
                    y2 = max(y2, y)
                    
                x1, y1, x2, y2 = (
                    max(x1 - 15, 0),
                    max(y1 - 15, 0),
                    min(x2 + 15, img_width),
                    min(y2 + 15, img_height),
                )
                
                liveness_checked = liveness.calculate_liveness(landmarks_dict)

                # Determine frame color based on verification and liveness
                if verified and liveness_checked:
                    frame_color = GREEN
                    status_text = f"{name} Blinks: {liveness.total_blinks}"
                elif verified and not liveness_checked:
                    frame_color = YELLOW
                    status_text = f"{name} Blinks: {liveness.total_blinks}"
                else:
                    frame_color = RED
                    status_text = "Unknown"

                # draw frame and show text
                cv2.rectangle(frame, (x1, y1), (x2, y2), frame_color, 2)
                
                # Display name/status
                (text_width, text_height), baseline = cv2.getTextSize(
                    status_text, font, font_scale, font_thickness
                )
                cv2.putText(
                    frame,
                    status_text,
                    ((x1 + x2 - text_width) // 2, y2 + text_height + 15),
                    font,
                    font_scale,
                    frame_color,
                    font_thickness,
                )
            
        # reset flags and names if face disappears
        else:
            verified = False
            name = "Unknown"
            liveness.reset()
            

        cv2.imshow("Face Detection Mesh", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break


    # housekeeping
    cap.release()
    cv2.destroyAllWindows()
