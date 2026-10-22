# #439620 Multi EMA Bullish Trend Strategy -> `fmz_439620_ema_rainbow_pullback_close_trail_long`

- FMZ source id: 439620 (lineage).
- Source: https://www.fmz.com/strategy/439620 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-22 12:04:05). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C122). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; house percent trail |
| 2 | PASS | EMA stack and crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trail` [0.08, 0.04]: **2 trials**; the EMA stack fixed.

## Ambiguities resolved

- Close ratchet read as the house percent trail on closes. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`coarse_bar_stop, trailing_stop`
