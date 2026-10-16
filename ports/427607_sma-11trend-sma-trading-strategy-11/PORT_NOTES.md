# #427607 Trend SMA Trading Strategy 1.1 -> `fmz_427607_noro_trend_ema_pullback`

- FMZ source id: 427607 (lineage).
- Source: https://www.fmz.com/strategy/427607 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-22 16:40:33). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C10). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | EMA lengths only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Equity quantity and the only-long quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fastlen` [5, 10] x `slowlen` [15, 30]: **4 trials**; defaults 5 / 15 (the source's).

## Ambiguities resolved

- The "SMA"s are EMAs as written. "Only long?" sets the short quantity to 0: sizing; default (false) ported.
- trend[1] is na before the first defining bar. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_pullback"`.

## Marks

`none`
