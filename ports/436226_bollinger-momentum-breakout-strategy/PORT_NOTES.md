# #436226 Bollinger Momentum Breakout Strategy -> `fmz_436226_bollinger_breakout_rsi_window`

- FMZ source id: 436226 (lineage).
- Source: https://www.fmz.com/strategy/436226 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-22 13:09:32). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C87). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band breakouts with an RSI window |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 30] x `mult` [2.0, 1.5]: **4 trials**; RSI 14 and its windows fixed.

## Ambiguities resolved

- Orders in call order; start date dropped. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
