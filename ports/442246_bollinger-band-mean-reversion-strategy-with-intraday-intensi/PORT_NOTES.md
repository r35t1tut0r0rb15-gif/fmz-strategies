# #442246 Bollinger Band Mean Reversion Strategy with Intraday Intensity Index -> `fmz_442246_bollinger_reentry_iii_time_profit_exit_2h_reversal`

- FMZ source id: 442246 (lineage).
- Source: https://www.fmz.com/strategy/442246 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-20 15:07:59). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V27). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bollinger re-entries confirmed by the intraday intensity index, time and profit exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_length` [20, 50] x `time_stop` [10, 20]: **4 trials**; BB x 2, III 21.

## Ambiguities resolved

- openprofit sign only; closes act only on unchanged positions. Volume = broker tick volume (III). REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
