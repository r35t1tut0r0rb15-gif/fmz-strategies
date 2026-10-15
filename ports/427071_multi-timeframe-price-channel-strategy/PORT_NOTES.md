# #427071 Multi-Timeframe Price Channel Strategy -> `fmz_427071_open_channel_cross`

- FMZ source id: 427071 (lineage).
- Source: https://www.fmz.com/strategy/427071 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-17 18:39:41). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C1). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; `security(..., '15', open)` on a 15-minute chart is the chart's own open. |
| 2 | PASS | Bar counts only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`channel` [60, 30] x `fast` [30, 20] x `slow` [60, 90]: **8 trials**; defaults 60 / 30 / 60 (the source's); EMA smoothing 60 fixed.

## Ambiguities resolved

- "Multi-timeframe" in the name: the only `security` call reads the chart's own 15-minute period.
- highest / lowest include the current bar; always in the market after the first signal (REVERSAL INTENDED).
- FREQ = "15min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`
