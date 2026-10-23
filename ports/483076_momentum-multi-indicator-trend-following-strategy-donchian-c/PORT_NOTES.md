# #483076 Momentum Multi Indicator Trend Following Strategy Donchian Channel with SuperTrend and Volume Filter Entry System -> `fmz_483076_donchian21_breakout_volume_supertrend_exit_long_only`

- FMZ source id: 483076 (lineage).
- Source: https://www.fmz.com/strategy/483076 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-21 11:47:17). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V41). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Donchian breakouts on volume with a supertrend exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 2 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [21, 55] x `st_mult` [2.0, 3.0]: **4 trials**; volume SMA 20, supertrend period 10.

## Ambiguities resolved

- Exit option 3 (supertrend). Volume = broker tick volume. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "channel_breakout"`.

## Marks

`none`
