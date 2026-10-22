# #442365 Extreme Reversal Setup Strategy -> `fmz_442365_outsized_candle_reversal`

- FMZ source id: 442365 (lineage).
- Source: https://www.fmz.com/strategy/442365 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-21 14:08:09). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C154). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Outsized-candle reversal |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bars_back` [20, 50] x `body_mult` [2.0, 3.0]: **4 trials**; body share 0.75 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`none`
