import argparse
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

from app.db import SessionLocal, init_db  # noqa: E402
from app.models import Experience, Question  # noqa: E402
from app.paths import REPO_DIR  # noqa: E402
from app.ingest.generic import import_experience  # noqa: E402
from app.ingest.sec_repo import import_repo  # noqa: E402
from app.ingest.wechat import import_wechat_article  # noqa: E402


def main():
    init_db()
    p = argparse.ArgumentParser(description="安全面试刷题 - 数据导入工具")
    sub = p.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("import-repo", help="导入/更新 GitHub Sec-Interview 题库")
    p1.add_argument("--repo", default=None, help="本地仓库路径(默认 data/sec-interview-repo)")
    p1.add_argument("--no-pull", action="store_true", help="不执行 git pull")

    p2 = sub.add_parser("wechat", help="导入微信公众号文章为题目")
    p2.add_argument("url")
    p2.add_argument("--no-split", action="store_true", help="整篇作为一题，不按标题切分")
    p2.add_argument("--category", default=None, help="分类名(默认: 公众号收录)")

    p4 = sub.add_parser("add-exp", help="手动添加面经(--url / --file / --text 三选一)")
    p4.add_argument("--url", default=None)
    p4.add_argument("--file", default=None)
    p4.add_argument("--text", default=None)
    p4.add_argument("--title", default=None)
    p4.add_argument("--company", default="未分类")
    p4.add_argument("--position", default=None)

    p5 = sub.add_parser("stats", help="查看题库/面经统计")

    p6 = sub.add_parser("export-static", help="导出题库 JSON，供离线前端/APK 打包使用")

    a = p.parse_args()
    db = SessionLocal()

    if a.cmd == "import-repo":
        print(json.dumps(import_repo(db, a.repo, pull=not a.no_pull), ensure_ascii=False, indent=2))

    elif a.cmd == "wechat":
        n, titles = import_wechat_article(db, a.url, split=not a.no_split, category=a.category)
        print(f"已导入 {n} 题:")
        for t in titles:
            print(f"  - {t}")

    elif a.cmd == "add-exp":
        text = None
        if a.file:
            text = Path(a.file).read_text(encoding="utf-8")
        elif a.text:
            text = a.text
        exp, created = import_experience(
            db, url=a.url, text=text, title=a.title, company=a.company, position=a.position
        )
        print(("已导入" if created else "已存在") + f": #{exp.id} [{exp.company}] {exp.title}")

    elif a.cmd == "stats":
        total = db.query(Question).count()
        print(f"题目总数: {total}")
        rows = db.query(Question.category, Question.id).all()
        cats: dict[str, int] = {}
        for c, _ in rows:
            cats[c] = cats.get(c, 0) + 1
        for c, n in sorted(cats.items(), key=lambda x: -x[1]):
            print(f"  {c}: {n}")
        exp_total = db.query(Experience).count()
        print(f"面经总数: {exp_total}")
        rows = db.query(Experience.company, Experience.id).all()
        comps: dict[str, int] = {}
        for c, _ in rows:
            comps[c] = comps.get(c, 0) + 1
        for c, n in sorted(comps.items(), key=lambda x: -x[1]):
            print(f"  {c}: {n}")

    elif a.cmd == "export-static":
        from app.paths import ROOT_DIR

        qs = db.query(Question).order_by(Question.sort_key, Question.id).all()
        data = [
            {
                "id": q.id,
                "category": q.category,
                "sort_key": q.sort_key,
                "title": q.title,
                "answer": q.answer,
            }
            for q in qs
        ]
        out = ROOT_DIR / "frontend" / "src" / "data" / "questions.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        print(f"已导出 {len(data)} 题 -> {out}")


if __name__ == "__main__":
    main()
