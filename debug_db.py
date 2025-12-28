from app.db import get_db

with get_db() as conn:
    print("Files in DB:")
    feeds = conn.execute("SELECT * FROM feeds").fetchall()
    for f in feeds:
        print(f"Feed: {f['name']} (ID: {f['id']})")

    print("\nArticles:")
    articles = conn.execute("SELECT id, feed_id, title, status, score FROM articles").fetchall()
    for a in articles:
        print(f"[{a['status']}] FeedID: {a['feed_id']} Score: {a['score']} - {a['title']}")
