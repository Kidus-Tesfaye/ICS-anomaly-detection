# Literature Review (Milestone 1)

Strategy: seed set → citation snowball (1–2 hops) → table → gap statement. Budget 15–25 papers.
See ROADMAP.md §3 for the full strategy and the must-cite evaluation-rigor line of work.

## Gap statement (write once the table is populated)

> TODO — target form: "N papers report detection metrics on SWaT/HAI; M report any
> latency/resource metric; 0 map a Pareto frontier across model families on a shared split
> with rigorous (point-wise + range-aware) metrics."

## Comparison table

| Paper (year) | Dataset(s) | Model class | Detection metric & **variant** (point-wise / point-adjusted / range-aware) | Efficiency metric (if any) | Split protocol notes | Take-away for us |
|---|---|---|---|---|---|---|
| SWaT dataset paper (Goh et al. 2016) | SWaT | — | — | — | defines attack taxonomy | TODO |
| HAI dataset paper (Shin et al.) | HAI | — | eTaPR introduced | — | | TODO |
| Kim et al. (AAAI 2022), rigorous TSAD evaluation | multiple | — | shows point-adjust inflation | — | | must-cite; defines our metric protocol |
| Tatbul et al. (NeurIPS 2018) | — | — | range-based P/R | — | | metric option |
| Audibert et al. (2022), "Do DNNs contribute...?" | SWaT, WADI, ... | deep vs. simple | | | | simple baselines competitive |
| "Quo Vadis, Unsupervised TSAD?" (ICML 2024) | multiple | — | | | | benchmark/method critique |
| Wu & Keogh, benchmark flaws | multiple | — | | | | dataset caveats for limitations section |
| USAD (Audibert et al., KDD 2020) | SWaT, WADI | deep AE-adversarial | | | | heavy-baseline candidate |
| TODO: LSTM-AE / GDN / GAN-based detector | | | | | | heavy-baseline candidate |
| TODO: 2–3 TinyML/edge anomaly detection papers | | | | | | efficiency-measurement methodology |

## References

Maintain `references.bib` alongside this file; every table row gets a BibTeX entry.
