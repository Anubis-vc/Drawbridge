import time
import json
import os
from datetime import datetime

class ConfigManager:
    def __init__(self, config_file='./config/config.json'):
        self.config_file = config_file
        self.config = self.load_config()
        self.last_modified = os.path.getmtime(config_file)
    
    def load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("ERROR: config file not found, falling back to default")
            raise FileNotFoundError
            # return self.get_default_config()
    
    def get_default_config(self):
        return {
            "face_recognition": 
                {
                    "model": "small",
                    "confidence_threshold": 0.7,
                    "liveness_check": "blink"
                },
            "notifications":
                {
                    "enabled_types": ["email"],
                    "email": {"recipients": ["testing.code.ved@gmail.com"]}
                }
        }
    
    def has_changed(self) -> bool:
        current_modified = os.path.getmtime(self.config_file)
        return current_modified > self.last_modified
        # return False
    
    def reload_if_changed(self) -> bool:
        if self.has_changed():
            old_config = self.config
            self.config = self.load_config()
            self.last_modified = os.path.getmtime(self.config_file)
            
            self.log_config_change(old_config, self.config)
            return True
        return False
    
    def log_config_change(self, old_config, new_config):
        print(f"[{datetime.now()}] Configuration reloaded")
        # could find out what has changed, though maybe pass that on to objects?
