# #474810 Bollinger Breakout with Mean Reversion 4H Quantitative Trading Strategy -> `fmz_474810_bb20_breakout_candle_bar_extreme_stop_from_flat`

- FMZ source id: 474810 (lineage).
- Source: https://www.fmz.com/strategy/474810 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-12 11:24:28). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C224). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the signal bar's extreme as the stop |
| 2 | PASS | Band breakout candles with candle-colour exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Leveraged equity size and commission stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `mult` [2.0, 2.5]: **4 trials**.

## Ambiguities resolved

- Entries only from flat. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`coarse_bar_stop`
