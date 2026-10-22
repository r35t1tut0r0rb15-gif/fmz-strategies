# #442116 基于RSI布林带和支撑阻力策略Rational-Trading-Robot-Powered-by-RSI-Strategy -> `fmz_442116_bb_touch_level_reversal`

- FMZ source id: 442116 (lineage).
- Source: https://www.fmz.com/strategy/442116 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-19 14:43:34). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C151). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bollinger touches |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_length` [20, 50] x `bb_mult` [2.0, 2.5]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
