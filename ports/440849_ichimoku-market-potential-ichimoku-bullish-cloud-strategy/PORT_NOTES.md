# #440849 市场潜力量Ichimoku多头云策略Market-Potential-Ichimoku-Bullish-Cloud-Strategy -> `fmz_440849_ichimoku_cross_above_leads_long`

- FMZ source id: 440849 (lineage).
- Source: https://www.fmz.com/strategy/440849 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-02 16:57:46). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C141). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Ichimoku lines |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`conversion` [9, 20] x `base` [26, 60]: **4 trials**; span B 52 fixed.

## Ambiguities resolved

- Lead lines compared undisplaced, as written. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
