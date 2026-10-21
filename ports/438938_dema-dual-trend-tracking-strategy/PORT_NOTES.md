# #438938 超级趋势指标DEMA双重趋势追踪策略Dual-Trend-Tracking-Strategy -> `fmz_438938_atr_trend_change_atr12`

- FMZ source id: 438938 (lineage).
- Source: https://www.fmz.com/strategy/438938 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-16 15:03:55). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C114). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ATR trend line changes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG438938. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`periods` [12, 20] x `multiplier` [3.0, 2.0]: **4 trials**; source hl2 fixed.

## Ambiguities resolved

- Level-free exits place nothing. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
