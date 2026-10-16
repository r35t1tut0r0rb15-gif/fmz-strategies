# #429497 Dual Moving Average Monitoring Model -> `fmz_429497_ema_macd_trail_long`

- FMZ source id: 429497 (lineage).
- Source: https://www.fmz.com/strategy/429497 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-10-17 16:33:29). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C26). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the trail is a house trail (approximation stated). |
| 2 | PASS | Moving-average and MACD conditions, a percentage trail. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The commented-out strategy() stored; the trail quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trail_pct` [3.0, 1.5] x `slow` [26, 50]: **4 trials**; EMA 8 and MACD 12 / 26 / 9 fixed.

## Ambiguities resolved

- House percent trail on closes (approximation stated). Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`trailing_stop`
