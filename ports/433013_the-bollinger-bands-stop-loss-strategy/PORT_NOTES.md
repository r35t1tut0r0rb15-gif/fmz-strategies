# #433013 The Bollinger Bands Stop Loss Strategy -> `fmz_433013_bb_alternating_close_stop`

- FMZ source id: 433013 (lineage).
- Source: https://www.fmz.com/strategy/433013 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-23 15:49:12). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C57). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-checked stop |
| 2 | PASS | Band crosses and a percent stop |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The commission setting stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 40] x `sl_pct` [1.0, 2.0]: **4 trials**; mult 2 fixed.

## Ambiguities resolved

- Stop levels refreshed only on reversals (as written); close-checked stop. REVERSAL INTENDED. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
