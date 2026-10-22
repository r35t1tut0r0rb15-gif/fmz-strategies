# #439981 MT Coordination Trading Strategy -> `fmz_439981_sma_stack_rsi50_close_break`

- FMZ source id: 439981 (lineage).
- Source: https://www.fmz.com/strategy/439981 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-25 15:06:04). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C128). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA sides, RSI and close-channel breaks |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The leverage and portfolio share stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma200_length` [200, 100] x `williams_length` [2, 5]: **4 trials**; SMA 21 / 50 and RSI 14 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_filter"`.

## Marks

`none`
