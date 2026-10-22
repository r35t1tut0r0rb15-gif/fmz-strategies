# #472252 Dynamic Darvas Box Breakout with Moving Average Trend Confirmation Trading System -> `fmz_472252_darvas_box_breakout_sma25_long`

- FMZ source id: 472252 (lineage).
- Source: https://www.fmz.com/strategy/472252 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-18 16:02:45). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C212). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Darvas box breakouts with an SMA filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`boxp` [5, 8] x `ma_len` [25, 50]: **4 trials**.

## Ambiguities resolved

- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`none`
