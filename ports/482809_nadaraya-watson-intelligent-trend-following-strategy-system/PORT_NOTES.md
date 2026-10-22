# #482809 基于Nadaraya-Watson核估计和移动平均交叉的智能趋势跟踪策略系统-Intelligent-Trend-Following-Strategy-System-Based-on-Nadaraya-Watson-Kernel-Estimation-and-Moving-Average-Crossover -> `fmz_482809_nadaraya_watson8_sma15_cross_alternating_reversal`

- FMZ source id: 482809 (lineage).
- Source: https://www.fmz.com/strategy/482809 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 14:54:41). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C250). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Kernel-smoothed close crossing its SMA |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bandwidth` [8.0, 4.0] x `lookback` [15, 30]: **4 trials**; 500-bar kernel.

## Ambiguities resolved

- One-sided (causal) kernel, na for the first 499 bars, as the source's na sum gives.
- The inPosition flag is followed in a loop. MPL 2.0 source, ported and stated. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "adaptive_average"`.

## Marks

`none`
