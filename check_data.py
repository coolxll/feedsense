from app.db import get_db

with get_db() as conn:
    rows = conn.execute(
        "SELECT title, score, category, analysis FROM articles WHERE status='analyzed' ORDER BY id DESC LIMIT 5"
    ).fetchall()
    
    for r in rows:
        print(f"Title: {r['title']}")
        print(f"Score: {r['score']}")
        print(f"Category: {r['category']}")
        print(f"Reason: {r['analysis']}")
        print("---\n")
