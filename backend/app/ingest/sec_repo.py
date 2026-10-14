import re
import subprocess
from pathlib import Path

from sqlalchemy.orm import Session

from ..models import Question
from ..paths import REPO_DIR

REPO_URL = "https://github.com/duckpigdog/Sec-Interview.git"

CHAPTER_RE = re.compile(r"^- \[(.+?)\]\((.+?)\)")
ITEM_RE = re.compile(r"^\s+- \[(.+?)\]\((.+?)\)")


def ensure_repo(pull: bool = True) -> Path:
    if (REPO_DIR / ".git").exists():
        if pull:
            subprocess.run(
                ["git", "-C", str(REPO_DIR), "pull", "--ff-only"],
                capture_output=True, timeout=120,
            )
        return REPO_DIR
    REPO_DIR.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "clone", "--depth", "1", REPO_URL, str(REPO_DIR)], check=True, timeout=300)
    return REPO_DIR


def parse_summary(md_text: str):
    """解析 SUMMARY.md -> [(sort_key, ch, no, 章节, 题目标题, 相对路径)]"""
    items = []
    current_chapter = ""
    for line in md_text.splitlines():
        m = CHAPTER_RE.match(line)
        if m:
            current_chapter = re.sub(r"^\d+\.\s*", "", m.group(1)).strip()
            continue
        m = ITEM_RE.match(line)
        if m and current_chapter:
            title, rel = m.group(1).strip(), m.group(2).strip()
            if rel.lower().endswith("readme.md"):
                continue
            m2 = re.match(r"^(\d+)\.(\d+)\s*(.*)$", title)
            ch, no = (int(m2.group(1)), int(m2.group(2))) if m2 else (999, 0)
            clean = (m2.group(3) if m2 else title).strip()
            items.append((f"{ch:04d}-{no:04d}", ch, no, current_chapter, clean, rel))
    return items


def import_repo(db: Session, repo_dir: str | None = None, pull: bool = True) -> dict:
    repo = Path(repo_dir) if repo_dir else ensure_repo(pull=pull)
    summary = repo / "SUMMARY.md"
    if not summary.exists():
        raise FileNotFoundError(f"仓库中找不到 SUMMARY.md: {repo}")
    items = parse_summary(summary.read_text(encoding="utf-8"))
    added = updated = 0
    for sort_key, ch, no, chapter, title, rel in items:
        f = repo / rel
        if not f.exists():
            continue
        body = f.read_text(encoding="utf-8").strip()
        # 文件正文以 "### 标题" 开头，与索引中的标题重复，去掉
        body = re.sub(r"^#{1,4}\s+" + re.escape(title) + r"\s*\n+", "", body)
        eid = f"repo:{ch}-{no}"
        q = db.query(Question).filter(Question.external_id == eid).first()
        if not q:
            q = Question(external_id=eid)
            db.add(q)
            added += 1
        else:
            updated += 1
        q.category = chapter
        q.sort_key = sort_key
        q.order_in_category = no
        q.title = title
        q.answer = body
        q.source_type = "repo"
        q.source_url = f"https://github.com/duckpigdog/Sec-Interview/blob/main/{rel}"
        q.tags = "[]"
    db.commit()
    return {"total": len(items), "added": added, "updated": updated, "repo_dir": str(repo)}
