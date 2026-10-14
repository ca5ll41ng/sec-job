import sys
from pathlib import Path


def _resolve():
    """返回 (项目根目录, 前端构建产物目录)。兼容 PyInstaller 打包后的运行环境。"""
    if getattr(sys, "frozen", False):
        root = Path(sys.executable).resolve().parent  # exe 所在目录，data/ 放这里
        bundle = Path(getattr(sys, "_MEIPASS", root))  # 只读打包资源
        return root, bundle / "frontend_dist"
    root = Path(__file__).resolve().parents[2]
    return root, root / "frontend" / "dist"


ROOT_DIR, DIST_DIR = _resolve()
DATA_DIR = ROOT_DIR / "data"
DB_PATH = DATA_DIR / "app.db"
MEDIA_DIR = DATA_DIR / "media"
REPO_DIR = DATA_DIR / "sec-interview-repo"
