# Desktop Ear（电脑的耳朵）

这是 Personal Agent System 的第一个本地电脑入口原型。第一版只验证：全局快捷键、录音、本地保存。它暂时不操作微信，也不重新开发 AI。

## 运行

```powershell
cd desktop-ear
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python desktop_ear.py
```

按 Ctrl+Shift+Space 开始和结束录音，也可以点击窗口按钮。录音保存在 data/recordings。

## 直接点击运行

打包版本位于 `dist/DesktopEar.exe`，双击即可打开，不需要先打开 PowerShell。首次运行时 Windows 可能询问麦克风权限，请允许。

## 当前边界

- 不持续上传录音。
- 不连接任何模型 API。
- 不操作微信或发送消息。
- 可选安装 requirements-optional.txt，为后续本地转写做准备。
