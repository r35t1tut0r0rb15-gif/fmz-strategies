# #446453 Variance and Moving Averages Based Volatility Strategy -> `fmz_446453_calm_range_sma_stack_one_bar_hold_long`

- FMZ source id: 446453 (lineage).
- Source: https://www.fmz.com/strategy/446453 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-28 17:33:08). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C174). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Calm-range trend entries with a one-bar hold |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`var_max` [35.0, 100.0] x `var_len` [30, 50]: **4 trials**; the SMA lengths fixed.

## Ambiguities resolved

- Always-true close: one-bar holds, as written. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
