# #427162 Dual-Rail Trend Tracking Strategy -> `fmz_427162_bb_rebound_long`

- FMZ source id: 427162 (lineage).
- Source: https://www.fmz.com/strategy/427162 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-18 17:31:43). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C2). Not run.
- Near-duplicate group: **ND427162** (with #429561, Jaccard 0.683); ported anyway (rule 7).

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Band in standard deviations. |
| 3 | PASS | Spot pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND427162. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 14, 30] x `mult` [2.0, 2.5]: **6 trials**; defaults 20 / 2.0 (the source's).

## Ambiguities resolved

- Long only, entries from flat; population stdev.
- FREQ = "3h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
