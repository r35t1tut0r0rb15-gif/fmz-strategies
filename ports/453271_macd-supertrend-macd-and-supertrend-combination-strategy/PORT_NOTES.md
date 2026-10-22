# #453271 MACD与Supertrend组合策略-MACD-and-Supertrend-Combination-Strategy -> `fmz_453271_macd_side_supertrend_confirm_reversal`

- FMZ source id: 453271 (lineage).
- Source: https://www.fmz.com/strategy/453271 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-03 16:35:15). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C192). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD side with Supertrend confirmation |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`st_len` [10, 14] x `st_mult` [3.0, 2.0]: **4 trials**; the MACD lengths fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
