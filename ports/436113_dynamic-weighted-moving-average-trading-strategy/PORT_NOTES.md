# #436113 Dynamic Weighted Moving Average Trading Strategy -> `fmz_436113_sma_cross_ema_filter`

- FMZ source id: 436113 (lineage).
- Source: https://www.fmz.com/strategy/436113 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-21 12:19:43). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C86). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average cross and a trend filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [5, 3] x `ema_len` [30, 50]: **4 trials**; SMA 10 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
