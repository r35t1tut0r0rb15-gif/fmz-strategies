# #439609 基于EVWMA的MACD交易策略EVWMA-based-MACD-Trading-Strategy -> `fmz_439609_evwma10_20_cross_reversal`

- FMZ source id: 439609 (lineage).
- Source: https://www.fmz.com/strategy/439609 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-22 10:50:25). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V23). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Crossings of fast and slow elastic volume-weighted averages |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [10, 5] x `slow` [20, 40]: **4 trials**.

## Ambiguities resolved

- EVWMA seeded with the close. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_weighted_ma"`.

## Marks

`none`
