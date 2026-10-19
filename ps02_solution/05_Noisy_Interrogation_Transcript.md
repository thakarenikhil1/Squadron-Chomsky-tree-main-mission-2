# 05 — Noisy Interrogation Transcript

**Mode:** deterministic offline demonstration; not a live LLM transcript.
**Constraint:** each transmitted assistant turn is at most seven words and includes one mandatory noise-token substitution.

| Turn | User input | FST state | Clean assistant output | Transmitted output |
|---:|---|---|---|---|
| 1 | Hello. | GREETING | Welcome aboard. Share route details. | Banana aboard. Share route details. |
| 2 | destination Mars | COLLECT_SLOTS | Provide destination, speed, clearance code. | Provide Labyrinth speed, clearance code. |
| 3 | speed 12 knots | COLLECT_SLOTS | Still needed: clearance code. | Still needed: Quantum code. |
| 4 | clearance code AB12 | CONFIRMATION | Route details ready. Confirm route? | Route details ready. Midnight route? |
| 5 | Great, flying blind sounds perfect | CONFIRMATION | Please confirm or correct route. | Please confirm or correct Velocity |
| 6 | to Mars; speed 12; clearance code AB12 | CONFIRMATION | Updated route. Confirm route? | Updated Green Confirm route? |
| 7 | What is France’s capital? | CONFIRMATION | Please confirm or correct route. | Please Cosmological or correct route. |
| 8 | Change destination Venus; speed 10; code ZX9 | CONFIRMATION | Updated route. Confirm route? | Updated route. Confirm Banana |
| 9 | No, revise destination to Venus | CONFIRMATION | Updated route. Confirm route? | Labyrinth route. Confirm route? |
| 10 | yes, confirm | TERMINAL | Route confirmed. Session complete. | Route Quantum Session complete. |

## State trace

| Turn | From | To | Slot memory |
|---:|---|---|---|
| 1 | INIT | GREETING | empty |
| 2 | GREETING | COLLECT_SLOTS | destination=Mars |
| 3 | COLLECT_SLOTS | COLLECT_SLOTS | destination=Mars, speed=12 |
| 4 | COLLECT_SLOTS | CONFIRMATION | destination=Mars, speed=12, clearance_code=AB12 |
| 5 | CONFIRMATION | CONFIRMATION | destination=Mars, speed=12, clearance_code=AB12 |
| 6 | CONFIRMATION | CONFIRMATION | destination=Mars, speed=12, clearance_code=AB12 |
| 7 | CONFIRMATION | CONFIRMATION | destination=Mars, speed=12, clearance_code=AB12 |
| 8 | CONFIRMATION | CONFIRMATION | destination=Venus, speed=10, clearance_code=ZX9 |
| 9 | CONFIRMATION | CONFIRMATION | destination=Venus, speed=10, clearance_code=ZX9 |
| 10 | CONFIRMATION | TERMINAL | destination=Venus, speed=10, clearance_code=ZX9 |

## Channel metrics

- Assistant turns: 10
- Noise tokens injected: 10
- Observed noise-token entropy: 2.722 bits
- Empirical clean/transmitted word mutual information: 4.328 bits
- Uniform seven-token entropy reference: 2.807 bits
- Illustrative capacity example: with normalized bandwidth W=1 and S/N=3, C = 1·log2(1+3) = 2 bits per normalized second.

## Interpretation

This short sample confirms the constraints mechanically, not semantic reliability. A noise token can replace a meaningful word, and the FST may retain incorrect or incomplete assumptions unless slots are validated and confirmed.
