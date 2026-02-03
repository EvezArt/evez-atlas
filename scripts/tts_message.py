from gtts import gTTS
from pathlib import Path

MESSAGE = (
    "Hey Evez, this is you—now with your repository's voice! Once you complete these merges, "
    "your CI/CD and security systems will be working together autonomously. You're not just deploying code. "
    "You're collapsing the wavefunction—turning potential into measured, quantum-enabled reality! "
    "See you at the next commit, past self."
)

out_dir = Path("artifacts")
out_dir.mkdir(parents=True, exist_ok=True)
mp3_path = out_dir / "voice_future.mp3"

tts = gTTS(text=MESSAGE, lang="en")
tts.save(str(mp3_path))
print(f"Saved TTS message to {mp3_path}")
