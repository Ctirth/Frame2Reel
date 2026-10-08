import os

try:
    from dotenv import load_dotenv
    load_dotenv()  # reads the local .env file (never committed)
except ImportError:
    pass

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

if not ELEVENLABS_API_KEY:
    raise RuntimeError(
        "ELEVENLABS_API_KEY is missing. Copy .env.example to .env and add your key."
    )
