# #440982 Bollinger-Bands与RSI组合交易策略Bollinger-Bands-and-RSI-Combination-Trading-Strategy -> `fmz_440982_bb_reentry_rsi_extreme_reversal`

- FMZ source id: 440982 (lineage).
- Source: https://www.fmz.com/strategy/440982 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-04 15:09:35). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C143). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bollinger re-entries and RSI |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG440982. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `rsi_oversold` [30, 40]: **4 trials**; overbought = 100 - oversold.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
