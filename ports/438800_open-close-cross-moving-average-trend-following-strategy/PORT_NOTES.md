# #438800 Open Close Cross Moving Average Trend Following Strategy -> `fmz_438800_occ_dema_2h_cross_trail`

- FMZ source id: 438800 (lineage).
- Source: https://www.fmz.com/strategy/438800 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-15 14:24:27). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C113). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; house trail |
| 2 | ADAPT | Tick trail -> ATR multiple and fraction |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The trail inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k_trail` [0.04, 1.0] x `activate` [0.0007, 0.01]: **4 trials**; DEMA 14 on 2-hour bars fixed.

## Ambiguities resolved

- Lower-timeframe DEMAs = the day's last 2-hour bar; tick trail as the house volatility trail. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop, trailing_stop`
