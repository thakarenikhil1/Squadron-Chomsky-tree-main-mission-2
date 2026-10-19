# 02 — FST Dialogue Manager and Noisy Protocol

## 1. Mealy-style dialogue manager

The implementation models a finite-state transducer with state set:

- `INIT`
- `GREETING`
- `COLLECT_SLOTS`
- `CONFIRMATION`
- `TERMINAL`

`FALLBACK` is a response behavior, not a sixth persistent state, so the required five-state model remains explicit. For each input, the manager updates its state and emits an output. This is Mealy-style behavior because output depends on the current state and input.

The required slot buffer is `slot_memory = {}` with keys `destination`, `speed`, and `clearance_code`. Pattern extraction accepts natural-language variants and can collect multiple slots from one utterance, regardless of answer order.

## 2. Transition overview

| Current state | Input/condition | Next state | Output behavior |
|---|---|---|---|
| INIT | any initial input | GREETING | greet and request route details |
| GREETING | greeting or details | COLLECT_SLOTS | acknowledge and collect missing slots |
| COLLECT_SLOTS | slots incomplete | COLLECT_SLOTS | ask for missing values |
| COLLECT_SLOTS | all slots present | CONFIRMATION | summarize the route and request confirmation |
| CONFIRMATION | yes/confirm | TERMINAL | report confirmed |
| CONFIRMATION | no/correction | COLLECT_SLOTS | revise or re-collect details |
| any nonterminal | unusable/off-topic input | same or collection state | fallback, retain valid slot memory |
| TERMINAL | any input | TERMINAL | report that session is complete |

## 3. Noisy-channel constraint

Each assistant conversational turn is constrained to **at most seven whitespace-separated words**. The simulator applies one mandatory substitution per assistant turn, replacing one word with a token from:

`Banana, Labyrinth, Quantum, Midnight, Velocity, Green, Cosmological`

The noise token counts toward the seven-word limit. The transcript records both the clean and transmitted text, allowing comparison. User turns in the generated ten-turn demonstration are also kept short; the formal channel constraint is enforced on transmitted assistant turns.

## 4. Slot extraction

The regular-expression patterns recognize common forms such as:

- Destination: `destination: Mars`, `to Mars`, `heading to Mars`
- Speed: `speed: 12`, `at 12`, `12 knots`
- Clearance: `clearance code: AB12`, `code AB12`

Patterns are deliberately transparent and conservative. Real deployments would need validation, ambiguity handling, and a richer entity/slot parser.

## 5. Operational notes

The implementation is deterministic and offline. It does not require an API key. The noise channel is a controlled experiment, not a realistic model of all communication errors. The optional metrics estimate entropy and mutual information from the generated sample; small samples should not be treated as statistically stable.
