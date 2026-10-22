# #453657 Supertrend和EMA组合策略-Supertrend-and-EMA-Combination-Strategy -> `fmz_453657_ema20_50_cross_classic_supertrend_long`

- FMZ source id: 453657 (lineage).
- Source: https://www.fmz.com/strategy/453657 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-06-07 15:36:41). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C193). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings with a Supertrend filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity sizing stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_len` [10, 14] x `mult` [3.0, 2.0] x `short_ema` [20, 10]: **8 trials**; the EMA 50 fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
