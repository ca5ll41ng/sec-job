"""安全面试刷题 PC 桌面版入口：
后台启动内置服务(127.0.0.1:8000)，再用原生窗口(pywebview)展示。
打包: pyinstaller desktop/SecQuiz.spec
"""
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

import urllib.request

import webview


def server_ready() -> bool:
    try:
        urllib.request.urlopen("http://127.0.0.1:8000/api/home", timeout=1)
        return True
    except Exception:
        return False


def main():
    if not server_ready():
        import uvicorn

        from app.main import app

        threading.Thread(
            target=lambda: uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning"),
            daemon=True,
        ).start()
        for _ in range(60):
            if server_ready():
                break
            time.sleep(0.2)

    try:
        webview.create_window(
            "安全面试刷题", "http://127.0.0.1:8000", width=1100, height=780, min_size=(380, 520)
        )
        webview.start()
    except Exception:
        # 无法创建原生窗口时退回系统浏览器
        import webbrowser

        webbrowser.open("http://127.0.0.1:8000")
        while True:
            time.sleep(3600)


if __name__ == "__main__":
    main()
