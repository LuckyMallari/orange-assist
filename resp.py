import json


class Resp:
    def __init__(self, status, request, text=None, html=None, uuid=None, output_html_file=None, output_audio_file=None):
        self.status = status
        self.text = text if text else None
        self.html = html if html else None
        self.request = request
        self.uuid = uuid if uuid else None
        self.output_html_file = output_html_file if output_html_file else None
        self.output_audio_file = output_audio_file if output_audio_file else None
