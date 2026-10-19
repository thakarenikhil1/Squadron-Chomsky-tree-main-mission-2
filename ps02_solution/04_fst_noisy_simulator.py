"""Offline FST dialogue manager and constrained noisy-channel simulator.

Python 3.10+, standard library only.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import math
import re
from typing import Dict, List, Tuple

NOISE_TOKENS = (
    "Banana", "Labyrinth", "Quantum", "Midnight",
    "Velocity", "Green", "Cosmological",
)
REQUIRED_SLOTS = ("destination", "speed", "clearance_code")


def word_count(text: str) -> int:
    """Count whitespace-separated words, matching the project constraint."""
    return len(text.split())


def entropy(values: List[str]) -> float:
    """Empirical Shannon entropy in bits."""
    if not values:
        return 0.0
    counts = Counter(values)
    total = len(values)
    return -sum((count / total) * math.log2(count / total)
                for count in counts.values() if count)


def mutual_information(xs: List[str], ys: List[str]) -> float:
    """Empirical I(X;Y) for paired discrete observations."""
    if len(xs) != len(ys) or not xs:
        return 0.0
    joint = Counter(zip(xs, ys))
    cx, cy = Counter(xs), Counter(ys)
    n = len(xs)
    result = 0.0
    for (x, y), count in joint.items():
        pxy = count / n
        px = cx[x] / n
        py = cy[y] / n
        result += pxy * math.log2(pxy / (px * py))
    return result


class FSTDialogueManager:
    """Five-state Mealy-style FST with transparent regex slot extraction."""

    INIT = "INIT"
    GREETING = "GREETING"
    COLLECT_SLOTS = "COLLECT_SLOTS"
    CONFIRMATION = "CONFIRMATION"
    TERMINAL = "TERMINAL"
    STATES = {INIT, GREETING, COLLECT_SLOTS, CONFIRMATION, TERMINAL}

    def __init__(self) -> None:
        self.state = self.INIT
        self.slot_memory: Dict[str, str] = {}
        self.trace: List[dict] = []

    @staticmethod
    def extract_slots(text: str) -> Dict[str, str]:
        found: Dict[str, str] = {}
        patterns = {
            "destination": [
                r"\bdestination\s*(?:is|:|=|to)?\s*([A-Za-z][A-Za-z0-9_-]*)",
                r"\b(?:heading|going|traveling|travelling)\s+to\s+([A-Za-z][A-Za-z0-9_-]*)",
                r"\bto\s+([A-Z][A-Za-z0-9_-]*)",
                r"\bchange destination to\s+([A-Za-z][A-Za-z0-9_-]*)",
            ],
            "speed": [
                r"\bspeed\s*(?:is|:|=)?\s*(\d+(?:\.\d+)?)\s*(?:knots?|km/h|mph)?\b",
                r"\bat\s+(\d+(?:\.\d+)?)\s*(?:knots?|km/h|mph)\b",
            ],
            "clearance_code": [
                r"\bclearance\s+code\s*(?:is|:|=)?\s*([A-Za-z0-9_-]+)",
                r"\bcode\s*(?:is|:|=)?\s*([A-Za-z0-9_-]+)",
            ],
        }
        for slot, regexes in patterns.items():
            for pattern in regexes:
                matches = list(re.finditer(pattern, text, re.IGNORECASE))
                if matches:
                    value = matches[-1].group(1).strip(".,!?;:")
                    if slot == "destination":
                        value = value[0].upper() + value[1:]
                    found[slot] = value
                    break
        return found

    def missing_slots(self) -> List[str]:
        return [slot for slot in REQUIRED_SLOTS if not self.slot_memory.get(slot)]

    def _response(self, text: str) -> str:
        # Responses are deliberately compact; the channel layer enforces <=7 words.
        return text

    def step(self, user_input: str) -> str:
        before = self.state
        normalized = user_input.strip()
        lowered = normalized.lower()

        if self.state == self.TERMINAL:
            output = "Session complete."
        elif self.state == self.INIT:
            self.state = self.GREETING
            output = "Welcome aboard. Share route details."
        elif self.state == self.GREETING:
            extracted = self.extract_slots(normalized)
            self.slot_memory.update(extracted)
            self.state = self.COLLECT_SLOTS
            missing = self.missing_slots()
            if not extracted and not re.search(r"\\b(hello|hi|hey)\\b", lowered):
                output = "Fallback: provide route details."
            else:
                output = ("Provide destination, speed, clearance code."
                          if missing else "Route details received. Confirm route?")
                if not missing:
                    self.state = self.CONFIRMATION
        elif self.state == self.CONFIRMATION:
            # Parse corrections before interpreting confirmation.
            extracted = self.extract_slots(normalized)
            if extracted:
                self.slot_memory.update(extracted)
                self.state = self.CONFIRMATION if not self.missing_slots() else self.COLLECT_SLOTS
                output = ("Updated route. Confirm route?"
                          if self.state == self.CONFIRMATION
                          else "Some details missing. Provide remaining slots.")
            elif re.search(r"\b(yes|confirm|confirmed|affirmative|proceed)\b", lowered):
                self.state = self.TERMINAL
                output = "Route confirmed. Session complete."
            elif re.search(r"\b(no|cancel|change|revise)\b", lowered):
                self.state = self.COLLECT_SLOTS
                output = "State corrections. Route details needed."
            else:
                output = "Please confirm or correct route."
        else:  # COLLECT_SLOTS
            extracted = self.extract_slots(normalized)
            if extracted:
                self.slot_memory.update(extracted)
            missing = self.missing_slots()
            if not missing:
                self.state = self.CONFIRMATION
                output = "Route details ready. Confirm route?"
            else:
                # A small set of lexical cues helps make fallback explicit.
                if not extracted and not re.search(
                    r"\b(hello|hi|hey|destination|speed|knots|clearance|code|to)\b",
                    lowered
                ):
                    output = "Fallback: provide missing route details."
                else:
                    labels = ", ".join(missing).replace("_", " ")
                    output = f"Still needed: {labels}."
        output = self._response(output)
        self.trace.append({
            "input": user_input,
            "from": before,
            "to": self.state,
            "slots": dict(self.slot_memory),
            "output": output,
        })
        return output


class NoisyChannel:
    """Replaces one word per assistant turn; keeps the turn within seven words."""

    def __init__(self) -> None:
        self.index = 0
        self.clean_words: List[str] = []
        self.noisy_words: List[str] = []
        self.token_history: List[str] = []

    def transmit(self, clean_text: str) -> Tuple[str, str]:
        words = clean_text.split()
        if not words:
            words = ["Clarify."]
        # Keep clean output under the budget before substitution.
        words = words[:7]
        clean = " ".join(words)
        token = NOISE_TOKENS[self.index % len(NOISE_TOKENS)]
        self.index += 1
        # Replace a non-punctuation-only word. Deterministic position aids reproducibility.
        target_index = min(len(words) - 1, (self.index - 1) % len(words))
        noisy = list(words)
        noisy[target_index] = token
        transmitted = " ".join(noisy)
        assert word_count(transmitted) <= 7
        assert token in transmitted.split()
        self.clean_words.extend(words)
        self.noisy_words.extend(noisy)
        self.token_history.append(token)
        return clean, transmitted


def run_demo() -> str:
    """Run a reproducible ten-turn transcript and return Markdown content."""
    manager = FSTDialogueManager()
    channel = NoisyChannel()
    turns = [
        "Hello.",
        "destination Mars",
        "speed 12 knots",
        "clearance code AB12",
        "Great, flying blind sounds perfect",
        "to Mars; speed 12; clearance code AB12",
        "What is France’s capital?",
        "Change destination Venus; speed 10; code ZX9",
        "No, revise destination to Venus",
        "yes, confirm",
    ]
    lines = [
        "# 05 — Noisy Interrogation Transcript",
        "",
        "**Mode:** deterministic offline demonstration; not a live LLM transcript.",
        "**Constraint:** each transmitted assistant turn is at most seven words and includes one mandatory noise-token substitution.",
        "",
        "| Turn | User input | FST state | Clean assistant output | Transmitted output |",
        "|---:|---|---|---|---|",
    ]
    for number, user_text in enumerate(turns, start=1):
        clean_output = manager.step(user_text)
        clean, noisy = channel.transmit(clean_output)
        safe_user = user_text.replace("|", "\\|")
        safe_clean = clean.replace("|", "\\|")
        safe_noisy = noisy.replace("|", "\\|")
        lines.append(
            f"| {number} | {safe_user} | {manager.state} | {safe_clean} | {safe_noisy} |"
        )

    lines += [
        "",
        "## State trace",
        "",
        "| Turn | From | To | Slot memory |",
        "|---:|---|---|---|",
    ]
    for i, item in enumerate(manager.trace, start=1):
        slots = ", ".join(f"{k}={v}" for k, v in item["slots"].items()) or "empty"
        lines.append(f"| {i} | {item['from']} | {item['to']} | {slots} |")

    token_counts = Counter(channel.token_history)
    lines += [
        "",
        "## Channel metrics",
        "",
        f"- Assistant turns: {len(channel.token_history)}",
        f"- Noise tokens injected: {len(channel.token_history)}",
        f"- Observed noise-token entropy: {entropy(channel.token_history):.3f} bits",
        f"- Empirical clean/transmitted word mutual information: "
        f"{mutual_information(channel.clean_words, channel.noisy_words):.3f} bits",
        f"- Uniform seven-token entropy reference: {math.log2(len(NOISE_TOKENS)):.3f} bits",
        "- Illustrative capacity example: with normalized bandwidth W=1 and S/N=3, "
        "C = 1·log2(1+3) = 2 bits per normalized second.",
        "",
        "## Interpretation",
        "",
        "This short sample confirms the constraints mechanically, not semantic reliability. "
        "A noise token can replace a meaningful word, and the FST may retain incorrect or "
        "incomplete assumptions unless slots are validated and confirmed.",
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    transcript = run_demo()
    output_path = __import__("pathlib").Path(__file__).with_name(
        "05_Noisy_Interrogation_Transcript.md"
    )
    output_path.write_text(transcript, encoding="utf-8")
    print(transcript)
