# ADR-0001: Project scope and core methodology decisions

- Status: accepted
- Date: 2026-07-15

## Context

Turning the "lightweight anomaly detection for ICS traffic" proposal into a rigorous,
reproducible public project 

## Decisions

1. HAI is used as a primary dataset while SWaT and WADI are reserved as secondary as they require iTrust    permission. 
2. A sliding window split is used rather than a randow row level split as the latter might leak information from training to testing/validation sets. 
3. Metric protocol
   -  point-wise P/R/F1/PR-AUC + range-aware (eTaPR) + time-to-detection.
4. One reproduced deep model (LSTM-AE or USAD)  is tested on HAI and its reproduced numbers
   are reported next to the source paper's, with deviations discussed.
5. Single inference runtime for cost benchmarking using skl2onnx for Classical models, and ONNX for NNs. One runtime keeps the latency comparison fair.
6. Framing Recent evaluations
   (Audibert 2022; Quo Vadis, ICML 2024) show simple baselines often match deep models on
   these datasets. So "light matches heavy at 1/100th the cost" is an achievable target.


## Consequences

- Anyone can run the full HAI pipeline without waiting on dataset access.
- Evaluation choices are defensible to domain reviewers and testable in CI.
- Resource numbers are honest constrained-CPU estimates; on-device measurement is at the 
moment an explicit future work.
