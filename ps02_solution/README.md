# PS02 — FST Dialogue Systems, Lovelace’s Objection & Noisy Channels

**Course:** Conversational AI — Winter Semester 2026/27  
**Mission:** 2 — FST Dialogue Systems, Lovelace’s Objection & Noisy Channels

This repository-ready solution implements the five deliverable groups specified in `ps02.pdf`.

## Quick start

Requires Python 3.10+; the simulator uses only the Python standard library.

```bash
python 04_fst_noisy_simulator.py
python -m unittest discover -s tests -v
```

The simulator writes a readable transcript to `05_Noisy_Interrogation_Transcript.md` and prints state traces plus channel metrics.

## Repository layout

```text
ps02_solution/
├── 01_Lovelace_Inquiry_Brief.md
├── 02_FST_and_Noisy_Protocol.md
├── 03_Entropy_Hazard_Audit.md
├── 04_fst_noisy_simulator.py
├── 05_Noisy_Interrogation_Transcript.md
├── ps02_solution.ipynb
├── README.md
└── tests/
    └── test_fst_dialogue_manager.py
```

## Important evidence boundary

The Anti-Turing section contains five proposed probes and a clearly labeled **illustrative example evaluation**, not a claim that Gemini, ChatGPT, or Claude were queried live. Replace the example with verbatim responses from a model session in VS Code + Antigravity before submitting that part as empirical evidence. Likewise, the simulator is a reproducible local/offline implementation; it does not require an API key and does not claim to measure a frontier model's internal cognition.

## GitHub workflow

Create or open your course repository, then add these files and commit them. The assignment PDF names the course repository as `https://github.com/Unisvet/couse-c-ai`; your team should submit its own public repository URL under the course instructions. Do not commit API keys or private credentials.
