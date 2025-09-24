from face_recognition import FaceRecognizer, Overlay
from liveness import Blink
from config import ConfigManager
# TODO: import and configure notifications

# third party libraries
import cv2
import mediapipe as mp
import time


if __name__ == "__main__":
    config_manager = ConfigManager(config_file='./config/config.json')    
    face_recognition = FaceRecognizer(**config_manager.config['face_recognition'])
    liveness = Blink(**config_manager.config['blink_config'])
    overlay = Overlay(font=cv2.FONT_HERSHEY_SIMPLEX, **config_manager.config['overlay'])

    # init mediapipe objects for detection
    mp_face_mesh = mp.solutions.face_mesh
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
    
    config_checked_time = time.time()
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame")
            break
        
        # check for a config change every 5 seconds
        if  time.time() - config_checked_time > 5:
            if config_manager.reload_if_changed():
                face_recognition.update_config(**config_manager.config['face_recognition'])
                liveness.update_config(**config_manager.config['blink_config'])
                overlay.update_config(**config_manager.config['overlay'])
            config_checked_time = time.time()
                

        # convert to rgb for mediapipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # run through mediapipe detection algorithm
        results = face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            for landmarks in results.multi_face_landmarks:
                name, face_similarity_score = face_recognition.run_facial_recognition(
                    frame
                )

                # https://mediapipe.readthedocs.io/en/latest/solutions/face_mesh.html
                # get bounding coordinates for framing and liveness detection
                img_height, img_width, _ = frame.shape
                # need pixel values to pass to liveness detection, mediapipe returns "normalized landmarks"
                landmarks_dict = {}
                x1, y1, x2, y2 = img_width, img_height, 0, 0
                for i, lm in enumerate(landmarks.landmark):
                    x = int(lm.x * img_width)
                    y = int(lm.y * img_height)
                    landmarks_dict[i] = (
                        x,
                        y,
                    )  # collecting landmarks for liveness detection
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
                
                # if the person is unknown we do not care if they are real
                if name == "Unknown":
                    liveness.reset()
                else:
                    liveness.calculate_liveness(landmarks_dict)
                
                overlay.draw(
                    face_recognition.verified,
                    liveness.live,
                    name,
                    liveness.total_blinks,
                    frame,
                    x1,
                    x2,
                    y1,
                    y2,
                )
        else:  # reset all verified states if face dissapears from frame
            face_recognition.reset()
            liveness.reset()

        cv2.imshow("Face Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # housekeeping
    cap.release()
    cv2.destroyAllWindows()
