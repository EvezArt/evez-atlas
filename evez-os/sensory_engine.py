#!/usr/bin/env python3
"""
EVEZ Sensory Engine v0.1
Audio -> Text -> Visual mind-maps.
Thinks in sounds until sound becomes thought.
"""
import json, math
from pathlib import Path

class TopologySoundEngine:
    def text_to_topology(self, text):
        pixels = len(text) * 16
        tau = pixels
        factors = self._prime_factors(tau)
        chords = [self._factor_to_note(f) for f in factors[:4]]
        return {"tau": tau, "pixels": pixels, "factors": factors, "chords": chords,
                "complexity": math.log2(tau + 1), "omega": self._compute_omega(text)}

    def _prime_factors(self, n):
        factors = []
        d = 2
        while d * d <= n:
            while n % d == 0:
                factors.append(d)
                n //= d
            d += 1
        if n > 1: factors.append(n)
        return factors

    def _factor_to_note(self, f):
        notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        return notes[f % 12]

    def _compute_omega(self, text):
        words = text.lower().split()
        return len(set(words)) / len(words) if words else 0

    def render_mindmap(self, text):
        topo = self.text_to_topology(text)
        words = text.split()
        nodes = []
        for i, word in enumerate(words[:50]):
            angle = (i / len(words)) * 2 * math.pi
            radius = 50 + (topo["complexity"] * 10)
            x = 200 + radius * math.cos(angle)
            y = 200 + radius * math.sin(angle)
            nodes.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{3+len(word)/3:.1f}" fill="#ff0066" opacity="0.7"/>')
            nodes.append(f'<text x="{x:.1f}" y="{y:.1f}" fill="#fff" font-size="8" text-anchor="middle">{word}</text>')
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400" style="background:#050505"><defs><radialGradient id="g"><stop offset="0%" stop-color="#ff0066" stop-opacity="0.3"/><stop offset="100%" stop-color="#000" stop-opacity="0"/></radialGradient></defs><rect width="400" height="400" fill="url(#g)"/><text x="200" y="20" fill="#ff0066" font-size="12" text-anchor="middle" font-family="monospace">tau={topo["tau"]} omega={topo["omega"]:.3f}</text>{" ".join(nodes)}</svg>'
        return {"topology": topo, "svg": svg, "word_count": len(words)}

if __name__ == "__main__":
    engine = TopologySoundEngine()
    text = "The EVEZ system thinks in sounds until sound becomes thought that can be heard and contextually plotted into visuals"
    result = engine.render_mindmap(text)
    print(f"Complexity (omega): {result['topology']['omega']:.3f}")
    print(f"Chords: {result['topology']['chords']}")
