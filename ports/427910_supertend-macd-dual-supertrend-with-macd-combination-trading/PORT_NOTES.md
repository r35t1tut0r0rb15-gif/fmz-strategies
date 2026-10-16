# #427910 Dual SuperTrend with MACD Combination Trading Strategy -> `fmz_427910_dual_supertrend_macd`

- FMZ source id: 427910 (lineage).
- Source: https://www.fmz.com/strategy/427910 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-26 17:45:03). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C14). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | ATR multiples and MACD lengths. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Commented strategy() sizing stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor1` [3, 2] x `factor2` [5, 3] x `atr1` [10, 14]: **8 trials**; defaults 3 / 5 / 10 (the source's); ATR 2 period 20 and MACD 12/26/9 fixed.

## Ambiguities resolved

- ta.supertrend as Pine v5 (worker A's helper). strategy() commented out; direction "both".
- REVERSAL INTENDED. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
