# #438489 基于PIVOT高低点的加密货币趋势反转策略CRYPTO-TREND-REVERSAL-STRATEGY-BASED-ON-PIVOT-SWING-HIGH-AND-LOW-POINTS -> `fmz_438489_swing_pivot_counter_break_close150_filter_1h_reversal`

- FMZ source id: 438489 (lineage).
- Source: https://www.fmz.com/strategy/438489 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-12 14:13:36). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V21). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Counter-trend breaks of confirmed swing levels with a 150-bar trend filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`pivot_len` [10, 5] x `trend_bars` [150, 75]: **4 trials**; left = right length.

## Ambiguities resolved

- Same-timeframe security(): no look-ahead; strict pivots; closes act only on unchanged positions. Volume not used. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "support_resistance"`.

## Marks

`none`
