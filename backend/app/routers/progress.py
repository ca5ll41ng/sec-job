from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Progress

router = APIRouter(tags=["progress"])


class ProgressIn(BaseModel):
    status: str | None = None
    starred: bool | None = None


@router.get("/progress")
def get_progress(
    client_id: str | None = Header(default=None, alias="X-Client-Id"),
    db: Session = Depends(get_db),
):
    if not client_id:
        return {}
    rows = db.query(Progress).filter(Progress.client_id == client_id).all()
    return {
        str(r.question_id): {"status": r.status, "starred": bool(r.starred)}
        for r in rows
        if r.status != "none" or r.starred
    }


@router.put("/progress/{question_id}")
def put_progress(
    question_id: int,
    body: ProgressIn,
    client_id: str | None = Header(default=None, alias="X-Client-Id"),
    db: Session = Depends(get_db),
):
    if not client_id:
        raise HTTPException(400, "缺少 X-Client-Id")
    row = db.get(Progress, (client_id, question_id))
    if not row:
        row = Progress(client_id=client_id, question_id=question_id, status="none", starred=False)
        db.add(row)
    if body.status is not None:
        row.status = body.status if body.status in ("none", "known", "unknown") else "none"
    if body.starred is not None:
        row.starred = body.starred
    db.commit()
    return {"ok": True, "status": row.status, "starred": bool(row.starred)}


@router.delete("/progress")
def clear_progress(
    confirm: bool = False,
    client_id: str | None = Header(default=None, alias="X-Client-Id"),
    db: Session = Depends(get_db),
):
    if not confirm:
        raise HTTPException(400, "需要 confirm=true")
    db.query(Progress).filter(Progress.client_id == (client_id or "")).delete()
    db.commit()
    return {"ok": True}
