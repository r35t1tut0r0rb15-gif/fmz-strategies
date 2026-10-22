# #454762 Machine Learning Based Moving Average Crossover Quantitative Trading Strategy -> `fmz_454762_sma9_21_cross_reversal`

- FMZ source id: 454762 (lineage).
- Source: https://www.fmz.com/strategy/454762 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-21 17:59:06). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C197). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_len` [9, 5] x `long_len` [21, 50]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
