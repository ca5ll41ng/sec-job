import json

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Experience, Progress, Question
from ..version import APP_VERSION

router = APIRouter(tags=["questions"])


def _progress_map(db: Session, client_id: str | None) -> dict:
    if not client_id:
        return {}
    rows = db.query(Progress).filter(Progress.client_id == client_id).all()
    return {r.question_id: r for r in rows}


def _q_item(x: Question, pm: dict) -> dict:
    p = pm.get(x.id)
    return {
        "id": x.id,
        "category": x.category,
        "title": x.title,
        "source_type": x.source_type,
        "status": p.status if p else "none",
        "starred": bool(p.starred) if p else False,
    }


@router.get("/home")
def home(client_id: str | None = Header(default=None, alias="X-Client-Id"), db: Session = Depends(get_db)):
    total = db.query(func.count(Question.id)).scalar() or 0
    known = unknown = starred = 0
    per_cat: dict[str, dict] = {}
    cats = (
        db.query(Question.category, func.count(Question.id), func.min(Question.sort_key))
        .group_by(Question.category)
        .all()
    )
    for name, cnt, sk in cats:
        per_cat[name] = {"name": name, "count": cnt, "known": 0, "unknown": 0, "sort": sk or name}
    if client_id:
        rows = (
            db.query(Question.category, Progress.status, func.count(Progress.question_id))
            .join(Progress, Progress.question_id == Question.id)
            .filter(Progress.client_id == client_id, Progress.status != "none")
            .group_by(Question.category, Progress.status)
            .all()
        )
        srows = (
            db.query(Question.category, func.count(Progress.question_id))
            .join(Progress, Progress.question_id == Question.id)
            .filter(Progress.client_id == client_id, Progress.starred.is_(True))
            .group_by(Question.category)
            .all()
        )
        for cat, status, n in rows:
            d = per_cat.get(cat)
            if not d:
                continue
            if status == "known":
                d["known"] += n
                known += n
            elif status == "unknown":
                d["unknown"] += n
                unknown += n
        starred = sum(n for _, n in srows)
    exp_total = db.query(func.count(Experience.id)).scalar() or 0
    companies = (
        db.query(Experience.company, func.count(Experience.id))
        .group_by(Experience.company)
        .order_by(func.count(Experience.id).desc())
        .all()
    )
    return {
        "version": APP_VERSION,
        "total_questions": total,
        "known": known,
        "unknown": unknown,
        "starred": starred,
        "total_experiences": exp_total,
        "companies": [{"company": c, "count": n} for c, n in companies],
        "categories": sorted(per_cat.values(), key=lambda d: d["sort"]),
    }


@router.get("/quiz-ids")
def quiz_ids(
    category: str | None = None,
    shuffle: bool = False,
    filter: str = "all",
    ids: str | None = None,
    client_id: str | None = Header(default=None, alias="X-Client-Id"),
    db: Session = Depends(get_db),
):
    if ids:
        wanted = [int(x) for x in ids.split(",") if x.strip().isdigit()]
        return {"ids": wanted}
    q = db.query(Question.id)
    if filter in ("wrong", "star"):
        q = q.join(Progress, Progress.question_id == Question.id).filter(
            Progress.client_id == (client_id or "")
        )
        if filter == "wrong":
            q = q.filter(Progress.status == "unknown")
        else:
            q = q.filter(Progress.starred.is_(True))
    if category and category != "all":
        q = q.filter(Question.category == category)
    if shuffle:
        q = q.order_by(func.random())
    else:
        q = q.order_by(Question.sort_key, Question.id)
    return {"ids": [r[0] for r in q.all()]}


@router.get("/questions")
def list_questions(
    q: str | None = None,
    category: str | None = None,
    type: str | None = None,
    page: int = 1,
    page_size: int = 20,
    client_id: str | None = Header(default=None, alias="X-Client-Id"),
    db: Session = Depends(get_db),
):
    query = db.query(Question)
    if type == "wrong":
        query = query.join(Progress, Progress.question_id == Question.id).filter(
            Progress.client_id == (client_id or ""), Progress.status == "unknown"
        )
    elif type == "star":
        query = query.join(Progress, Progress.question_id == Question.id).filter(
            Progress.client_id == (client_id or ""), Progress.starred.is_(True)
        )
    if category and category != "all":
        query = query.filter(Question.category == category)
    if q:
        query = query.filter(or_(Question.title.contains(q), Question.answer.contains(q)))
    total = query.count()
    page_size = min(max(page_size, 1), 500)
    items = (
        query.order_by(Question.sort_key, Question.id)
        .offset((max(page, 1) - 1) * page_size)
        .limit(page_size)
        .all()
    )
    pm = _progress_map(db, client_id)
    return {"total": total, "items": [_q_item(x, pm) for x in items]}


@router.get("/questions/{qid}")
def get_question(
    qid: int,
    client_id: str | None = Header(default=None, alias="X-Client-Id"),
    db: Session = Depends(get_db),
):
    x = db.get(Question, qid)
    if not x:
        raise HTTPException(404, "题目不存在")
    p = db.get(Progress, (client_id, qid)) if client_id else None
    return {
        **_q_item(x, {qid: p} if p else {}),
        "answer": x.answer,
        "source_url": x.source_url,
        "tags": json.loads(x.tags or "[]"),
    }


@router.get("/search")
def search(q: str, db: Session = Depends(get_db)):
    questions = (
        db.query(Question)
        .filter(or_(Question.title.contains(q), Question.answer.contains(q)))
        .order_by(Question.title.contains(q).desc(), Question.sort_key)
        .limit(30)
        .all()
    )
    experiences = (
        db.query(Experience)
        .filter(or_(Experience.title.contains(q), Experience.content.contains(q)))
        .order_by(Experience.id.desc())
        .limit(30)
        .all()
    )
    return {
        "questions": [{"id": x.id, "category": x.category, "title": x.title} for x in questions],
        "experiences": [
            {"id": x.id, "company": x.company, "title": x.title} for x in experiences
        ],
    }
