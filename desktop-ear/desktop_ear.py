"""Desktop Ear: a tray-resident Windows voice recorder with optional local STT."""

from __future__ import annotations

import datetime as dt
import os
import queue
import subprocess
import sys
import threading
import wave
from pathlib import Path
from tkinter import messagebox
import tkinter as tk

import numpy as np
import pystray
import sounddevice as sd
from PIL import Image, ImageDraw
from pynput import keyboard


APP_DIR = (
    Path(sys.executable).resolve().parent
    if getattr(sys, "frozen", False)
    else Path(__file__).resolve().parent
)
RECORDINGS_DIR = APP_DIR / "data" / "recordings"
RATE = int(os.getenv("DESKTOP_EAR_SAMPLE_RATE", "16000"))
HOTKEY = os.getenv("DESKTOP_EAR_HOTKEY", "<ctrl>+<shift>+<space>")
WHISPER_MODEL = os.getenv("DESKTOP_EAR_WHISPER_MODEL", "tiny")


class Recorder:
    def __init__(self) -> None:
        self.frames: queue.Queue[np.ndarray] = queue.Queue()
        self.stream: sd.InputStream | None = None
        self.active = False
        self.lock = threading.Lock()

    def start(self) -> None:
        with self.lock:
            if self.active:
                return
            self.frames = queue.Queue()
            self.stream = sd.InputStream(
                samplerate=RATE,
                channels=1,
                dtype="float32",
                callback=self._callback,
            )
            self.stream.start()
            self.active = True

    def stop(self) -> Path:
        with self.lock:
            if not self.active or self.stream is None:
                raise RuntimeError("录音尚未开始")
            stream = self.stream
            self.stream = None
            self.active = False

        stream.stop()
        stream.close()
        chunks = []
        while not self.frames.empty():
            chunks.append(self.frames.get())
        audio = (
            np.concatenate(chunks, axis=0)
            if chunks
            else np.zeros((0, 1), dtype=np.float32)
        )
        pcm = (np.clip(audio, -1, 1) * 32767).astype(np.int16)
        RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)
        stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        target = RECORDINGS_DIR / f"recording-{stamp}.wav"
        with wave.open(str(target), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(RATE)
            wav.writeframes(pcm.tobytes())
        return target

    def _callback(self, indata, _frames, _time, status) -> None:
        if status:
            print("Audio status:", status)
        self.frames.put(indata.copy())


class DesktopEar:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Desktop Ear | 电脑的耳朵")
        self.root.geometry("560x440")
        self.root.minsize(500, 390)
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)
        self.root.bind("<Unmap>", self.on_minimize)

        self.recorder = Recorder()
        self.listener: keyboard.GlobalHotKeys | None = None
        self.tray: pystray.Icon | None = None
        self.whisper = None
        self.closing = False
        self.status = tk.StringVar(value="待机中")
        self.result = tk.StringVar(value="快捷键开始录音，录音仅保存在本机。")
        self.recording_paths: list[Path] = []

        self._build_window()
        self._build_tray()
        self._start_hotkey()
        self.refresh_recordings()

    def _build_window(self) -> None:
        header = tk.Frame(self.root, padx=18, pady=14)
        header.pack(fill="x")
        tk.Label(header, text="Desktop Ear", font=("Segoe UI", 20, "bold")).pack(anchor="w")
        tk.Label(
            header,
            text="电脑的语音入口 · 后台常驻 · 本地保存",
            fg="#555555",
        ).pack(anchor="w", pady=(2, 0))

        status_box = tk.LabelFrame(self.root, text="当前状态", padx=12, pady=10)
        status_box.pack(fill="x", padx=18, pady=(0, 10))
        tk.Label(status_box, textvariable=self.status, anchor="w").pack(fill="x")
        tk.Label(
            status_box,
            text=f"全局快捷键：{HOTKEY}    关闭窗口会隐藏到系统托盘",
            anchor="w",
            fg="#666666",
        ).pack(fill="x", pady=(5, 0))

        actions = tk.Frame(self.root)
        actions.pack(fill="x", padx=18, pady=5)
        self.record_button = tk.Button(
            actions, text="开始录音", width=15, height=2, command=self.toggle_recording
        )
        self.record_button.pack(side="left")
        tk.Button(
            actions, text="隐藏到后台", width=15, height=2, command=self.hide_window
        ).pack(side="left", padx=8)
        tk.Button(
            actions, text="打开录音目录", width=15, height=2, command=self.open_recordings
        ).pack(side="left")

        recordings = tk.LabelFrame(self.root, text="最近录音（双击打开）", padx=8, pady=7)
        recordings.pack(fill="both", expand=True, padx=18, pady=(8, 8))
        self.listbox = tk.Listbox(recordings, height=7, activestyle="none")
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar = tk.Scrollbar(recordings, command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)
        self.listbox.bind("<Double-Button-1>", self.open_selected_recording)
        tk.Label(
            self.root,
            textvariable=self.result,
            anchor="w",
            justify="left",
            wraplength=520,
            fg="#444444",
        ).pack(fill="x", padx=18, pady=(2, 14))

    def _build_tray(self) -> None:
        self.tray = pystray.Icon(
            "desktop-ear",
            self._tray_image(),
            "Desktop Ear - 待机中",
            menu=pystray.Menu(
                pystray.MenuItem("显示小窗", self.show_window),
                pystray.MenuItem("开始 / 结束录音", self.toggle_from_tray),
                pystray.MenuItem("打开录音目录", self.open_recordings_from_tray),
                pystray.MenuItem("退出", self.exit_from_tray),
            ),
        )
        self.tray.run_detached()

    @staticmethod
    def _tray_image() -> Image.Image:
        image = Image.new("RGBA", (64, 64), (31, 92, 125, 255))
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((21, 9, 43, 42), radius=11, fill="white")
        draw.arc((12, 18, 52, 56), 0, 180, fill="white", width=5)
        draw.line((32, 55, 32, 61), fill="white", width=5)
        draw.line((23, 61, 41, 61), fill="white", width=5)
        return image

    def _start_hotkey(self) -> None:
        self.listener = keyboard.GlobalHotKeys({HOTKEY: self.toggle_recording})
        self.listener.start()

    def toggle_recording(self) -> None:
        if not self.closing:
            self.root.after(0, self._toggle_recording_ui)

    def toggle_from_tray(self, _icon=None, _item=None) -> None:
        self.toggle_recording()

    def _toggle_recording_ui(self) -> None:
        try:
            if self.recorder.active:
                target = self.recorder.stop()
                self.record_button.config(text="开始录音")
                self.result.set(f"已保存：{target.name}\n正在尝试本地转写…")
                self._set_status("录音已保存")
                threading.Thread(target=self._transcribe, args=(target,), daemon=True).start()
            else:
                self.recorder.start()
                self.record_button.config(text="结束录音")
                self._set_status("正在录音… 再按快捷键或托盘菜单结束")
                self.result.set("录音正在本地进行；结束后保存为 WAV。")
        except Exception as exc:
            self._set_status("录音启动/保存失败")
            self.result.set(str(exc))
            self._notify("Desktop Ear", str(exc))

    def _transcribe(self, audio_path: Path) -> None:
        try:
            from faster_whisper import WhisperModel
        except ImportError:
            self.root.after(
                0,
                lambda: self._transcription_done(
                    "录音已保存。安装可选 faster-whisper 后可进行本地转写。"
                ),
            )
            return
        try:
            if self.whisper is None:
                self.whisper = WhisperModel(
                    WHISPER_MODEL, device="cpu", compute_type="int8"
                )
            segments, _info = self.whisper.transcribe(str(audio_path), language="zh")
            text = "".join(segment.text for segment in segments).strip()
            audio_path.with_suffix(".transcript.txt").write_text(
                text + "\n", encoding="utf-8"
            )
            message = "转写结果：" + (text or "（没有识别到文字）")
        except Exception as exc:
            message = "音频已保存，但本地转写失败：" + str(exc)
        self.root.after(0, lambda: self._transcription_done(message))

    def _transcription_done(self, message: str) -> None:
        self.result.set(message)
        self._set_status("待机中")
        self.refresh_recordings()

    def _set_status(self, value: str) -> None:
        self.status.set(value)
        if self.tray is not None:
            self.tray.title = "Desktop Ear - " + value

    def refresh_recordings(self) -> None:
        RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)
        self.recording_paths = sorted(
            RECORDINGS_DIR.glob("recording-*.wav"), reverse=True
        )[:20]
        self.listbox.delete(0, tk.END)
        for path in self.recording_paths:
            self.listbox.insert(tk.END, path.name)

    def show_window(self, _icon=None, _item=None) -> None:
        if not self.closing:
            self.root.after(0, self._show_window)

    def _show_window(self) -> None:
        self.root.deiconify()
        self.root.state("normal")
        self.root.lift()
        self.root.focus_force()

    def hide_window(self) -> None:
        self.root.withdraw()

    def on_minimize(self, _event=None) -> None:
        if self.root.state() == "iconic":
            self.root.after(100, self.root.withdraw)

    def open_recordings(self) -> None:
        RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)
        if os.name == "nt":
            os.startfile(str(RECORDINGS_DIR))
        else:
            subprocess.Popen(["xdg-open", str(RECORDINGS_DIR)])

    def open_recordings_from_tray(self, _icon=None, _item=None) -> None:
        self.root.after(0, self.open_recordings)

    def open_selected_recording(self, _event=None) -> None:
        selected = self.listbox.curselection()
        if selected:
            os.startfile(str(self.recording_paths[selected[0]]))

    def exit_from_tray(self, _icon=None, _item=None) -> None:
        self.root.after(0, self.close)

    def _notify(self, title: str, message: str) -> None:
        if self.tray is not None:
            try:
                self.tray.notify(message, title)
            except Exception:
                pass

    def close(self) -> None:
        if self.closing:
            return
        self.closing = True
        if self.recorder.active:
            try:
                self.recorder.stop()
            except Exception:
                pass
        if self.listener is not None:
            self.listener.stop()
        if self.tray is not None:
            self.tray.stop()
        self.root.destroy()


def main() -> None:
    RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)
    root = tk.Tk()
    DesktopEar(root)
    root.mainloop()


if __name__ == "__main__":
    main()
