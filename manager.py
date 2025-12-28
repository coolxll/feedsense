import typer
from rich.console import Console
from rich.table import Table
from .db import init_db, get_db
from .config import config
from .rss_service import RSSService
from .llm_service import LLMService

app = typer.Typer(help="RSS Auto Read - AI Powered Feed Reader")
console = Console()
rss_service = RSSService()

@app.command()
def init():
    """Initialize the database."""
    config.validate()
    init_db()
    console.print("[green]System initialized.[/green]")

@app.command()
def add(url: str):
    """Add a new RSS feed URL."""
    rss_service.add_feed(url)

@app.command()
def list_feeds():
    """List all subscriptions."""
    feeds = rss_service.list_feeds()
    table = Table(title="RSS Subscriptions")
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("URL", style="green")
    
    for feed in feeds:
        table.add_row(str(feed['id']), feed['name'], feed['url'])
    
    console.print(table)

@app.command()
def fetch():
    """Fetch latest articles from all feeds."""
    count = rss_service.fetch_all()
    console.print(f"[green]Finished.[/green] Total new articles: {count}")

@app.command()
def analyze(limit: int = 10):
    """Analyze pending articles using AI."""
    llm_service = LLMService()
    count = llm_service.process_pending(limit)
    console.print(f"[green]Finished.[/green] Analyzed {count} articles.")

@app.command()
def report(top: int = 20, score_min: int = 0):
    """Show top rated articles."""
    with get_db() as conn:
        query = '''
            SELECT a.title, a.score, a.category, a.analysis, a.link, f.name as feed_name
            FROM articles a
            JOIN feeds f ON a.feed_id = f.id
            WHERE a.status = 'analyzed' AND a.score >= ?
            ORDER BY a.score DESC, a.published DESC
            LIMIT ?
        '''
        rows = conn.execute(query, (score_min, top)).fetchall()

    table = Table(title=f"Top Articles (Min Score: {score_min})")
    table.add_column("Score", style="bold yellow", justify="right")
    table.add_column("Title", style="bold white")
    table.add_column("Category", style="cyan")
    table.add_column("AI Reason", style="dim")
    
    for row in rows:
        color = "green" if row['score'] >= 8 else "yellow" if row['score'] >= 5 else "white"
        score_str = f"[{color}]{row['score']}[/{color}]"
        table.add_row(score_str, row['title'], row['category'], row['analysis'])
    
    console.print(table)

if __name__ == "__main__":
    app()
