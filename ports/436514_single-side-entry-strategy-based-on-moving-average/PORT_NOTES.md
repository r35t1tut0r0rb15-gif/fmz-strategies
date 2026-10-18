# #436514 Single Side Entry Strategy Based on Moving Average -> `fmz_436514_noro_ma_side_flips`

- FMZ source id: 436514 (lineage).
- Source: https://www.fmz.com/strategy/436514 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-25 14:09:49). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C90). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average side flips |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND427090. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_type` [1, 2, 4, 5, 6, 7] x `len` [30, 50]: **12 trials** (type 3 reads volume and is left out).

## Ambiguities resolved

- Type 3 (vwma) not ported (volume). KAMA from 0 as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_filter"`.

## Marks

`none`
