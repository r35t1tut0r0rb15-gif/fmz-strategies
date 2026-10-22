# #439111 Dollar Cost Averaging After Downtrend Strategy -> `fmz_439111_downtrend_end_buy_and_hold`

- FMZ source id: 439111 (lineage).
- Source: https://www.fmz.com/strategy/439111 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-17 17:57:58). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C117). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA difference histogram turn |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The cash size, pyramiding and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [50, 20] x `slow` [200, 100]: **4 trials**; signal 20 fixed.

## Ambiguities resolved

- Adds are sizing; held to the end of the data. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
