# #430988 基于SuperTrend和Fisher变换的趋势跟随长线策略Trend-Following-Long-Term-Strategy-Based-on-SuperTrend-and-Fisher-Transform -> `fmz_430988_supertrend_fisher_long`

- FMZ source id: 430988 (lineage).
- Source: https://www.fmz.com/strategy/430988 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-03 15:42:16). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C42). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-checked exits |
| 2 | PASS | Fisher transform, SuperTrend and ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The risk-amount contract formula stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND430988. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mult` [2.0, 3.0] x `fisher_level` [-2.5, -1.5]: **4 trials**; Fisher 10 and ATR 10 fixed.

## Ambiguities resolved

- Fisher condition on the turn bar itself; close-checked exits. Long only. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
