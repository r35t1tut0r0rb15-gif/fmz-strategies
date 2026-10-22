# #476270 Cross boundary Dynamic Range Quantitative Trading Strategy Based on Bollinger Bands -> `fmz_476270_bb20_lower_reentry_upper_reentry_close_long`

- FMZ source id: 476270 (lineage).
- Source: https://www.fmz.com/strategy/476270 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-27 15:39:49). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C231). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bollinger band re-entries |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty 86 USDT / close and capital 86 stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `mult` [2.0, 2.5]: **4 trials**.

## Ambiguities resolved

- The balance tests always pass (non-var, reset each bar). Long only. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
