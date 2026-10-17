# #433946 基于ATR和MA组合的超级趋势交易策略Supertrend-Trading-Strategy-Based-on-ATR-and-MA-Combination -> `fmz_433946_supertrend_3_7_flips`

- FMZ source id: 433946 (lineage).
- Source: https://www.fmz.com/strategy/433946 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-01 16:40:27). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C63). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | An ATR trailing line |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The decimal-scaled ATR bracket stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [3.0, 2.0] x `pd` [7, 14]: **4 trials**.

## Ambiguities resolved

- The bracket never gets a level (self-comparison), so only the flips trade, as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
