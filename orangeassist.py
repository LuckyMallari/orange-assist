import click
import os
import google.auth.transport.grpc
import google.auth.transport.requests
import google.oauth2.credentials
import json
import logging
import uuid
import sys
import pathlib
try:
    from helpers import (
        assistant_helpers,
        audio_helpers
    )
except (SystemError, ImportError):
    from helpers import (
        assistant_helpers,
        audio_helpers
    )

from google.assistant.embedded.v1alpha2 import (
    embedded_assistant_pb2,
    embedded_assistant_pb2_grpc
)
ASSISTANT_API_ENDPOINT = 'embeddedassistant.googleapis.com'
DEFAULT_GRPC_DEADLINE = 60 * 3 + 5
DEFAULT_AUDIO_SAMPLE_RATE = 16000
DEFAULT_AUDIO_SAMPLE_WIDTH = 2
DEFAULT_AUDIO_ITER_SIZE = 3200
DEFAULT_AUDIO_DEVICE_BLOCK_SIZE = 6400
DEFAULT_AUDIO_DEVICE_FLUSH_SIZE = 25600


def getcredentials(credentials_file):
    # Load OAuth 2.0 credentials.
    credentials = None
    http_request = None

    try:
        with open(os.path.join(click.get_app_dir('google-oauthlib-tool'), credentials_file), 'r') as f:
            credentials = google.oauth2.credentials.Credentials(
                token=None, **json.load(f))
            http_request = google.auth.transport.requests.Request()
            credentials.refresh(http_request)
    except Exception as e:
        logging.error(f"Error loading credentials: {e}")
        logging.error(
            'Run google-oauthlib-tool to initialize new OAuth 2.0 credentials.')
        return None, None
    return credentials, http_request


class OrangeAssistant():
    def __init__(self, cfg):
        self.assistant = None
        self.conversation_state = None
        if not cfg.device_model_id:
            print('Set device_model_id in config.json')
            sys.exit(-1)
            return
        if not cfg.device_id:
            print('Set device-id in config.json')
            sys.exit(-1)
            return
        if not cfg.project_id:
            print('Set project_id in config.json')
            sys.exit(-1)
            return

        self.cfg = cfg
        self.conversation_stream_speaker = None
        self.conversation_stream_file = None
        self.credentials, self.http_request = getcredentials(
            cfg.credentials_file)

        device_base_url = f"https://{ASSISTANT_API_ENDPOINT}/v1alpha2/projects/{cfg.project_id}/devices"
        if cfg.uuid is None:
            cfg.register(str(uuid.uuid1()))
                      
        device_id = cfg.uuid
        payload = {
            'id': device_id,
            'model_id': self.cfg.device_model_id,
            'client_type': 'SDK_SERVICE'
        }
        session = google.auth.transport.requests.AuthorizedSession(
            self.credentials
        )
        r = session.post(device_base_url, data=json.dumps(payload))
        if r.status_code != 200:
            logging.error('Failed to register device: %s', r.text)
            sys.exit(-1)
        logging.info('Device registered: %s', device_id)
        # pathlib.Path(os.path.dirname(device_config)).mkdir(exist_ok=True)
        # with open(device_config, 'w') as f:
        #     json.dump(payload, f)

    def __enter__(self):
        return self

    def __exit__(self, etype, e, traceback):
        if e:
            return False

    def connect(self):
        creds, reqs = getcredentials(self.cfg.credentials_file)
        # Create an authorized gRPC channel.
        grpc_channel = google.auth.transport.grpc.secure_authorized_channel(
            creds, reqs, ASSISTANT_API_ENDPOINT)
        self.assistant = embedded_assistant_pb2_grpc.EmbeddedAssistantStub(
            grpc_channel)

        logging.info(f"Connecting to {ASSISTANT_API_ENDPOINT}")

    def assist(self, r):
        if self.cfg.is_debug:
            r.screen_mode = self.cfg.screen_mode
        if not r.request:
            return "NO OUTPUT. DOH!",""

        # Send a text request to the Assistant and playback the response.
        def iter_assist_requests():
            config = embedded_assistant_pb2.AssistConfig(
                audio_out_config=embedded_assistant_pb2.AudioOutConfig(
                    encoding='LINEAR16',
                    sample_rate_hertz=16000,
                    volume_percentage=100,
                ),
                dialog_state_in=embedded_assistant_pb2.DialogStateIn(
                    language_code=r.language,
                    conversation_state=self.conversation_state,
                    is_new_conversation=True,
                ),
                device_config=embedded_assistant_pb2.DeviceConfig(
                    device_id=self.cfg.device_id,
                    device_model_id=self.cfg.device_model_id,
                ),
                text_query=r.request
            )

            screen_mode = r.screen_mode if r.screen_mode else self.cfg.screen_mode
            config.screen_out_config.screen_mode = getattr(
                embedded_assistant_pb2.ScreenOutConfig, screen_mode)
            self.is_new_conversation = True
            req = embedded_assistant_pb2.AssistRequest(config=config)
            yield req

        audio_out_wavesink = None
        if r.output_audio_file or r.is_play_audio:
            audio_sink = (
                audio_helpers.SoundDeviceStream(
                    sample_rate=DEFAULT_AUDIO_SAMPLE_RATE,
                    sample_width=DEFAULT_AUDIO_SAMPLE_WIDTH,
                    block_size=DEFAULT_AUDIO_DEVICE_BLOCK_SIZE,
                    flush_size=DEFAULT_AUDIO_DEVICE_FLUSH_SIZE
                )
            )
            audio_source = (
                audio_helpers.SoundDeviceStream(
                    sample_rate=DEFAULT_AUDIO_SAMPLE_RATE,
                    sample_width=DEFAULT_AUDIO_SAMPLE_WIDTH,
                    block_size=DEFAULT_AUDIO_DEVICE_BLOCK_SIZE,
                    flush_size=DEFAULT_AUDIO_DEVICE_FLUSH_SIZE
                )
            )

            self.conversation_stream_speaker = audio_helpers.ConversationStream(
                source=audio_source,
                sink=audio_sink,
                iter_size=DEFAULT_AUDIO_ITER_SIZE,
                sample_width=DEFAULT_AUDIO_SAMPLE_WIDTH,
            )
            if r.output_audio_file:
                if self.conversation_stream_file:
                    self.conversation_stream_file.close()
                self.conversation_stream_file = audio_helpers.WaveSink(
                    open(f"output/{r.output_audio_file}", 'wb'),
                    sample_rate=DEFAULT_AUDIO_SAMPLE_RATE,
                    sample_width=DEFAULT_AUDIO_SAMPLE_WIDTH
                )

        text_response = ''
        html_response = ''
        responses = self.assistant.Assist(
            iter_assist_requests(), DEFAULT_GRPC_DEADLINE)
        for resp in responses:
            if len(resp.audio_out.audio_data) > 0:
                if r.is_play_audio:
                    if not self.conversation_stream_speaker.playing:
                        self.conversation_stream_speaker.stop_recording()
                        self.conversation_stream_speaker.start_playback()
                        logging.info('Playing assistant response.')
                    self.conversation_stream_speaker.write(
                        resp.audio_out.audio_data)
                if r.output_audio_file:
                    self.conversation_stream_file.write(
                        resp.audio_out.audio_data)
            if resp.screen_out.data:
                html_response = resp.screen_out.data
            if resp.dialog_state_out.conversation_state:
                conversation_state = resp.dialog_state_out.conversation_state
                self.conversation_state = conversation_state
            if resp.dialog_state_out.supplemental_display_text:
                if text_response != resp.dialog_state_out.supplemental_display_text:
                    text_response += resp.dialog_state_out.supplemental_display_text

        if self.conversation_stream_file:
            self.conversation_stream_file.close()
        print(text_response)
        return text_response, html_response
