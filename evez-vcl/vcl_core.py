#!/usr/bin/env python3
"""
EVEZ Visual Cognition Layer (VCL) v0.1
Generates visual artifacts from agent cognition states.
"""
import json, math
from pathlib import Path

class VisualCognitionLayer:
    def __init__(self):
        self.artifacts = []

    def cognition_to_svg(self, cognition_state):
        """Convert agent cognition state to visual artifact."""
        phi = cognition_state.get("phi", 0.5)
        depth = cognition_state.get("recursive_depth", 1)
        agents = cognition_state.get("agent_count", 1)

        # Generate neural network visualization
        nodes = []
        edges = []
        for i in range(agents):
            angle = (i / max(agents, 1)) * 2 * math.pi
            r = 50 + (phi * 100)
            x = 200 + r * math.cos(angle)
            y = 200 + r * math.sin(angle)
            nodes.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{5+depth*2:.1f}" fill="#ff0066" opacity="{phi:.2f}"/>')
            if i > 0:
                edges.append(f'<line x1="200" y1="200" x2="{x:.1f}" y2="{y:.1f}" stroke="#6600ff" opacity="0.3"/>')

        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400" style="background:#050505">{" ".join(edges)}{" ".join(nodes)}<circle cx="200" cy="200" r="{10+depth*3:.1f}" fill="#ff0066" opacity="0.8"/><text x="200" y="20" fill="#ff0066" font-size="12" text-anchor="middle" font-family="monospace">phi={phi:.3f} depth={depth}</text></svg>'

        artifact = {
            "type": "cognition_svg",
            "phi": phi,
            "depth": depth,
            "agents": agents,
            "svg": svg,
            "size_bytes": len(svg)
        }
        self.artifacts.append(artifact)
        return artifact

    def get_gallery(self):
        return self.artifacts

if __name__ == "__main__":
    vcl = VisualCognitionLayer()
    state = {"phi": 0.995, "recursive_depth": 4, "agent_count": 12}
    art = vcl.cognition_to_svg(state)
    print(f"Artifact: {art['size_bytes']} bytes, phi={art['phi']}")
