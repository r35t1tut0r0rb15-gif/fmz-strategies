# #442979 Bollinger Bands Breakout Trend Trading Strategy -> `fmz_442979_band_outside_bar_extreme_break_reversal`

- FMZ source id: 442979 (lineage).
- Source: https://www.fmz.com/strategy/442979 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-27 18:00:39). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C164). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the re-sent bracket pending |
| 2 | PASS | Breaks of band-outside bar extremes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG442979. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `mult` [1.5, 2.0]: **4 trials**; the bracket settings fixed (pending).

## Ambiguities resolved

- Kept reference levels; re-sent bracket pending; Sell wins a tie. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`trailing_stop_pending`
