# #482242 Trinity Bar Based Trend Breakthrough and Momentum Tracking Strategy -> `fmz_482242_trinity_bar_thirds_sequence_reversal`

- FMZ source id: 482242 (lineage).
- Source: https://www.fmz.com/strategy/482242 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-17 10:53:49). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C243). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bar-thirds continuation sequences |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 200 % of equity and capital stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND482242. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

No parameter reaches the orders: **1 trial**, the source as written.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
