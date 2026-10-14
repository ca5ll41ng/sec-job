from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from .db import Base


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    external_id = Column(String(128), unique=True, index=True, nullable=False)
    category = Column(String(64), index=True, nullable=False, default="未分类")
    sort_key = Column(String(32), index=True, default="")
    order_in_category = Column(Integer, default=0)
    title = Column(Text, nullable=False)
    answer = Column(Text, default="")
    source_type = Column(String(16), default="manual")  # repo | wechat | manual
    source_url = Column(Text, default="")
    tags = Column(Text, default="[]")
    created_at = Column(DateTime, default=utcnow)


class Experience(Base):
    __tablename__ = "experiences"

    id = Column(Integer, primary_key=True)
    company = Column(String(64), index=True, nullable=False, default="未分类")
    position = Column(String(64), default="")
    title = Column(Text, default="")
    content = Column(Text, default="")
    source_site = Column(String(128), default="")
    source_url = Column(String(512), index=True, default="")
    published_at = Column(String(32), default="")
    created_at = Column(DateTime, default=utcnow)


class Progress(Base):
    __tablename__ = "progress"

    client_id = Column(String(64), primary_key=True)
    question_id = Column(Integer, primary_key=True)
    status = Column(String(8), default="none")  # none | known | unknown
    starred = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
