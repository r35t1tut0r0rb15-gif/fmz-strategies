# #438466 Daily Moving Average Tracking Strategy for Gold Value -> `fmz_438466_daily_candle_ema_hours_trail`

- FMZ source id: 438466 (lineage).
- Source: https://www.fmz.com/strategy/438466 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-12 11:54:21). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C110). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; house percent trail |
| 2 | ADAPT | Price-unit trail -> fractions of the close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The trail inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trail_pct` [0.00023, 0.002] x `activate` [0.0023, 0.01]: **4 trials**; hours 11-16 and EMA 50 / 200 fixed.

## Ambiguities resolved

- Daily values two broker days back; price-unit trail -> fractions. REVERSAL INTENDED. FREQ = "45min".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_confluence"`.

## Marks

`trailing_stop`
