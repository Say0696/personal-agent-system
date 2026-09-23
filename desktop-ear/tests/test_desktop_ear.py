import tempfile
import wave
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

import numpy as np

import desktop_ear


class FakeInputStream:
    def __init__(self, *, samplerate, channels, dtype, callback):
        self.samplerate = samplerate
        self.channels = channels
        self.callback = callback

    def start(self):
        self.callback(np.array([[0.25], [-0.25]], dtype=np.float32), 2, None, None)

    def stop(self):
        pass

    def close(self):
        pass


class RecorderTests(TestCase):
    def test_records_frames_to_local_pcm_wav(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(desktop_ear, "RECORDINGS_DIR", Path(directory)), patch.object(
                desktop_ear.sd, "InputStream", FakeInputStream
            ):
                recorder = desktop_ear.Recorder()
                recorder.start()
                target = recorder.stop()

            self.assertTrue(target.exists())
            with wave.open(str(target), "rb") as audio:
                self.assertEqual(audio.getnchannels(), 1)
                self.assertEqual(audio.getsampwidth(), 2)
                self.assertEqual(audio.getframerate(), desktop_ear.RATE)
                self.assertEqual(audio.getnframes(), 2)
