# #444009 Bollinger Bands Breakout with Volatility Filter Strategy -> `fmz_444009_deep_bb_break_calm_bar_long_1m`

- FMZ source id: 444009 (lineage).
- Source: https://www.fmz.com/strategy/444009 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-08 15:28:05). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C169). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Deep band breaks with a calm-bar filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size, capital and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lower_breakout` [0.25, 0.5] x `max_drawdown` [0.055, 0.03]: **4 trials**; the band, volatility and settle settings fixed.

## Ambiguities resolved

- Long branch only (direction 1). Long only. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
