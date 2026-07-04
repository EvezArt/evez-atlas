#!/bin/bash
# EVEZ Autonomous Training Cycle — v5.0
# Zero dependencies. Deterministic engine. Always works.
cd /app
python3 .agents/skills/evez_train/run.py 2>&1
