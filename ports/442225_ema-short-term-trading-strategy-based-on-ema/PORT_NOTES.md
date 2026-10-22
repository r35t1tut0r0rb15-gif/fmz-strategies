# #442225 基于EMA均线的短线交易策略Short-term-Trading-Strategy-Based-on-EMA -> `fmz_442225_ema10_20_cross_triple_cross_short_reversal`

- FMZ source id: 442225 (lineage).
- Source: https://www.fmz.com/strategy/442225 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-20 14:06:27). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C152). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The capital and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [10, 5] x `slow` [20, 30]: **4 trials**; EMA 50 / 75 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
