# #472974 Dual EMA Momentum Trend Trading Strategy with Full Body Candle Signal System -> `fmz_472974_full_body_candle_beyond_ema9_15_reversal`

- FMZ source id: 472974 (lineage).
- Source: https://www.fmz.com/strategy/472974 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-25 17:30:46). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C212). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Full-body candles beyond two EMAs |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`body_frac` [0.75, 0.6] x `ema_slow` [15, 50]: **4 trials**; the EMA 9 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
