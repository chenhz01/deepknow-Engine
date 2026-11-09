# deepknow-Engine — A dossier that makes any AI truly know a person

> **Know a person, not a persona.**
> **The human layer of the agent-skills ecosystem.** 中文版见 [README.md](README.md)。
>
> **Disclaimer:** independently developed; not affiliated with or endorsed by Anthropic / Claude Code, mem0, EverOS, SillyTavern, or DSH NEXT. Those names appear only as landscape references. Repository contract and the two-channel distribution rule: [`AGENTS.md`](AGENTS.md).

[![License: Apache-2.0](https://img.shields.io/badge/Code-Apache--2.0-blue.svg)](LICENSE-APACHE)
[![License: CC BY 4.0](https://img.shields.io/badge/Docs%20%26%20Templates-CC%20BY%204.0-green.svg)](LICENSE-CC-BY-4.0)
[![Tests](https://img.shields.io/badge/tests-21%2B%20cases%20green-brightgreen.svg)](scripts/test_v26.py)

Your AI agent forgets you every session. Memory layers (mem0, 68k★) fix *what the agent remembers*. Character cards fix *who the AI pretends to be*. Nobody fixes the third thing: **a structured, private, test-enforced profile of one real person** — your parent, your spouse, your client — so the AI doesn't perform care, it *knows*.

## Where we sit (one table)

| | Memory layers (mem0 / EverOS) | Character cards (SillyTavern) | **deepknow-Engine** |
|---|---|---|---|
| Captures | agent working memory | a fictional persona | **one real person** |
| Privacy | untyped | none | **load-time permissions + physical isolation + PII scanning** |
| Proactivity | none | LLM-improvised (uncontrollable) | **deterministic engine: quota / cooldown / quiet hours / default passive** |
| Form | SDK / service | frontend + card spec | **zero-dependency Markdown + JSON Schema, copy & run** |

One line: not a memory-layer competitor — **the missing human layer of the memory stack**.

## What it looks like

| You say | Without the dossier | With the dossier |
|---|---|---|
| "I'm exhausted today" | "Remember to rest! 🙂" | "Day 3 of back-to-back — you said no work after 23:00. Want me to cut tomorrow down to 3 tasks?" |
| Ask for investment advice | generic disclaimer | cites *his own* written risk bar, gently but firmly holds the line |
| Late night 23:00 | keeps replying | engine hits quiet-hours, suggests sleep first |

**Care is not performed, it is fed.** Every "I understand you" traces to a line in the dossier: his hot buttons, his unfinished projects, how he wants to be loved.

## Design commitments (enforced by a test, not promised in a doc)

All test matrices are open source — run them yourself: `python scripts/test_v26.py` (21 cases, 11 negative controls) and `python scripts/validate.py examples/example-dossier.json` (structure + PII scan).

| # | Commitment | Mechanism | Test backing |
|---|---|---|---|
| C1 | The AI can never read `private` sections | derived, redacted cards at load time; private content is physically outside the AI's reach | sha256 digest + validator suite |
| C2 | The AI can never write the dossier directly | it can only emit proposal JSON; every write path is deterministic code | injection / privilege / subject-swap poison packs → whole-pack reject, exit 2 |
| C3 | Tampering is detected on sight | digest re-signed only by the ingester; verified before every load | tamper tests abort everything, exit 3 |
| C4 | No signature, no effect | human approval gate + lazy expiry (med 24h / lifestyle 14d) | expired-reject + batch≥3 double-confirm tests |
| C5 | Behavior instructions can't sneak in | action-verb detection on payload + ANSI stripping | 3 red-team fixtures, all rejected |
| C6 | Proactivity never becomes nagging | default passive; daily quota 3, cooldown 2h, quiet hours — all hardcoded in the deterministic engine (the LLM never touches the gate) | engine design record in [docs/dialogue-hooks.md](docs/dialogue-hooks.md); a standalone test file is on the v2.7 list |

**Honest boundary:** the PII scanner reduces risk; it does not *guarantee* privacy. Your dossier lives on your disk and nowhere else.

## The dossier: six chapters

1. **Who he is** — identity, roles, place in the family web
2. **Money & red lines** — budget bars, never-cross decision rules
3. **Active projects** — what's running, what's frozen, why
4. **Temper & hot buttons** — what he hates, loves, has been burned by
5. **How he wants to be loved** — communication preferences, care that lands vs. care that offends
6. **Daily action list** — the executable translation of all five above

Chapter 6 is the soul: a dossier is not a biography, it is **a behavioral spec**.

## Growing dossier, human signature (v2.6)

```
conversation → ①extract (host-agent contract) → ②propose (AI writes nothing) → ③human approve → ④scan → ⑤ingest
```

```bash
python scripts/proposal.py submit pack.jsonl --dir proposals/
python scripts/proposal.py review --dir proposals/
python scripts/proposal.py approve --dir proposals/ --ids p-20261104-001   # batch ≤ 5; ≥3 needs --confirm-batch
python scripts/proposal.py ingest --dossier dossier.json --dir proposals/ --cardgen scripts/card-gen.py
```

Hard edges: the gene layer (slow variables) never enters the proposal loop; deletions are never physical; third-party info is not extracted by default; the subject's veto outranks the confirmer's approval.

## Quick start

```bash
# Install as a skill into your agent (auto-detects Claude Code / DSH NEXT)
bash scripts/install.sh          # macOS / Linux
powershell scripts/install.ps1   # Windows

# In your agent, say:
#   "Build a dossier for my mom"
# The agent interviews you and produces dossier.md + dossier.json

# Validate + PII scan (always run before sharing)
python scripts/validate.py examples/example-dossier.json
```

Zero dependencies (Python stdlib only). Pure Markdown + JSON. Local-only.

## Roadmap

| Version | Shipped | Evidence |
|---|---|---|
| v2.0 three-layer architecture | load-time permission engine (gene / dossier / card) | 10-persona adversarial brainstorm + validator suite |
| v2.5 dialogue hooks | the dossier that speaks first — deterministic triggers, default passive | 12-persona × 36-session review + 10-case engine tests |
| v2.6 update loop | growth under human signature: five deterministic gates | 8-persona × 24-session attack + 21-case acceptance (11 negative) |
| v2.7 (next) | supersede chain, multi-device export/import, more culture packs | — |

Two commercial editions are planned (Pro template packs for care organizations / warm CRM; done-for-you dossier interviews). The community edition stays free and open source, forever.

## For makers & vendors

Pre-install / partnership inquiries for desktop AI, companion robots, and CX systems: **hcac4735@agent.qq.com** (subject: deepknow).

## License

Dual-licensed: code under [Apache-2.0](LICENSE-APACHE); templates, docs and example dossiers under [CC BY 4.0](LICENSE-CC-BY-4.0).

## Acknowledgements

Inspired by the DSH NEXT persona-card community and the Claude agent-skills ecosystem. Competitor data pulled live from the GitHub Search API (Nov 2026) — full map in [docs/competitor-analysis.md](docs/competitor-analysis.md).
