# #430543 Dual Balanced Bulls and Bears Strategy -> `fmz_430543_combo_123_bull_bear_balance`

- FMZ source id: 430543 (lineage).
- Source: https://www.fmz.com/strategy/430543 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-30 10:32:53). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C35). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | The price-unit balance levels -> ATR fractions. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND430543. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`zone_atr` [0.1, 0.5]: **2 trials**; the 123 settings and ATR 14 fixed.

## Ambiguities resolved

- Levels +-15 (price units) -> +-zone_atr x ATR(14). Disagreement closes all. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
