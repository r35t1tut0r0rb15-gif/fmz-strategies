# #434984 Ichimoku Trend Following Strategy -> `fmz_434984_ichimoku_counters_long`

- FMZ source id: 434984 (lineage).
- Source: https://www.fmz.com/strategy/434984 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-11 15:00:29). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C72). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Ichimoku lines and counters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 100 % of equity and capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND434984. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`kijun_lag` [6, 3] x `count_max` [8, 4]: **4 trials**; the 26 / 9 / 52 SMAs fixed.

## Ambiguities resolved

- Counters as written; date window dropped. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
