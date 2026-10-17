# #434705 SuperTrend Engulfing Strategy -> `fmz_434705_supertrend_engulfing_bracket`

- FMZ source id: 434705 (lineage).
- Source: https://www.fmz.com/strategy/434705 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-08 15:40:26). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C70). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (re-issued levels approximated) |
| 2 | ADAPT | Tick padding -> ATR multiple |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mult` [3.0, 2.0] x `pad_atr` [0.1, 0.5]: **4 trials**; ATR 10 and the 25 / 50 % body thresholds fixed.

## Ambiguities resolved

- Signal-bar levels re-based on the fill; re-issued levels not ported (trailing_stop_pending). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`trailing_stop_pending`
