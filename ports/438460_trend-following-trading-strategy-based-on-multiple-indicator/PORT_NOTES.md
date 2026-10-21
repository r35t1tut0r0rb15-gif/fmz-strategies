# #438460 Trend Following Trading Strategy Based on Multiple Indicators -> `fmz_438460_rule1_macd_stoch_ema`

- FMZ source id: 438460 (lineage).
- Source: https://www.fmz.com/strategy/438460 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-12 11:25:04). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C110). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD, stochastic and EMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stoch_len` [14, 9] x `ema_signal` [10, 20]: **4 trials**; MACD 8 / 17 / 9 and K / D 5 fixed.

## Ambiguities resolved

- Background levels unused. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
