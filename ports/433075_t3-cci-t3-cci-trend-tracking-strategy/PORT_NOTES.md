# #433075 基于T3和CCI指标的趋势追踪策略T3-CCI-Trend-Tracking-Strategy -> `fmz_433075_t3_cci_state`

- FMZ source id: 433075 (lineage).
- Source: https://www.fmz.com/strategy/433075 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-11-24 10:33:31). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C58). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | A bounded-scale oscillator sign |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`cci_len` [14, 28] x `t3_len` [5, 10]: **4 trials**; b 0.618 fixed.

## Ambiguities resolved

- T3 stages seeded with 0 as written. REVERSAL INTENDED. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
