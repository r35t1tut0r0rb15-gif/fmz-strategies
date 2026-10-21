# #439051 基于MA转折点的长短策略MA-Turning-Point-Long-and-Short-Strategy -> `fmz_439051_sma25_turning_point`

- FMZ source id: 439051 (lineage).
- Source: https://www.fmz.com/strategy/439051 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-17 11:56:53). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C115). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MA rate-of-change turns |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND430020. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma1` [25, 50] x `trend_strength` [2.5, 10.0]: **4 trials**; lookback 1 fixed; SMA.

## Ambiguities resolved

- Threshold 0.025 % as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
