# #438769 Multi timeframe Super Trend Tracking Strategy -> `fmz_438769_atr_trend_change_long`

- FMZ source id: 438769 (lineage).
- Source: https://www.fmz.com/strategy/438769 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-15 11:35:47). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C112). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ATR trend line changes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG438769. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`periods` [10, 20] x `multiplier` [3.0, 2.0]: **4 trials**; source hl2 fixed.

## Ambiguities resolved

- Date window always true. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
