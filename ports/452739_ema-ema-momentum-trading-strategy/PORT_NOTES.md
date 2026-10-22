# #452739 EMA动量交易策略-EMA-Momentum-Trading-Strategy -> `fmz_452739_ema10_21_cross_one_bar_delay_reversal`

- FMZ source id: 452739 (lineage).
- Source: https://www.fmz.com/strategy/452739 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-28 17:28:30). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C189). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Delayed EMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [10, 5] x `slow` [21, 50]: **4 trials**.

## Ambiguities resolved

- One-bar delay as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
