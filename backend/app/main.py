from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .db import init_db
from .paths import DIST_DIR, MEDIA_DIR
from .routers import experiences, progress, questions

init_db()

app = FastAPI(title="安全面试刷题", docs_url="/api/docs", openapi_url="/api/openapi.json")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(questions.router, prefix="/api")
app.include_router(progress.router, prefix="/api")
app.include_router(experiences.router, prefix="/api")

MEDIA_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")

if DIST_DIR.exists():
    app.mount("/assets", StaticFiles(directory=DIST_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa_fallback(full_path: str):
        fp = (DIST_DIR / full_path).resolve()
        if full_path and fp.is_file() and str(fp).startswith(str(DIST_DIR.resolve())):
            return FileResponse(fp)
        return FileResponse(DIST_DIR / "index.html")
