# ADR-0001: Project scope and core methodology decisions

- Status: accepted
- Date: 2026-07-15

## Context

Turning the "lightweight anomaly detection for ICS traffic" proposal into a rigorous,
reproducible public project (see ROADMAP.md). Several decisions must be fixed up front because
they shape every later milestone.

## Decisions

1. **Primary dataset: HAI; secondary: SWaT.** HAI is publicly downloadable with no
   registration and ships eTaPR tooling, so anyone can reproduce the pipeline immediately.
   SWaT requires an iTrust request (submitted in week 1) and joins in M7 for the
   generalization claim. WADI/Electra are out of scope for v1.
2. **Split strategy: contiguous time blocks with a boundary gap ≥ window size.** Random
   row-level splits leak on autocorrelated ICS time series. Enforced by automated tests in
   `tests/data_validation/`.
3. **Metric protocol: point-wise P/R/F1/PR-AUC + range-aware (eTaPR) + time-to-detection.**
   Point-adjusted F1 is never a headline number (random scores can achieve near-SOTA
   point-adjusted F1 — Kim et al., AAAI 2022). Thresholds are selected on validation only.
4. **Heavy baseline: one reproduced deep model (LSTM-AE or USAD) on HAI.** Reproduced numbers
   are reported next to the source paper's, with deviations discussed.
5. **Lightweight suite v1: PCA reconstruction, Isolation Forest, tiny autoencoder** (CUSUM/EWMA
   as stretch), all behind one `fit`/`score`/`predict` interface driven by YAML configs.
6. **Single inference runtime for cost benchmarking: ONNX Runtime, single-threaded.**
   Classical models via skl2onnx, NNs via ONNX export. One runtime keeps the latency
   comparison apples-to-apples. (TensorFlow Lite — now LiteRT — is deferred to the
   on-device future-work phase.)
7. **Framing: map the Pareto frontier, agnostic about which end wins.** Recent evaluations
   (Audibert 2022; Quo Vadis, ICML 2024) show simple baselines often match deep models on
   these datasets; "light matches heavy at 1/100th the cost" is a valid headline result.
8. **v1 "done" definition:** the final-deliverables checklist in ROADMAP.md §14, headlined by
   a `make reproduce` that regenerates the Pareto figure from raw data.

## Consequences

- Anyone can run the full HAI pipeline without waiting on dataset access.
- Evaluation choices are defensible to domain reviewers and testable in CI.
- Resource numbers are honest constrained-CPU estimates; on-device measurement is explicitly
  future work, not an implied claim.
