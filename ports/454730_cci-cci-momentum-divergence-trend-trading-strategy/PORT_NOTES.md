# #454730 CCI动量背离趋势交易策略CCI-Momentum-Divergence-Trend-Trading-Strategy -> `fmz_454730_cci_zero_cross_rsi_extreme_turn_reversal`

- FMZ source id: 454730 (lineage).
- Source: https://www.fmz.com/strategy/454730 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-21 14:07:45). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C195). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | CCI zero crossings after RSI extremes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`cci_len` [10, 20] x `rsi_len` [14, 7]: **4 trials**; the levels 65 / 35 fixed.

## Ambiguities resolved

- Both crosses are either-way crossings. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
