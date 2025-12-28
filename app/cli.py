import typer
from rich.console import Console
from rich.table import Table
from app.db import init_db, get_db
from app.config import config
from app.services.rss import RSSService
from app.services.llm import LLMService

app = typer.Typer(help="FeedSense - AI Powered Feed Reader")
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
        table.add_row(str(feed["id"]), feed["name"], feed["url"])

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
        query = """
            SELECT a.title, a.score, a.category, a.analysis, a.link, f.name as feed_name
            FROM articles a
            JOIN feeds f ON a.feed_id = f.id
            WHERE a.status = 'analyzed' AND a.score >= ?
            ORDER BY a.score DESC, a.published DESC
            LIMIT ?
        """
        rows = conn.execute(query, (score_min, top)).fetchall()

    if not rows:
        console.print(f"[yellow]No articles found with score >= {score_min}[/yellow]")
        return

    console.print(f"\n[bold cyan]📰 Top Articles (Min Score: {score_min})[/bold cyan]\n")
    
    for i, row in enumerate(rows, 1):
        score = row["score"]
        color = "green" if score >= 8 else "yellow" if score >= 5 else "white"
        
        console.print(f"[bold]{i}. [{color}]★ {score}[/{color}][/bold] {row['title']}")
        console.print(f"   [cyan]分类:[/cyan] {row['category'] or 'N/A'}")
        console.print(f"   [dim]理由:[/dim] {row['analysis'] or 'N/A'}")
        console.print(f"   [blue underline]🔗 {row['link']}[/blue underline]")
        console.print()
    
    console.print(f"[dim]Total: {len(rows)} articles[/dim]\n")


@app.command()
def daily(date: str = None, score_min: int = 5):
    """Show articles from a specific date (YYYY-MM-DD). Defaults to today."""
    from datetime import datetime, timedelta

    if date is None:
        target_date = datetime.now().date()
    else:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            console.print(
                "[red]Error:[/red] Invalid date format. Use YYYY-MM-DD (e.g., 2025-12-28)"
            )
            return

    # Calculate date range (whole day)
    start_datetime = datetime.combine(target_date, datetime.min.time())
    end_datetime = start_datetime + timedelta(days=1)

    with get_db() as conn:
        query = """
            SELECT a.title, a.score, a.category, a.analysis, a.link, a.published, f.name as feed_name
            FROM articles a
            JOIN feeds f ON a.feed_id = f.id
            WHERE a.status = 'analyzed' 
                AND a.score >= ?
                AND a.published >= ? 
                AND a.published < ?
            ORDER BY a.score DESC, a.published DESC
        """
        rows = conn.execute(
            query, (score_min, start_datetime, end_datetime)
        ).fetchall()

    if not rows:
        console.print(
            f"[yellow]No articles found for {target_date} with score >= {score_min}[/yellow]"
        )
        return

    console.print(f"\n[bold cyan]📅 Daily Digest: {target_date} (Min Score: {score_min})[/bold cyan]\n")
    
    for i, row in enumerate(rows, 1):
        score = row["score"]
        color = "green" if score >= 8 else "yellow" if score >= 5 else "white"
        
        console.print(f"[bold]{i}. [{color}]★ {score}[/{color}][/bold] {row['title']}")
        console.print(f"   [cyan]分类:[/cyan] {row['category'] or 'N/A'} | [dim]来源:[/dim] {row['feed_name']}")
        console.print(f"   [dim]理由:[/dim] {row['analysis'] or 'N/A'}")
        console.print(f"   [blue underline]🔗 {row['link']}[/blue underline]")
        console.print()

    console.print(f"[dim]Total: {len(rows)} articles[/dim]\n")


@app.command()
def stats():
    """Show statistics about feeds and articles."""
    with get_db() as conn:
        # Feed stats
        feed_count = conn.execute("SELECT COUNT(*) FROM feeds WHERE is_active=1").fetchone()[0]
        
        # Article stats
        total_articles = conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
        analyzed = conn.execute("SELECT COUNT(*) FROM articles WHERE status='analyzed'").fetchone()[0]
        pending = conn.execute("SELECT COUNT(*) FROM articles WHERE status='new'").fetchone()[0]
        
        # Score distribution
        high_score = conn.execute("SELECT COUNT(*) FROM articles WHERE score >= 7").fetchone()[0]
        mid_score = conn.execute("SELECT COUNT(*) FROM articles WHERE score >= 4 AND score < 7").fetchone()[0]
        low_score = conn.execute("SELECT COUNT(*) FROM articles WHERE score < 4 AND score > 0").fetchone()[0]
        
        # Today's articles
        from datetime import datetime, timedelta
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_count = conn.execute(
            "SELECT COUNT(*) FROM articles WHERE published >= ?", (today_start,)
        ).fetchone()[0]

    console.print("\n[bold cyan]📊 FeedSense Statistics[/bold cyan]\n")
    
    console.print(f"[bold]Feeds:[/bold] {feed_count} active")
    console.print(f"[bold]Articles:[/bold] {total_articles} total")
    console.print(f"  ├─ ✅ Analyzed: {analyzed}")
    console.print(f"  ├─ ⏳ Pending: {pending}")
    console.print(f"  └─ 📅 Today: {today_count}\n")
    
    console.print(f"[bold]Quality Distribution:[/bold]")
    console.print(f"  ├─ [green]High (7-10):[/green] {high_score}")
    console.print(f"  ├─ [yellow]Medium (4-6):[/yellow] {mid_score}")
    console.print(f"  └─ [dim]Low (0-3):[/dim] {low_score}\n")


if __name__ == "__main__":
    app()
