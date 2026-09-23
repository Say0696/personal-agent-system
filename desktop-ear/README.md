# Desktop Ear

The local voice-entry client inside Personal Agent System. It stays in the Windows system tray, records on demand through a global hotkey, and stores WAV files locally. Optional local transcription is available.

```powershell
cd desktop-ear
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python desktop_ear.py
```

Closing or minimizing the window hides the app to the tray. Use the tray menu to show the window, toggle recording, open recordings, or exit. This version does not connect to a model API, automate WeChat, or execute commands.

The packaged click-to-run build is `dist/DesktopEar.exe`. Windows may ask for microphone permission on first use.
