# #489156 Bollinger Bands with Dual SMA Momentum Enhanced Quantitative Trading Strategy -> `fmz_489156_bb21_2_upper_breakout_sma6_45_trend_long`

- FMZ source id: 489156 (lineage).
- Source: https://www.fmz.com/strategy/489156 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-02 11:28:15). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C269). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bollinger breakouts with an SMA trend filter |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 100 % of equity, commission and slippage stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [21, 50] x `slowSmaLength` [45, 100]: **4 trials**; SMA 6, BB 2.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
