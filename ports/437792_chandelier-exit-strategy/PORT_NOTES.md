# #437792 Chandelier Exit Strategy -> `fmz_437792_chandelier_exit_long`

- FMZ source id: 437792 (lineage).
- Source: https://www.fmz.com/strategy/437792 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-05 15:57:51). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C106). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ATR stop lines on closes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 25 / close quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mult` [3.0, 2.0] x `length` [22, 14]: **4 trials**; extremes of closes fixed.

## Ambiguities resolved

- Stop lines as close-tested signals; dir starts up. Long only. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks

`none`
