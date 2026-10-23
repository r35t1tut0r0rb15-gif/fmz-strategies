# #429465 双EMA金叉死叉交易策略Dual-EMA-Crossover-Trading-Strategy -> `fmz_429465_ema25_75_cross_reversal`

- FMZ source id: 429465 (lineage).
- Source: https://www.fmz.com/strategy/429465 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-17 13:56:54). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V9). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossover |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [25, 12] x `slow` [75, 50]: **4 trials**.

## Ambiguities resolved

- Volume only colours bars. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_crossover"`.

## Marks

`none`
