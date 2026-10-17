# #432979 Momentum Turtle Trend Tracking Strategy -> `fmz_432979_daily_ha_roc_filter`

- FMZ source id: 432979 (lineage).
- Source: https://www.fmz.com/strategy/432979 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-23 11:53:27). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C56). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; daily values from completed broker days; fixed-percent stop |
| 2 | PASS | Candle colour and a percent rate of change |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 100 % of equity and the commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND430880. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`roc_len` [30, 60] x `sl_pct` [0.02, 0.04]: **4 trials**; pcntChange 7 fixed, the EMA length is roc_len / 2.

## Ambiguities resolved

- Daily HA from completed broker days; level entries re-enter after a stop; unreachable target dropped. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "heikin_ashi_trend"`.

## Marks

`none`
