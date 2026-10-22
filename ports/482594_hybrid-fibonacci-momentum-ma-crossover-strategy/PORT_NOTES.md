# #482594 Hybrid Fibonacci Momentum MA Crossover Strategy -> `fmz_482594_sma9_21_cross_pct2_4_bracket_reversal`

- FMZ source id: 482594 (lineage).
- Source: https://www.fmz.com/strategy/482594 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-19 11:02:16). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C247). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket from the signal close as fractions of the fill |
| 2 | PASS | SMA crossings with a percent bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_loss_percentage` [2, 4] x `take_profit_percentage` [4, 8]: **4 trials**; SMA 9 / 21.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
