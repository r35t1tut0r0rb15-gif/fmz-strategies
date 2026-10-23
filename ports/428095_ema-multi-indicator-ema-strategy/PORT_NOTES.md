# #428095 多重指标EMA策略Multi-Indicator-EMA-Strategy -> `fmz_428095_six_indicator_score_7_3_reversal`

- FMZ source id: 428095 (lineage).
- Source: https://www.fmz.com/strategy/428095 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-28 15:57:34). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V8). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Multi-indicator score thresholds |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The commented strategy() (25 % of equity, capital 1000) stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`emalen` [80, 50] x `entry_score` [7, 9]: **4 trials**; exit 3, the other settings as written.

## Ambiguities resolved

- RSI zone scores as written. OBV unused. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
