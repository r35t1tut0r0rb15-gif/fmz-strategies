# #482859 Moving Average Based Supply Demand Zone Trading System with Dynamic Risk Management -> `fmz_482859_sma9_21_cross_near_demand_supply_zone_pct_bracket_reversal`

- FMZ source id: 482859 (lineage).
- Source: https://www.fmz.com/strategy/482859 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 15:39:27). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C251). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket from the fill |
| 2 | PASS | SMA crossings near swing-extreme zones |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`zone_lookback` [50, 100] x `take_profit_perc` [2.0, 4.0]: **4 trials**; SMA 9 / 21, zone strength 2, stop 1 %.

## Ambiguities resolved

- The bracket sent with the signal bar's (na or other-side) average price is ported from the fill.
- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
