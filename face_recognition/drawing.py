from mediapipe.python.solutions.drawing_utils import DrawingSpec
from mediapipe.python.solutions import face_mesh_connections

# Mediapipe styles for facemesh drawing, BGR values
_THICKNESS_CONTOURS = 2
_YELLOW = (0, 204, 255)
# _PEACH = (180, 229, 255)
_WHITE = (224, 224, 224)
_CYAN = (192, 255, 48)
_RED = (76, 71, 255)
_GREEN = (0, 255, 0)

facemesh_tesselation_style = DrawingSpec((76, 71, 255), 1)

facemesh_eyes_connection_style = {}
left_spec = DrawingSpec(color=_CYAN, thickness=1)
for connection in face_mesh_connections.FACEMESH_LEFT_IRIS:
    facemesh_eyes_connection_style[connection] = left_spec
right_spec = DrawingSpec(color=_CYAN, thickness=1)
for connection in face_mesh_connections.FACEMESH_RIGHT_IRIS:
    facemesh_eyes_connection_style[connection] = right_spec

facemesh_contour_connection_style = {
    face_mesh_connections.FACEMESH_LIPS: DrawingSpec(
        color=_WHITE, thickness=_THICKNESS_CONTOURS
    ),
    face_mesh_connections.FACEMESH_LEFT_EYE: DrawingSpec(
        color=_CYAN, thickness=_THICKNESS_CONTOURS
    ),
    face_mesh_connections.FACEMESH_LEFT_EYEBROW: DrawingSpec(
        color=_WHITE, thickness=_THICKNESS_CONTOURS
    ),
    face_mesh_connections.FACEMESH_RIGHT_EYE: DrawingSpec(
        color=_CYAN, thickness=_THICKNESS_CONTOURS
    ),
    face_mesh_connections.FACEMESH_RIGHT_EYEBROW: DrawingSpec(
        color=_WHITE, thickness=_THICKNESS_CONTOURS
    ),
    face_mesh_connections.FACEMESH_FACE_OVAL: DrawingSpec(
        color=_RED, thickness=_THICKNESS_CONTOURS
    ),
    face_mesh_connections.FACEMESH_NOSE: DrawingSpec(
        color=_YELLOW, thickness=_THICKNESS_CONTOURS
    ),
}
# flatten the connections into a simple dictionary since each landmark is a list of tuples
face_mesh_contour_style = {}
for k, v in facemesh_contour_connection_style.items():
    for connection in k:
        face_mesh_contour_style[connection] = v


# helpers to clean up the code in main
def get_tesselation_style():
    return facemesh_tesselation_style


def get_contour_style():
    return face_mesh_contour_style


def get_iris_style():
    return facemesh_eyes_connection_style


def get_verified_style():
    return DrawingSpec(color=_GREEN, thickness=1)


def get_unverified_style():
    return DrawingSpec(color=_RED, thickness=1)
