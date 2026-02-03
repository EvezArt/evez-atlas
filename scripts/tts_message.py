from gtts import gTTS
from pathlib import Path
import sys

MESSAGE = (
    "Hey Evez—your timelines just synced. Merge your safeguards, "
    "label your tasks, and watch the orchestrator hum. Each commit collapses "
    "uncertainty into reality. Keep CI green, secrets clean, and remember: "
    "the future isn't written; it's deployed."
)

try:
    out_dir = Path("artifacts")
    out_dir.mkdir(parents=True, exist_ok=True)
    mp3_path = out_dir / "voice_future.mp3"

    gTTS(text=MESSAGE, lang="en").save(str(mp3_path))
    print(f"Saved TTS message to {mp3_path}")
except Exception as e:
    print(f"Error generating TTS: {e}", file=sys.stderr)
    sys.exit(1)
