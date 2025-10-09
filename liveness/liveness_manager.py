from liveness.blink import Blink


class LivenessManager:
    def __init__(self, enabled_types: list, blink_config=None, audio_config=None):
        self.liveness_objects = self.create_objects([blink_config, audio_config])
        self.live = False

    def create_objects(self, blink_config, audio_config):
        objects = {}
        if blink_config:
            objects["blink"] = Blink(**blink_config)
        if audio_config:
            raise NotImplementedError

    def check_liveness():
        pass
