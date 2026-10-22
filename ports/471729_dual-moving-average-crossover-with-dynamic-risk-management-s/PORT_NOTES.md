# #471729 Dual Moving Average Crossover with Dynamic Risk Management Strategy -> `fmz_471729_ema20_50_cross_pct_close_tests_long`

- FMZ source id: 471729 (lineage).
- Source: https://www.fmz.com/strategy/471729 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-12 17:29:24). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C211). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the stop and target are close tests |
| 2 | PASS | EMA crossings with percent close tests |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [20, 10] x `slow` [50, 100] x `sl_pct` [0.025, 0.05]: **8 trials**; the 4 % target fixed.

## Ambiguities resolved

- Close tests against the signal close. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
