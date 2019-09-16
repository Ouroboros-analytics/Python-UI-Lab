import json
from pathlib import Path


class Settings:
    def __init__(self):
        self.settings_path = Path('settings.json')
        self.settings = json.load(self.settings_path.open())
        self.lesson_path = Path(self.settings['lessonPath'])
        self.class_path = Path(self.settings['classPath'])
        self.class_day = self.settings['classDay']
        self.theme = self.settings['theme']
        self.push_style = self.settings['pushStyle']
        self.commit_msg = self.settings['commitMsg']

    def write(self, parameter, value):
        self.settings[parameter] = value

        self.settings_path.write_text(json.dumps(self.settings))
