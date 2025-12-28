import feedparser
import time
from datetime import datetime
from .db import get_db
from rich.console import Console

console = Console()

class RSSService:
    def add_feed(self, url: str):
        """Add a new feed source."""
        # Parse first to get title
        feed = feedparser.parse(url)
        if feed.bozo:
             console.print(f"[yellow]Warning:[/yellow] Trouble parsing {url}, but continuing.")
        
        name = feed.feed.get('title', url)
        
        with get_db() as conn:
            try:
                conn.execute(
                    "INSERT INTO feeds (name, url, last_fetched) VALUES (?, ?, ?)",
                    (name, url, datetime.now())
                )
                conn.commit()
                console.print(f"[green]Added feed:[/green] {name}")
                return True
            except Exception as e:
                console.print(f"[red]Error adding feed:[/red] {e}")
                return False

    def list_feeds(self):
        with get_db() as conn:
            return conn.execute("SELECT * FROM feeds").fetchall()

    def fetch_all(self):
        """Fetch new articles from all active feeds."""
        with get_db() as conn:
            feeds = conn.execute("SELECT * FROM feeds WHERE is_active=1").fetchall()

        new_count = 0
        for row in feeds:
            feed_id = row['id']
            url = row['url']
            console.print(f"Fetching {row['name']}...")
            
            feed = feedparser.parse(url)
            
            # Prepare batch insert
            entries_to_add = []
            
            for entry in feed.entries:
                link = entry.get('link', '')
                if not link: continue
                
                # Check duplication
                with get_db() as conn:
                    exists = conn.execute("SELECT id FROM articles WHERE link=?", (link,)).fetchone()
                
                if exists:
                    continue
                
                # Extract fields
                title = entry.get('title', 'No Title')
                pub_parsed = entry.get('published_parsed') or entry.get('updated_parsed')
                if pub_parsed:
                    published = datetime.fromtimestamp(time.mktime(pub_parsed))
                else:
                    published = datetime.now()
                    
                summary = entry.get('summary', '')
                content = ''
                if 'content' in entry:
                    content = entry.content[0].value
                
                entries_to_add.append((feed_id, title, link, published, summary, content))
            
            if entries_to_add:
                with get_db() as conn:
                    conn.executemany('''
                        INSERT INTO articles (feed_id, title, link, published, summary, content, status)
                        VALUES (?, ?, ?, ?, ?, ?, 'new')
                    ''', entries_to_add)
                    conn.commit()
                new_count += len(entries_to_add)
                console.print(f"  -> Found {len(entries_to_add)} new articles.")
            else:
                console.print("  -> No new articles.")
                
        return new_count
