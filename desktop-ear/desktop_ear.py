from pathlib import Path
import datetime as dt
import os
import sys
import queue
import threading
import wave
import tkinter as tk
from tkinter import messagebox
import numpy as np
import sounddevice as sd
from pynput import keyboard

APP_DIR = Path(sys.executable).resolve().parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent
RECORDINGS_DIR = APP_DIR / 'data' / 'recordings'
RATE = int(os.getenv('DESKTOP_EAR_SAMPLE_RATE', '16000'))
HOTKEY = os.getenv('DESKTOP_EAR_HOTKEY', '<ctrl>+<shift>+<space>')

class Recorder:
    def __init__(self):
        self.frames = queue.Queue()
        self.stream = None
        self.active = False
        self.lock = threading.Lock()

    def start(self):
        with self.lock:
            if self.active:
                return
            self.frames = queue.Queue()
            self.stream = sd.InputStream(samplerate=RATE, channels=1, dtype='float32', callback=self.callback)
            self.stream.start()
            self.active = True

    def stop(self):
        with self.lock:
            if not self.active or self.stream is None:
                raise RuntimeError('录音尚未开始')
            stream = self.stream
            self.stream = None
            self.active = False
        stream.stop()
        stream.close()
        parts = []
        while not self.frames.empty():
            parts.append(self.frames.get())
        audio = np.concatenate(parts, axis=0) if parts else np.zeros((0, 1), dtype=np.float32)
        pcm = (np.clip(audio, -1, 1) * 32767).astype(np.int16)
        RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)
        stamp = dt.datetime.now().strftime('%Y%m%d-%H%M%S')
        target = RECORDINGS_DIR / ('recording-' + stamp + '.wav')
        with wave.open(str(target), 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(RATE)
            wav.writeframes(pcm.tobytes())
        return target

    def callback(self, indata, frames, time, status):
        if status:
            print('音频状态:', status)
        self.frames.put(indata.copy())

class App:
    def __init__(self, root):
        self.root = root
        self.root.title('Desktop Ear / 电脑的耳朵')
        self.root.geometry('500x300')
        self.recorder = Recorder()
        self.listener = keyboard.GlobalHotKeys({HOTKEY: self.toggle})
        self.listener.start()
        tk.Label(root, text='Desktop Ear', font=('Segoe UI', 20, 'bold')).pack(pady=(20, 4))
        tk.Label(root, text='第一版：全局快捷键录音，本地保存，不持续上传。', fg='#555').pack()
        self.status = tk.StringVar(value='待机中  快捷键: ' + HOTKEY)
        tk.Label(root, textvariable=self.status, wraplength=460).pack(pady=22)
        self.button = tk.Button(root, text='开始录音', width=18, height=2, command=self.toggle)
        self.button.pack()
        tk.Label(root, text='录音保存在 desktop-ear/data/recordings', fg='#666').pack(pady=20)
        root.protocol('WM_DELETE_WINDOW', self.close)

    def toggle(self):
        self.root.after(0, self.toggle_ui)

    def toggle_ui(self):
        try:
            if self.recorder.active:
                target = self.recorder.stop()
                self.button.config(text='开始录音')
                self.status.set('录音已保存: ' + target.name + '\n正在尝试本地转写...')
                threading.Thread(target=self.transcribe, args=(target,), daemon=True).start()
            else:
                self.recorder.start()
                self.button.config(text='结束录音')
                self.status.set('正在录音... 再按一次快捷键结束')
        except Exception as exc:
            self.status.set('操作失败: ' + str(exc))
            messagebox.showerror('Desktop Ear', str(exc))

    def transcribe(self, audio_path):
        try:
            from faster_whisper import WhisperModel
        except ImportError:
            self.root.after(0, lambda: self.status.set('录音已保存: ' + audio_path.name + '\n未安装 faster-whisper，当前只保留音频。'))
            return
        try:
            model = WhisperModel(os.getenv('DESKTOP_EAR_WHISPER_MODEL', 'tiny'), device='cpu', compute_type='int8')
            segments, _info = model.transcribe(str(audio_path), language='zh')
            text = ''.join(segment.text for segment in segments).strip()
            transcript = audio_path.with_suffix('.transcript.txt')
            transcript.write_text(text + '\n', encoding='utf-8')
            message = '转写完成: ' + (text or '（没有识别到文字）')
        except Exception as exc:
            message = '音频已保存，但转写失败: ' + str(exc)
        self.root.after(0, lambda: self.status.set(message))

    def close(self):
        if self.recorder.active:
            try:
                self.recorder.stop()
            except Exception:
                pass
        self.listener.stop()
        self.root.destroy()

if __name__ == '__main__':
    RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)
    root = tk.Tk()
    App(root)
    root.mainloop()
