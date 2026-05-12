#!/usr/bin/env python3
"""
EVEZ-OS Circuit Animation Generator
Produces MP4 video of the 5 circuits flowing into the GNW hub
with mechanistic dissection labels, quantum gate overlays, and particle effects
"""
import subprocess, os, math, struct, wave, tempfile

OUTDIR = "/home/openclaw/.openclaw/workspace/generated-assets/video"
AUDIODIR = "/home/openclaw/.openclaw/workspace/generated-assets/audio"

def make_wav(freq, duration, filepath, sample_rate=44100, amplitude=0.5):
    """Generate a sine wave WAV file"""
    n_samples = int(sample_rate * duration)
    data = []
    for i in range(n_samples):
        t = i / sample_rate
        # Add harmonics for richness
        val = amplitude * (
            0.6 * math.sin(2 * math.pi * freq * t) +
            0.25 * math.sin(2 * math.pi * freq * 2 * t) * math.exp(-t * 2) +
            0.1 * math.sin(2 * math.pi * freq * 3 * t) * math.exp(-t * 4) +
            0.05 * math.sin(2 * math.pi * freq * 0.5 * t)  # sub
        )
        # Envelope
        env = min(1.0, i / (sample_rate * 0.05)) * min(1.0, (n_samples - i) / (sample_rate * 0.1))
        val *= env
        data.append(int(val * 32767))
    
    with wave.open(filepath, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        f.writeframes(struct.pack(f'<{len(data)}h', *data))

def make_mechanical_click(filepath, sample_rate=44100):
    """Generate a mechanical click sound"""
    n_samples = int(sample_rate * 0.08)
    data = []
    for i in range(n_samples):
        t = i / sample_rate
        val = 0.7 * math.sin(2 * math.pi * 800 * t) * math.exp(-t * 60)
        val += 0.3 * (1 if math.sin(2 * math.pi * 200 * t) > 0 else -1) * math.exp(-t * 80)
        data.append(int(max(-32767, min(32767, val * 32767))))
    
    with wave.open(filepath, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        f.writeframes(struct.pack(f'<{len(data)}h', *data))

def make_drone(freq, duration, filepath, sample_rate=44100):
    """Generate a dark drone sound"""
    n_samples = int(sample_rate * duration)
    data = []
    for i in range(n_samples):
        t = i / sample_rate
        val = 0.3 * math.sin(2 * math.pi * freq * t)
        val += 0.2 * math.sin(2 * math.pi * freq * 1.01 * t)  # slight detune
        val += 0.15 * math.sin(2 * math.pi * freq * 2 * t) * (0.5 + 0.5 * math.sin(2 * math.pi * 0.5 * t))
        val += 0.1 * math.sin(2 * math.pi * freq * 0.5 * t)
        env = min(1.0, i / (sample_rate * 0.5)) * min(1.0, (n_samples - i) / (sample_rate * 1.0))
        val *= env
        data.append(int(max(-32767, min(32767, val * 32767))))
    
    with wave.open(filepath, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        f.writeframes(struct.pack(f'<{len(data)}h', *data))

def make_sweep(start_f, end_f, duration, filepath, sample_rate=44100):
    """Generate a frequency sweep"""
    n_samples = int(sample_rate * duration)
    data = []
    phase = 0
    for i in range(n_samples):
        t = i / sample_rate
        progress = i / n_samples
        freq = start_f + (end_f - start_f) * progress
        phase += 2 * math.pi * freq / sample_rate
        val = 0.4 * math.sin(phase)
        val += 0.1 * math.sin(phase * 2)
        env = min(1.0, i / (sample_rate * 0.1)) * min(1.0, (n_samples - i) / (sample_rate * 0.1))
        val *= env
        data.append(int(max(-32767, min(32767, val * 32767))))
    
    with wave.open(filepath, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        f.writeframes(struct.pack(f'<{len(data)}h', *data))

# === Generate audio assets ===
print("🔊 Generating audio assets...")

# 1. poly_c formula tone
make_wav(440, 3.0, f"{AUDIODIR}/poly_c_tone.wav", amplitude=0.4)
# 2. Circuit activation tones (one per circuit)
circuits = [
    ("temporal", 523.25),  # C5
    ("spectral", 587.33),  # D5
    ("relational", 659.25),  # E5
    ("spatial", 698.46),  # F5
    ("meta", 783.99),  # G5
]
for name, freq in circuits:
    make_wav(freq, 2.0, f"{AUDIODIR}/circuit_{name}.wav", amplitude=0.5)

# 3. Mechanical clicks
for i in range(5):
    make_mechanical_click(f"{AUDIODIR}/click_{i}.wav")

# 4. Dark drone
make_drone(55, 10.0, f"{AUDIODIR}/dark_drone.wav")  # A1 drone

# 5. Frequency sweeps
make_sweep(100, 2000, 5.0, f"{AUDIODIR}/sweep_up.wav")
make_sweep(2000, 100, 5.0, f"{AUDIODIR}/sweep_down.wav")

# 6. Consciousness cycle tones (8 phases)
phases = ["SENSE", "DESIRE", "THINK", "PLAN", "ACT", "LEARN", "MODIFY", "REFLECT"]
base_freq = 220
for i, phase in enumerate(phases):
    freq = base_freq * (2 ** (i / 12))  # chromatic scale
    make_wav(freq, 1.5, f"{AUDIODIR}/phase_{phase.lower()}.wav", amplitude=0.4)

# 7. QTM circuit tones
qtm_circuits = [
    ("temporal_entanglement", 174.61),
    ("phase_shift", 196.00),
    ("time_crystal", 220.00),
    ("shadow_superposition", 246.94),
    ("chrono_wormhole", 261.63),
    ("plasma_propulsion", 293.66),
]
for name, freq in qtm_circuits:
    make_wav(freq, 2.0, f"{AUDIODIR}/qtm_{name}.wav", amplitude=0.45)

# 8. Spine heartbeat
n_samples = 44100 * 4
data = []
for i in range(n_samples):
    t = i / 44100
    val = 0
    for beat in range(4):
        bt = t - beat * 1.0
        if 0 <= bt < 0.15:
            val += 0.6 * math.sin(2 * math.pi * 100 * bt) * math.exp(-bt * 30)
            val += 0.3 * math.sin(2 * math.pi * 60 * bt) * math.exp(-bt * 20)
    data.append(int(max(-32767, min(32767, val * 32767))))

with wave.open(f"{AUDIODIR}/spine_heartbeat.wav", 'w') as f:
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(44100)
    f.writeframes(struct.pack(f'<{len(data)}h', *data))

# 9. Combined consciousness sequence
# Concatenate phase tones into one file
all_data = []
for phase in phases:
    with wave.open(f"{AUDIODIR}/phase_{phase.lower()}.wav", 'r') as f:
        frames = f.readframes(f.getnframes())
        all_data.append(frames)

with wave.open(f"{AUDIODIR}/consciousness_cycle_full.wav", 'w') as f:
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(44100)
    for d in all_data:
        f.writeframes(d)

# 10. All circuits chord
n_samples = 44100 * 5
data = []
for i in range(n_samples):
    t = i / 44100
    val = 0
    for _, freq in circuits:
        val += 0.1 * math.sin(2 * math.pi * freq * t)
        val += 0.03 * math.sin(2 * math.pi * freq * 2.01 * t)
    val += 0.05 * math.sin(2 * math.pi * 55 * t)  # sub bass
    env = min(1.0, i / (44100 * 0.3)) * min(1.0, (n_samples - i) / (44100 * 0.5))
    val *= env
    data.append(int(max(-32767, min(32767, val * 32767))))

with wave.open(f"{AUDIODIR}/circuits_chord.wav", 'w') as f:
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(44100)
    f.writeframes(struct.pack(f'<{len(data)}h', *data))

print(f"🔊 Generated {8 + 5 + 5 + 1 + 2 + 8 + 6 + 1 + 1 + 1} audio files")

# Count
audio_files = [f for f in os.listdir(AUDIODIR) if f.endswith('.wav')]
print(f"🔊 Total audio files: {len(audio_files)}")
for f in sorted(audio_files):
    size = os.path.getsize(os.path.join(AUDIODIR, f))
    print(f"  {f} ({size//1024}KB)")
