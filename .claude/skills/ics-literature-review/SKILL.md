---
name: ics-literature-review
description: Literature review workflow for this ICS anomaly-detection project - audit the Zotero corpus for the accuracy-vs-cost gap statement, maintain docs/literature_review.md and the .bib file, check coverage against the required seed set, and validate the bibliography with scripts/check_bibliography.py. Use when working on Milestone 1, adding or reviewing papers, building the related-work table, updating the gap statement, or checking the bibliography after a Zotero export.
---

# ICS Anomaly Detection - Literature Review

Project-specific companion to the general `reference-review` skill. That skill covers the
mechanics (locating a library, extracting PDF text, the audit method, bibliography rules); this
one supplies **what this project specifically needs to establish and defend**.

Read `ROADMAP.md` §3 and §4 for the full plan; `docs/adr/0001-scope.md` for the fixed decisions.

## Project setup

| Item | Location |
|---|---|
| Zotero storage | `C:\Users\kidus\Zotero\storage\<ITEMKEY>\*.pdf` |
| Bibliography | `docs/ICS Anomaly Detection.bib` (exported from Zotero) |
| Review table | `docs/literature_review.md` |
| Bibliography checker | `scripts/check_bibliography.py` (`make check-bib`) |
| Python env | `.venv` - `pypdf` installed as local tooling, deliberately **not** in `pyproject.toml` |

Run the checker after **every** Zotero re-export:

```bash
.venv/Scripts/python scripts/check_bibliography.py
```

## The contribution this review must protect

The project maps a **detection-quality vs. inference-cost Pareto frontier** for lightweight
detectors against a reproduced deep baseline, on open ICS datasets, under a rigorous metric
protocol. The literature review exists to prove that frontier is genuinely unmapped.

Framing rule: the project is **agnostic about which end of the frontier wins**. Recent
evaluations show simple baselines often match deep models on these datasets, so "a tiny model
matches the deep baseline at a fraction of the cost" is a *stronger* result than the expected
trade-off, not a failure. Never frame the review as "how much accuracy is sacrificed."

## Audit axes for this project

Scan every PDF for all three axes at once, then read context around hits before concluding
anything (see the general skill's "keyword hit proves mention, not measurement" rule).

**1. Datasets** - `SWaT`, `WADI`, `HAI`, plus general-TSAD benchmarks (`SMD`, `SMAP`, `MSL`)
which indicate a paper is *not* ICS-focused.

**2. Evaluation-metric variant** - the credibility axis for this subfield:

- point-adjusted scoring (`point-adjust`, `point adjustment`, `F1_PA`) - **inflates results
  dramatically**; random scores can reach near-SOTA under it
- range-based precision/recall (Tatbul-style)
- eTaPR / TaPR - designed for HAI
- PR-AUC / AUPRC / average precision
- affiliation-based, VUS

Record which variant each paper uses. Many are vague about it, and that vagueness is itself part
of the gap.

**3. Efficiency / cost** - the axis the contribution occupies:

- inference latency, detection time, throughput, response time
- model size, parameter count, memory footprint
- peak RAM / memory consumption
- energy or power consumption
- FLOPs / MACs
- edge hardware: Raspberry Pi, microcontroller, MCU, Jetson, Cortex-M, TFLite/LiteRT
- computational complexity, training time

### The distinctions that decide whether the gap survives

When a paper scores high on axis 3, read the context and classify it precisely:

- **Training cost vs. inference cost** - most "efficient" ICS papers report training time and
  parameter counts. The contribution is *inference* cost. This distinction is load-bearing.
- **Measured vs. estimated vs. copied** - model sizes derived from parameter counts are
  estimates; numbers quoted from other papers' hardware are not a controlled comparison.
- **One architecture family vs. cross-family** - variants of a single model are not a frontier
  across statistical / shallow-ML / tiny-NN families.
- **Controlled runtime vs. mixed hardware** - the whole contribution rests on apples-to-apples,
  single-runtime, single-threaded measurement.
- **Survey naming a direction as open vs. a paper closing it** - a recent systematic review
  listing lightweight edge deployment as future work is strong support; quote it.

## Required coverage (check gaps by category)

1. **Dataset papers** - the primary sources for SWaT, WADI, HAI, and the HAI contest paper
   (needed because HAI is the primary dataset and requires a comparison point)
2. **Evaluation rigor** - the point-adjustment critique, range-based metrics, eTaPR, the
   benchmark-flaws critiques, the position papers questioning deep TSAD, and the large
   comparative evaluations
3. **Heavy baselines** - the widely cited deep detectors reporting on these datasets; one becomes
   the Milestone 3 reproduction target
4. **Closest prior work** - lightweight/efficient ICS detectors. These are the papers that could
   occupy the gap; read them in full
5. **TinyML / edge anomaly detection** - need not be ICS-specific; borrow efficiency-measurement
   methodology
6. **Surveys** for positioning
7. **Adversarial robustness** - Phase 3 future work only

**When a must-cite is missing, mine reference lists.** The paper the review most needs is usually
cited by two or more papers already in the library.

## Gap statement

Maintain it in `docs/literature_review.md`, in countable form, and re-verify it whenever papers
are added. The defensible shape:

> Of the papers evaluating on these ICS datasets, N report any resource metric; those that do
> report **training** cost rather than **inference** cost; none report per-sample inference
> latency under a controlled single runtime across statistical, shallow-ML and tiny-NN families
> on a shared split; and none pair resource measurement with non-point-adjusted detection
> metrics. A recent systematic review still lists lightweight edge deployment as open.

Weaker claims like "nobody measures efficiency in ICS anomaly detection" are false and will be
caught. Precision is what makes the claim survive review.

## Review table columns

`docs/literature_review.md` keeps one row per paper:

| Paper | Dataset(s) | Model class | Detection metric **and variant** | Efficiency metrics reported | Split protocol notes | Take-away |

The split-protocol column matters because many papers are vague about train/test separation,
which connects directly to the project's leakage discussion (`ROADMAP.md` §6).

## Bibliography specifics

- **Dialect**: target venues for this work (IEEE, ACM, Springer LNCS, USENIX) expect **classic
  BibTeX**. In Zotero's export dropdown, "Better BibLaTeX" sits immediately above "Better
  BibTeX" - verify by file content (`journal`/`year` = correct; `journaltitle`/`date` = wrong),
  never by the UI label. Record the final choice in an ADR when the venue is chosen.
- **The `.bib` is generated** - mirror every fix in Zotero, or the next export discards it. This
  has already happened more than once in this project.
- **Non-literature items** (dataset landing pages, community code repos) belong in
  `docs/data_card.md`, not the related-work bibliography.
- **Preprints**: cite what is actually accessible. Where the published version is paywalled and
  unavailable, citing the preprint is the honest choice. The ideal entry carries both the venue
  and the eprint.

## Triage against the paper budget

`ROADMAP.md` §3 budgets 15-25 papers for a credible related-work section. With a larger corpus,
split effort:

- **Deep-read**: dataset papers, the closest lightweight prior work, the chosen heavy baseline,
  and the metric-protocol papers
- **Skim for the table**: general ICS detector papers - their value is being a *row* in the
  tally; each one omitting inference cost is evidence for the gap
- **Cite-only**: surveys and positioning references

## Self-check

- [ ] `scripts/check_bibliography.py` reports zero errors
- [ ] Every PDF in Zotero storage is identified and appears in the review table or is explicitly
      excluded
- [ ] The gap statement is countable, and the tally is reproducible from a script
- [ ] The closest lightweight prior work has been read in context, not keyword-scanned
- [ ] Every table row records the metric **variant**, not just the metric name
- [ ] Claims distinguish training cost from inference cost throughout
