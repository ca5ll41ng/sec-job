import hashlib
import json
import re
import time

import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from ..models import Question
from ..paths import MEDIA_DIR
from .html2md import html_to_md

UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}


def download_images(node) -> None:
    """把文章图片下载到本地 data/media，避免微信图床防盗链"""
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    for img in node.find_all("img"):
        src = img.get("data-src") or img.get("src") or ""
        new = ""
        if src.startswith("http"):
            try:
                data = requests.get(src, headers=UA, timeout=15).content
                if len(data) > 200:
                    name = hashlib.md5(data).hexdigest()[:16] + ".png"
                    (MEDIA_DIR / name).write_bytes(data)
                    new = f"/media/{name}"
            except Exception:
                new = ""
        if new:
            img.attrs = {"src": new, "alt": ""}
        else:
            img.decompose()


def fetch_article(url: str) -> dict:
    r = requests.get(url, headers=UA, timeout=20)
    r.raise_for_status()
    r.encoding = "utf-8"
    soup = BeautifulSoup(r.text, "lxml")
    t = soup.select_one("#activity-name") or soup.select_one('meta[property="og:title"]')
    if t is None:
        title = (soup.title.get_text(strip=True) if soup.title else "未命名文章")
    else:
        title = t.get_text(strip=True) if t.name != "meta" else t.get("content", "")
    author_el = soup.select_one("#js_name")
    author = author_el.get_text(strip=True) if author_el else ""
    content = (
        soup.select_one("#js_content")
        or soup.select_one("#page-content")
        or soup.select_one("article")
        or soup.body
        or soup
    )
    download_images(content)
    md = re.sub(r"\n{3,}", "\n\n", html_to_md(str(content))).strip()
    return {"title": title, "author": author, "md": md}


def split_md(md: str):
    """按 1-3 级标题切分文章为多道题；少于 2 个标题则整篇一题"""
    parts = re.split(r"(?m)^#{1,3}\s+(.+?)\s*$", md)
    if len(parts) < 5:  # 少于 2 个标题
        return [("", md)]
    pre = parts[0].strip()
    chunks = []
    for i in range(1, len(parts) - 1, 2):
        head, body = parts[i].strip(), parts[i + 1].strip()
        chunks.append([head, body])
    if pre:
        chunks[0][1] = pre + "\n\n" + chunks[0][1]
    chunks = [(h, b) for h, b in chunks if len(b) > 10]
    if len(chunks) < 2:
        return [("", md)]
    return chunks


def import_wechat_article(
    db: Session, url: str, split: bool = True, category: str | None = None
) -> tuple[int, list[str]]:
    art = fetch_article(url)
    cat = category or "公众号收录"
    digest = hashlib.md5(url.encode()).hexdigest()[:10]
    chunks = split_md(art["md"]) if split else [("", art["md"])]
    titles = []
    for i, (h, body) in enumerate(chunks):
        if h:
            title = h
        elif len(chunks) == 1:
            title = art["title"]
        else:
            title = f"{art['title']}·{i + 1}"
        eid = f"wechat:{digest}-{i}"
        q = db.query(Question).filter(Question.external_id == eid).first()
        if not q:
            q = Question(external_id=eid)
            db.add(q)
        q.category = cat
        q.sort_key = f"9000-{digest}{i:04d}"  # 公众号题目排在仓库题之后
        q.order_in_category = i
        q.title = title
        q.answer = body
        q.source_type = "wechat"
        q.source_url = url
        q.tags = json.dumps([art["author"]] if art["author"] else [], ensure_ascii=False)
        titles.append(title)
    db.commit()
    return len(chunks), titles
