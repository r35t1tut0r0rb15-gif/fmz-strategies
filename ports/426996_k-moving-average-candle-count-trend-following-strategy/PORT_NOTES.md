# #426996 K Moving Average Candle Count Trend Following Strategy -> `fmz_426996_candle_meter`

- Source: https://www.fmz.com/strategy/426996 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-16 19:04:02). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A29). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | Price distances -> ATR(14) multiples at the signal bar. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bar_counter` [3, 5] x `sl_atr` [0.25, 0.5, 1.0]: **6 trials**, target 2 x the stop (the source's 60 / 30); default 0.25 is the smallest step (30 USD is a small fraction of a 4h ATR).

## Ambiguities resolved

- Criterion 2 (ADAPT): 60 / 30 price units -> ATR(14) multiples at the signal bar.
- Entries do not depend on the position: no mirroring.
- Stops on 4h bars: coarse_bar_stop.

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks (2026-10-07)

`coarse_bar_stop`
