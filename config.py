import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console

# Initialize Rich Console
console = Console()

# Load .env file
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    # Try loading .env.example if .env doesn't exist for dev convenience, 
    # but warn user
    pass

class Config:
    API_KEY = os.getenv("DASHSCOPE_API_KEY")
    MODEL_NAME = os.getenv("LLM_MODEL_NAME", "qwen-turbo")
    BASE_URL = os.getenv("LLM_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    DB_PATH = Path(__file__).parent / "rss_data.db"
    
    @classmethod
    def validate(cls):
        if not cls.API_KEY or cls.API_KEY.startswith("sk-xxx"):
            console.print("[bold red]Error:[/bold red] DASHSCOPE_API_KEY is not set or invalid in .env file.")
            console.print("Please copy [bold].env.example[/bold] to [bold].env[/bold] and add your API key.")
            sys.exit(1)

config = Config()
