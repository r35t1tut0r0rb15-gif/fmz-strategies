# #484919 Double Bollinger Bands Extreme Reversal Trading Strategy -> `fmz_484919_double_bb20_3sd_reentry_2sd_exit_reversal`

- FMZ source id: 484919 (lineage).
- Source: https://www.fmz.com/strategy/484919 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-05 10:10:08). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C262). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Double Bollinger band re-entries and exits |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 40] x `bb2_mult` [3.0, 2.5]: **4 trials**; inner band 2 sd.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
