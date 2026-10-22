# #451389 Dual Moving Average Crossover Strategy -> `fmz_451389_typical_price_ema20_cross_long`

- FMZ source id: 451389 (lineage).
- Source: https://www.fmz.com/strategy/451389 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-14 15:37:54). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C184). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Typical-price / EMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`long_len` [20, 50] x `short_len` [1, 5]: **4 trials**; the EMA type and the typical price fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
