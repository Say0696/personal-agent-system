# Desktop Ear（电脑的耳朵）

这是 Personal Agent System 的本地电脑语音入口。程序可以常驻系统托盘，用全局快捷键录音并保存到本地；可选本地转写。它暂时不操作微信，也不重新开发 AI。

## 运行

```powershell
cd desktop-ear
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python desktop_ear.py
```

按 Ctrl+Shift+Space 开始和结束录音，也可以点击窗口按钮或托盘菜单。关闭窗口、点击最小化都会隐藏到托盘，选择托盘菜单中的“退出”才会结束程序。录音保存在 EXE 同级的 data/recordings；双击最近录音可打开文件。

## 直接点击运行

打包版本位于 `dist/DesktopEar.exe`，双击即可打开，不需要先打开 PowerShell。首次运行时 Windows 可能询问麦克风权限，请允许。系统托盘图标提供显示小窗、录音开关、打开录音目录和退出命令。

## 当前边界

- 不持续上传录音。
- 不连接任何模型 API。
- 不操作微信或发送消息。
- 可选安装 requirements-optional.txt，为后续本地转写做准备。
