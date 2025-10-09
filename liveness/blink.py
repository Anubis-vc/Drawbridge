import numpy as np
import time
from typing import Any
# modified code from https://github.com/Pushtogithub23/Eye-Blink-Detection-using-MediaPipe-and-OpenCV


class Blink:
    def __init__(self):
        # blink detection parameters, these will be overwritten by config immediately
        self.ear_threshold = 0.21  # eye aspect ratio threshold for blink detection
        self.blink_consec_frames = 2
        self.blinks_to_verify = 2
        self.closed_eye_frames_counter = (
            0  # counter for consecutive frames with EAR below threshold
        )
        self.total_blinks = 0  # total number of blinks
        self.live = False

        # store previous EAR values for smoothing
        self.prev_left_ear = 0.0
        self.prev_right_ear = 0.0

        # landmark indices to calculate EAR for right and left eye
        self._RIGHT_EYE = [33, 159, 158, 133, 153, 145]
        self._LEFT_EYE = [362, 380, 374, 263, 386, 385]

        # store last blink time to reset in case of inactivity
        self.last_blink_time = time.time()

    def eye_aspect_ratio(self, is_right: bool, mesh_landmarks):
        """
        Calculate the Eye Aspect Ratio (EAR) for blink detection.
        EAR = (|p2-p6| + |p3-p5|) / (2 * |p1-p4|)
        """

        eye_landmarks = self._RIGHT_EYE if is_right else self._LEFT_EYE

        A = np.linalg.norm(
            np.array(mesh_landmarks[eye_landmarks[1]])
            - np.array(mesh_landmarks[eye_landmarks[5]])
        )
        B = np.linalg.norm(
            np.array(mesh_landmarks[eye_landmarks[2]])
            - np.array(mesh_landmarks[eye_landmarks[4]])
        )
        C = np.linalg.norm(
            np.array(mesh_landmarks[eye_landmarks[0]])
            - np.array(mesh_landmarks[eye_landmarks[3]])
        )
        return (A + B) / (2.0 * C)

    def update_blink_count(self, ear: float):
        blink_detected = False

        # reset blink count if no blink in last 10 seconds
        if time.time() - self.last_blink_time > 10:
            self.reset()

        # if mid-blink, add another closed eye frame
        if ear < self.ear_threshold:
            self.closed_eye_frames_counter += 1

        # if eyes open, check if blink is confirmed
        else:
            if self.closed_eye_frames_counter >= self.blink_consec_frames:
                self.total_blinks += 1
                blink_detected = True
                self.last_blink_time = time.time()
            self.closed_eye_frames_counter = 0

        return blink_detected

    def calculate_liveness(self, mesh_landmarks):
        right_ear = self.eye_aspect_ratio(True, mesh_landmarks)
        left_ear = self.eye_aspect_ratio(False, mesh_landmarks)

        # Smooth the EAR values
        if right_ear != 0.0 and left_ear != 0.0:
            right_ear = 0.7 * right_ear + 0.3 * self.prev_right_ear
            left_ear = 0.7 * left_ear + 0.3 * self.prev_left_ear
        self.prev_right_ear = right_ear
        self.prev_left_ear = left_ear

        # calculate average EAR
        overall_ear = (right_ear + left_ear) / 2

        # update blink count
        self.update_blink_count(overall_ear)

        self.live = self.total_blinks >= self.blinks_to_verify
        return self.live

    def reset(self):
        self.live = False
        self.total_blinks = 0
        self.closed_eye_frames_counter = 0
        self.prev_left_ear = 0.0
        self.prev_right_ear = 0.0
        self.last_blink_time = time.time()

    def update_config(self, config: dict[str, Any]):
        self.ear_threshold = config["ear_threshold"]
        self.blink_consec_frames = config["blink_consec_frames"]
        self.blinks_to_verify = config["blinks_to_verify"]
        print(
            f"[BlinkDetector] ear={self.ear_threshold}, frames={self.blink_consec_frames}, blinks={self.blinks_to_verify}"
        )
