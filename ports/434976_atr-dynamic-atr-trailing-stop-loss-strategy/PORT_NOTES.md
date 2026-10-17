# #434976 动态ATR追踪止损策略Dynamic-ATR-Trailing-Stop-Loss-Strategy -> `fmz_434976_dual_atr_trail_cross_long`

- FMZ source id: 434976 (lineage).
- Source: https://www.fmz.com/strategy/434976 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-11 14:24:18). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C72). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ATR trailing lines |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG434976. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_mult` [0.5, 1.0] x `slow_mult` [3.0, 2.0]: **4 trials**; ATR 5 / 10 fixed.

## Ambiguities resolved

- Trailing lines as close-based signals. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks

`none`
