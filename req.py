import json


class Req:
    def __init__(self, raw):
        try:
            r = json.loads(raw)
        except:
            r = json.loads("{}")
        self.request = r['request'] if 'request' in r else None
        self.uuid = r['uuid'] if 'uuid' in r else None
        self.language = r['language'] if 'language' in r else 'en-US'
        self.screen_mode = r['screen_mode'] if 'screen_mode' in r else "PLAYING"
        self.output_html_file = r['output_html_file'] if 'output_html_file' in r else None
        self.output_audio_file = r['output_audio_file'] if 'output_audio_file' in r else None
        self.is_play_audio = r['is_play_audio'] if 'is_play_audio' in r else False
        self.is_return_html = r['is_return_html'] if 'is_return_html' in r else False

