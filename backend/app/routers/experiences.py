from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Experience
from ..ingest.generic import import_experience
from ..ingest.wechat import import_wechat_article

router = APIRouter(tags=["experiences"])


class ExpImport(BaseModel):
    url: str | None = None
    text: str | None = None
    title: str | None = None
    company: str = "未分类"
    position: str | None = None


class WechatImport(BaseModel):
    url: str
    split: bool = True
    category: str | None = None


@router.get("/experiences/companies")
def companies(db: Session = Depends(get_db)):
    rows = (
        db.query(Experience.company, func.count(Experience.id))
        .group_by(Experience.company)
        .order_by(func.count(Experience.id).desc())
        .all()
    )
    return {"items": [{"company": c, "count": n} for c, n in rows]}


@router.get("/experiences")
def list_experiences(
    company: str | None = None,
    q: str | None = None,
    page: int = 1,
    page_size: int = 15,
    db: Session = Depends(get_db),
):
    query = db.query(Experience)
    if company and company != "全部":
        query = query.filter(Experience.company == company)
    if q:
        query = query.filter(
            or_(Experience.title.contains(q), Experience.content.contains(q), Experience.position.contains(q))
        )
    total = query.count()
    page_size = min(max(page_size, 1), 100)
    items = (
        query.order_by(Experience.id.desc())
        .offset((max(page, 1) - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        "total": total,
        "items": [
            {
                "id": x.id,
                "company": x.company,
                "position": x.position,
                "title": x.title,
                "source_site": x.source_site,
                "source_url": x.source_url,
                "published_at": x.published_at,
                "excerpt": (x.content or "")[:150],
            }
            for x in items
        ],
    }


@router.get("/experiences/{eid}")
def get_experience(eid: int, db: Session = Depends(get_db)):
    x = db.get(Experience, eid)
    if not x:
        raise HTTPException(404, "面经不存在")
    return {
        "id": x.id,
        "company": x.company,
        "position": x.position,
        "title": x.title,
        "content": x.content,
        "source_site": x.source_site,
        "source_url": x.source_url,
        "published_at": x.published_at,
        "created_at": str(x.created_at or ""),
    }


@router.post("/experiences/import")
def import_experience_api(body: ExpImport, db: Session = Depends(get_db)):
    if not body.url and not body.text:
        raise HTTPException(400, "需要提供 url 或 text")
    try:
        exp, created = import_experience(
            db,
            url=body.url,
            text=body.text,
            title=body.title,
            company=body.company or "未分类",
            position=body.position,
        )
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(502, f"抓取失败: {type(e).__name__}: {e}")
    return {"id": exp.id, "created": created, "title": exp.title}


@router.post("/questions/import-wechat")
def import_wechat_api(body: WechatImport, db: Session = Depends(get_db)):
    try:
        n, titles = import_wechat_article(db, body.url, split=body.split, category=body.category)
    except Exception as e:
        raise HTTPException(502, f"抓取失败: {type(e).__name__}: {e}")
    return {"imported": n, "titles": titles[:20]}
