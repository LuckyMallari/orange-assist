import json


class Config:
    def __init__(self):
        with open('config.json') as json_data_file:
            j = json.load(json_data_file)
            self.is_debug = j['is_debug'] if 'is_debug' in j else False
            self.is_verbose = j['is_verbose'] if 'is_verbose' in j else False
            self.username = j['username'] if 'username' in j else None
            self.password = j['password'] if 'password' in j else None
            self.host = j['host'] if 'host' in j else None
            self.port = j['port'] if 'port' in j else None
            self.device_model_id = j['device_model_id'] if 'device_model_id' in j else None
            self.device_id = j['device_id'] if 'device_id' in j else None
            self.on_success = j['on_success'] if 'on_success' in j else None
            self.credentials_file = j['credentials_file'] if 'credentials_file' in j else False
            self.screen_mode = j['screen_mode'] if 'screen_mode' in j else "PLAYING"
            self.delete_output_files_sec = j['delete_output_files_sec'] if 'delete_output_files_sec' in j else None
            self.project_id = j['project_id'] if 'project_id' in j else None
            self.enable_speaker = j['enable_speaker'] if 'enable_speaker' in j else False

