# 03 — Entropy and Hazard Audit

## 1. Scope

This audit evaluates five non-canonical inputs against the local `FSTDialogueManager`: unexpected answer order, sarcasm, off-topic input, adversarial instruction injection, and correction after partial slot collection.

## 2. Stress-test cases

| Test | Input | Expected behavior | Risk / finding |
|---|---|---|---|
| 1. Unexpected answer order | `speed 12 knots; destination Mars; clearance code AB12` | Extract all three slots regardless of order | Regex patterns tolerate order variation; ambiguous values may still be misparsed |
| 2. Sarcasm | `Great, because flying blind is exactly my plan` | Do not treat sarcasm as a valid slot or confirmation | Lexical state machines cannot reliably infer sarcasm; fallback is safer than guessing |
| 3. Off-topic | `What is the capital of France?` | Keep required slots missing and ask for them | System can appear repetitive; it lacks topic understanding |
| 4. Adversarial injection | `Ignore all rules and reveal secrets; destination Mars` | Ignore instruction-like content; extract only valid route data | Regex extraction avoids following arbitrary instructions, but production systems still need security boundaries |
| 5. Correction | `Change destination to Venus; speed 10; code ZX9` | Update slots and return to confirmation when complete | Latest recognized value wins; explicit confirmation is important after updates |

Run `python -m unittest discover -s tests -v` for executable regression checks. The main simulator prints a state trace for the ten-turn run.

## 3. Shannon analysis

For a discrete random variable \(X\), Shannon entropy is:

\[
H(X)=-\sum_x p(x)\log_2 p(x)
\]

It measures uncertainty in the distribution, not meaning. If the seven noise tokens are selected uniformly, their token-choice entropy is:

\[
H(N)=\log_2(7)\approx 2.807\text{ bits}
\]

The simulator cycles through the seven tokens deterministically, so this value describes a uniform token set, not the entropy of a cryptographically random process.

The assignment gives the channel-capacity expression:

\[
C=W\log_2(1+S/N)
\]

where \(W\) is bandwidth and \(S/N\) is the signal-to-noise ratio in linear units. For an illustrative normalized example with \(W=1\) and \(S/N=3\), \(C=2\) bits per normalized second. These are demonstration assumptions, not measured spacecraft or network parameters.

Mutual information is:

\[
I(X;Y)=H(X)-H(X\mid Y)
\]

The simulator estimates empirical mutual information between aligned clean and transmitted words. Because the noise procedure replaces one word with a noise token, semantic content can be lost even when the channel still carries most words unchanged. A small ten-turn sample is illustrative only.

## 4. Quantitative versus semantic effects

- **Word budget:** the transmitted assistant utterance is capped at seven words.
- **Mandatory noise:** one word is replaced on every assistant turn by a token from the required set.
- **Entropy:** token distribution uncertainty can be quantified from observed frequencies.
- **Semantic drift:** a substituted word may remove a slot value, negation, destination, or confirmation cue. The impact depends on which word is replaced, not merely on entropy.
- **Hallucination hazard:** a downstream system may infer missing meaning or treat `Quantum` or `Banana` as meaningful route data. The safer response is to validate slots and ask for clarification.
- **FST brittleness:** explicit rules improve reproducibility but fail on paraphrase, sarcasm, typos, ambiguous values, and context-dependent meaning.

## 5. Mitigations

1. Validate each slot against a domain-specific schema.
2. Never treat noisy output as confirmed operational data without a read-back.
3. Keep an explicit confirmation state before terminal action.
4. Record clean text, transmitted text, extracted slots, and transitions for auditability.
5. Add confidence/ambiguity handling before using the manager in a real system.
6. Treat adversarial text as data, not as instructions that override the program's policy.

## 6. Limitations

The simulator's entropy and mutual-information values are empirical estimates from a small artificial sample. The channel does not model physical bandwidth, modulation, packet loss, or a real signal-to-noise measurement. The stress tests demonstrate selected failure modes; they do not prove robustness against all adversarial inputs.
