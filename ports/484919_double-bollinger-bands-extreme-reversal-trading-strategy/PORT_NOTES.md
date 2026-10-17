# #484919 双布林带极值反转交易策略-Double-Bollinger-Bands-Extreme-Reversal-Trading-Strategy -> `fmz_484919_double_bollinger_reversal`

- FMZ source id: 484919 (lineage).
- Source: https://www.fmz.com/strategy/484919 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-05 10:10:08). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L14). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bands. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 40] x `outer_mult` [3.0, 2.5]: **4 trials**; defaults 20 / 3 (the source's); inner bands 2 sigma fixed.

## Ambiguities resolved

- Closes act on the position at the bar's start (#430850). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
