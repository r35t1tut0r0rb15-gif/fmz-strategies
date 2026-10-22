# #440369 坚果123反转与突破范围短线交易策略Peanut-123-Reversal-and-Breakout-Range-Short-term-Trading-Strategy -> `fmz_440369_reversal123_breakout_range_short`

- FMZ source id: 440369 (lineage).
- Source: https://www.fmz.com/strategy/440369 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-29 16:31:04). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C133). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close pattern, stochastic and a range breakout |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND426888. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `look_bak` [4, 10]: **4 trials**; the 123 smoothing fixed.

## Ambiguities resolved

- Short or flat only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
