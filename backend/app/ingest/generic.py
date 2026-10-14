import hashlib
import re

import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from ..models import Experience
from .html2md import html_to_md

UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

NOISE_TAGS = ["script", "style", "nav", "header", "footer", "aside", "form", "iframe", "noscript"]
CONTENT_SELECTORS = [
    "#js_content",        # 微信公众号
    "#content_views",     # CSDN
    "article",
    "#article",
    ".article-content",
    ".post-body",
    ".topic-main-content",  # 牛客
    "main",
    "#detail",
]


def fetch_page(url: str) -> str:
    r = requests.get(url, headers=UA, timeout=20)
    r.raise_for_status()
    if not r.encoding or r.encoding.lower() == "iso-8859-1":
        r.encoding = r.apparent_encoding or "utf-8"
    return r.text


def extract_article(url: str) -> dict:
    soup = BeautifulSoup(fetch_page(url), "lxml")
    for tag in soup(NOISE_TAGS):
        tag.decompose()
    og = soup.select_one('meta[property="og:title"]')
    if og and og.get("content"):
        title = og["content"].strip()
    elif soup.h1:
        title = soup.h1.get_text(strip=True)
    elif soup.title:
        title = soup.title.get_text(strip=True)
    else:
        title = ""
    node = None
    for sel in CONTENT_SELECTORS:
        n = soup.select_one(sel)
        if n and len(n.get_text(strip=True)) > 120:
            node = n
            break
    if node is None:
        best, best_len = None, 0
        for div in soup.find_all(["div", "section"]):
            n = len(div.get_text(strip=True))
            if n > best_len:
                best, best_len = div, n
        node = best or soup.body or soup
    return {"title": title, "md": html_to_md(str(node)), "len": len(node.get_text(strip=True))}


def guess_position(text: str) -> str:
    rules = [
        ("渗透", "渗透测试工程师"),
        ("红队", "红队工程师"),
        ("蓝队", "蓝队工程师"),
        ("应急", "应急响应工程师"),
        ("安全研究", "安全研究员"),
        ("安全服务", "安全服务工程师"),
        ("安服", "安全服务工程师"),
        ("二进制", "二进制安全工程师"),
        ("逆向", "逆向工程师"),
        ("等保", "等保测评师"),
        ("安全运营", "安全运营工程师"),
        ("开发", "安全开发工程师"),
    ]
    for kw, pos in rules:
        if kw in text:
            return pos
    return "安全工程师"


def import_experience(
    db: Session,
    url: str | None = None,
    text: str | None = None,
    title: str | None = None,
    company: str = "未分类",
    position: str | None = None,
):
    """导入一条面经。url+text 同时给出时直接存 text；只给 url 则抓取网页提取正文。

    返回 (Experience, 是否新建)。
    """
    if url:
        site = re.sub(r"^https?://(www\.)?", "", url).split("/")[0]

    if url and not text:
        art = extract_article(url)
        if art["len"] < 150:
            raise ValueError(
                f"正文提取失败(仅 {art['len']} 字)，该页面可能需要登录或为动态渲染，请改用「粘贴文本」导入"
            )
        content = art["md"]
        title = title or art["title"] or url
    else:
        if not text or len(text.strip()) < 30:
            raise ValueError("面经正文太短(至少 30 字)")
        content = text.strip()
        title = title or content.strip().splitlines()[0][:80] or "未命名面经"
        site = site if url else ""

    key = url or f"text:{hashlib.md5(content.encode()).hexdigest()}"
    existing = db.query(Experience).filter(Experience.source_url == key).first()
    if existing:
        return existing, False

    exp = Experience(
        company=company or "未分类",
        position=position or guess_position(title + content),
        title=title[:200],
        content=content,
        source_site=site,
        source_url=key,
        published_at="",
    )
    db.add(exp)
    db.commit()
    return exp, True
