from utils.enums import OpenCvColors, MpColors
import cv2
from mediapipe.python.solutions.drawing_utils import DrawingSpec
from mediapipe.python.solutions import face_mesh_connections
import mediapipe as mp


class Overlay:
    def __init__(self, font, font_scale, font_thickness, mesh: bool = False):
        self.font = font
        self.scale = font_scale
        self.thickness = font_thickness

        # Define thickness
        self._THICKNESS_CONTOURS = 2

        # Initialize MediaPipe drawing styles
        if mesh:
            self._setup_mediapipe_styles()

    def _setup_mediapipe_styles(self):
        """Setup MediaPipe drawing styles"""

        self.facemesh_tesselation_style = DrawingSpec(
            color=MpColors.RED.value, thickness=1
        )

        self.facemesh_eyes_connection_style = {}
        left_spec = DrawingSpec(color=MpColors.CYAN.value, thickness=1)
        for connection in face_mesh_connections.FACEMESH_LEFT_IRIS:
            self.facemesh_eyes_connection_style[connection] = left_spec

        right_spec = DrawingSpec(color=MpColors.CYAN.value, thickness=1)
        for connection in face_mesh_connections.FACEMESH_RIGHT_IRIS:
            self.facemesh_eyes_connection_style[connection] = right_spec

        # Contour connection style
        self.facemesh_contour_connection_style = {
            face_mesh_connections.FACEMESH_LIPS: DrawingSpec(
                color=MpColors.WHITE.value, thickness=self._THICKNESS_CONTOURS
            ),
            face_mesh_connections.FACEMESH_LEFT_EYE: DrawingSpec(
                color=MpColors.CYAN.value, thickness=self._THICKNESS_CONTOURS
            ),
            face_mesh_connections.FACEMESH_LEFT_EYEBROW: DrawingSpec(
                color=MpColors.WHITE.value, thickness=self._THICKNESS_CONTOURS
            ),
            face_mesh_connections.FACEMESH_RIGHT_EYE: DrawingSpec(
                color=MpColors.CYAN.value, thickness=self._THICKNESS_CONTOURS
            ),
            face_mesh_connections.FACEMESH_RIGHT_EYEBROW: DrawingSpec(
                color=MpColors.WHITE.value, thickness=self._THICKNESS_CONTOURS
            ),
            face_mesh_connections.FACEMESH_FACE_OVAL: DrawingSpec(
                color=MpColors.RED.value, thickness=self._THICKNESS_CONTOURS
            ),
            face_mesh_connections.FACEMESH_NOSE: DrawingSpec(
                color=MpColors.YELLOW.value, thickness=self._THICKNESS_CONTOURS
            ),
        }

        # Flatten the connections into a simple dictionary
        self.face_mesh_contour_style = {}
        for k, v in self.facemesh_contour_connection_style.items():
            for connection in k:
                self.face_mesh_contour_style[connection] = v

    def _getframeinfo(self, verified: bool, live: bool, name: str, blinks: int):
        """Get the color and message to display in the fram"""
        if verified and live:
            frame_color = OpenCvColors.GREEN.value
            status_text = f"{name} Blinks: {blinks}"
        elif verified and not live:
            frame_color = OpenCvColors.YELLOW.value
            status_text = f"{name} Blinks: {blinks}"
        else:
            frame_color = OpenCvColors.RED.value
            status_text = "Unknown"
        return frame_color, status_text

    def draw(
        self, verified: bool, live: bool, name: str, blinks: int, frame, x1, x2, y1, y2
    ):
        """Overlays the frame with rectangle and information about the face in frame"""

        frame_color, status_text = self._getframeinfo(verified, live, name, blinks)
        cv2.rectangle(frame, (x1, y1), (x2, y2), frame_color, self.thickness)

        (text_width, text_height), baseline = cv2.getTextSize(
            status_text, self.font, self.scale, self.thickness
        )

        cv2.putText(
            frame,
            status_text,
            ((x1 + x2 - text_width) // 2, y2 + text_height + 15),
            self.font,
            self.scale,
            frame_color,
            self.thickness,
        )

    def draw_mesh(self, frame, landmarks, verified: bool = False):
        """Draw MediaPipe face mesh on the frame"""

        # https://github.com/google-ai-edge/mediapipe/blob/master/mediapipe/python/solutions/drawing_styles.py
        mp_drawing = mp.solutions.drawing_utils

        # Draw face mesh
        mp_drawing.draw_landmarks(
            frame,
            landmarks,
            mp.solutions.face_mesh.FACEMESH_TESSELATION,
            None,
            self._get_verified_style() if verified else self._get_unverified_style(),
        )

        # Draw face contours
        mp_drawing.draw_landmarks(
            frame,
            landmarks,
            mp.solutions.face_mesh.FACEMESH_CONTOURS,
            None,
            self._get_verified_style() if verified else self._get_unverified_style(),
        )

        # Draw iris connections
        mp_drawing.draw_landmarks(
            frame,
            landmarks,
            mp.solutions.face_mesh.FACEMESH_IRISES,
            None,
            self._get_verified_style() if verified else self._get_unverified_style(),
        )

    def _get_tesselation_style(self):
        """Get tesselation drawing style"""
        return self.facemesh_tesselation_style

    def _get_contour_style(self):
        """Get contour drawing style"""
        return self.face_mesh_contour_style

    def _get_iris_style(self):
        """Get iris drawing style"""
        return self.facemesh_eyes_connection_style

    def _get_verified_style(self):
        """Get verified drawing style"""
        return DrawingSpec(color=OpenCvColors.GREEN.value, thickness=1)

    def _get_unverified_style(self):
        """Get unverified drawing style"""
        return DrawingSpec(color=OpenCvColors.RED.value, thickness=1)
    
    def update_config(self, font_scale, font_thickness, mesh: bool = False):
        if self.scale != font_scale:
            self.scale = font_scale
            print("Updated font scale")
        if self.thickness != font_thickness:
            self.thickness = font_thickness
            print("Updated font thickness")
        if mesh:
            self._setup_mediapipe_styles
