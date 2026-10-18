# #435249 Multi Timeframe Moving Average Strategy -> `fmz_435249_six_average_alignment_bracket`

- FMZ source id: 435249 (lineage).
- Source: https://www.fmz.com/strategy/435249 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-13 15:34:09). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C76). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Tick bracket -> ATR multiple |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the tick bracket quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k_atr` [0.04, 1.0] x `len3` [21, 34]: **4 trials**; SMA 5 / 13 and EMA 75 / 90 / 200 fixed; the target is 2 x the stop.

## Ambiguities resolved

- Tick bracket -> ATR multiple. State entries re-fire after each exit. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
