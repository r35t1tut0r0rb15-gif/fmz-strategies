# #458252 双重RSI策略结合背离与交叉的高级趋势捕捉系统-Dual-RSI-Strategy-Advanced-Trend-Capture-System-Combining-Divergence-and-Crossover -> `fmz_458252_rsi_threshold_cross_latched_divergence_reversal`

- FMZ source id: 458252 (lineage).
- Source: https://www.fmz.com/strategy/458252 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-07-31 11:55:12). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C204). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI threshold crossings gated by latched divergences |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len` [14, 7] x `xbars` [90, 45]: **4 trials**; the thresholds 30 / 70 fixed.

## Ambiguities resolved

- Divergence flags never cleared (as written); ties at the window high read as the current bar. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
