import asyncio
import cv2
import mediapipe as mp

from config import config_manager
from database.data_operations import db

from face_recognition import FaceRecognizer, Overlay
from liveness import Blink
from notifications import NotificationManager
from runtime_services.embedding_manager import EmebeddingManager
from hardware_integration.lock_controller import LockController
from hardware_integration.arduino_handler import Arduino
from utils.enums import AccessLevel


class State:
    def __init__(self, arduino: Arduino | None = None) -> None:
        self.face_recognition = FaceRecognizer()
        self.liveness = Blink()
        self.overlay = Overlay()
        self.notification_manager = NotificationManager()
        # Inject Arduino if provided; otherwise LockController will create its own
        self.door = LockController(arduino)

        self._video_task: asyncio.Task | None = None
        self._stop_signal = asyncio.Event()
        self.latest_frame_jpg_enc = None

        # variables to debounce for notifications (pending) and door
        self._door_busy = False

        config_manager.register_listener(
            "face_recognition", self.face_recognition.update_config
        )
        config_manager.register_listener("blink_config", self.liveness.update_config)
        config_manager.register_listener("overlay", self.overlay.update_config)
        config_manager.register_listener(
            "notifications", self.notification_manager.update_config
        )

        self.embedding_manager = EmebeddingManager(db)
        db.register_listener(self.embedding_manager)
        
    async def cycle_lock(self):
        self._door_busy = True
        self.door.open()
        await asyncio.sleep(10)
        self.door.close()
        await asyncio.sleep(5)
        
    def is_video_running(self) -> bool:
        return self._video_task is not None

    async def start_video(self) -> str:
        if self._video_task and not self._video_task.done():
            return "Video already running"

        self._stop_signal.clear()
        self._video_task = asyncio.create_task(self._run_video_loop())
        return "Started Video"

    async def stop_video(self) -> str:
        if not self._video_task or self._video_task.done():
            return "Video not running"
        self._stop_signal.set()
        await self._video_task
        self._video_task = None
        return "Stopped Video"

    async def _run_video_loop(self):
        face_mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7,
        )

        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 720)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        print(f"Width: {cap.get(cv2.CAP_PROP_FRAME_WIDTH)}")
        print(f"Height: {cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")

        try:
            while not self._stop_signal.is_set() and cap.isOpened():
                # use thread for intensive blocking operations so api can still respond quickly
                ret, frame = await asyncio.to_thread(cap.read)
                if not ret:
                    print("Failed to read frame")
                    break

                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = await asyncio.to_thread(face_mesh.process, rgb_frame)

                if results.multi_face_landmarks:
                    for landmarks in results.multi_face_landmarks:
                        (
                            name,
                            score,
                            access,
                        ) = await asyncio.to_thread(  # TODO: update for no-GIL python
                            self.face_recognition.run_facial_recognition,
                            frame,
                            self.embedding_manager.embeddings,
                            self.embedding_manager.users,
                        )
                        img_height, img_width, _ = frame.shape
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

                        if name == "Unknown":
                            self.liveness.reset()
                        else:
                            self.liveness.calculate_liveness(landmarks_dict)

                        self.overlay.draw(
                            self.face_recognition.verified,
                            self.liveness.live,
                            name,
                            self.liveness.total_blinks,
                            frame,
                            x1,
                            x2,
                            y1,
                            y2,
                        )

                        # TODO: these single services should not be doing checks, move that here
                        self.notification_manager.check_and_send(
                            self.face_recognition.verified,
                            self.liveness.live,
                            name,
                            access_level=access,
                        )

                        if (
                            not self._door_busy
                            and self.face_recognition.verified
                            and self.liveness.live
                            and (
                                access == AccessLevel.ADMIN
                                or access == AccessLevel.FAMILY
                            )
                        ):
                            # run in a task to avoid blocking loop
                            asyncio.create_task(self.cycle_lock())

                else:  # no face landmarks recognized
                    self.face_recognition.reset()
                    self.liveness.reset()

                # imencode should be lightweight enough on this smaller resolution to run w/o thread
                self.latest_frame_jpg_enc = cv2.imencode(".jpg", frame)
                # cv2.imshow("Face Detection", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    self._stop_signal.set()
                    break
        finally:
            cap.release()
            cv2.destroyAllWindows()
            for _ in range(2):
                cv2.waitKey(1)  # let HighGUI process the close event
            face_mesh.close()
            self._stop_signal.set()
            self._video_task = None
            self.latest_frame_jpg_enc = None
