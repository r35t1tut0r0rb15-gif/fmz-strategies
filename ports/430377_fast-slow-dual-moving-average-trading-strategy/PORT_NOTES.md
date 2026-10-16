# #430377 Fast Slow Dual Moving Average Trading Strategy -> `fmz_430377_sma3_9_cross_long`

- FMZ source id: 430377 (lineage).
- Source: https://www.fmz.com/strategy/430377 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-27 16:41:24). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C35). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Moving averages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity per entry stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND429389. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [3, 5] x `slow` [9, 20]: **4 trials**.

## Ambiguities resolved

- Default direction (long only). FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
