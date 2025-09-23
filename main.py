from face_recognition.liveness import Liveness
from face_recognition.face_recognizer import FaceRecognizer
# TODO: import and configure notifications

import cv2
import mediapipe as mp
import argparse

# allowing usage of small model during dev since i don't have a gpu yet
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--small", action="store_true")
    args = parser.parse_args()

    model = "buffalo_s" if args.small else "buffalo_l"
    print(f"Using model {model}")
    
    
    face_recognition = FaceRecognizer(model)
    liveness = Liveness()
    

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


    # Process video at lower res for faster processing
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 720)
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


    # vars to help with live feed
    name = "Unknown"
    face_similarity_score = -1


    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame")
            break

        # convert to rgb for mediapipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # run through mediapipe detection algorithm
        results = face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            for landmarks in results.multi_face_landmarks:
                
                # retrieve embedding for each face in the image
                name, face_similarity_score = face_recognition.run_facial_recognition(frame)
                
                # https://mediapipe.readthedocs.io/en/latest/solutions/face_mesh.html
                # get bounding coordinates for framing and liveness detection
                img_height, img_width, _ = frame.shape
                # need pixel values to pass to liveness detection, mediapipe returns "normalized landmarks"
                landmarks_dict = {}
                x1, y1, x2, y2 = img_width, img_height, 0, 0
                for i, lm in enumerate(landmarks.landmark):
                    x = int(lm.x * img_width)
                    y = int(lm.y * img_height)
                    landmarks_dict[i] = (x, y) # collecting landmarks for liveness detection
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
                
                liveness.calculate_liveness(landmarks_dict)

                # Determine frame color based on verification and liveness
                if face_recognition.verified and liveness.live:
                    frame_color = GREEN
                    status_text = f"{name} Blinks: {liveness.total_blinks}"
                elif face_recognition.verified and not liveness.live:
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
        else: # reset all verified states if face dissapears from frame
            name = "Unknown"
            face_similarity_score = -1
            face_recognition.reset()
            liveness.reset()
            

        cv2.imshow("Face Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break


    # housekeeping
    cap.release()
    cv2.destroyAllWindows()
