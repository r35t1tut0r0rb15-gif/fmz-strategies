# #438046 基于EMA200的移动止盈移动止损策略EMA-200-Based-Trailing-Take-Profit-and-Trailing-Stop-Loss-Strategy -> `fmz_438046_sma14_28_cross_ema200_side`

- FMZ source id: 438046 (lineage).
- Source: https://www.fmz.com/strategy/438046 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-08 15:50:52). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C108). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings and EMA side; per-bar target described (pending) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The quantity, capital and margins stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND438046. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [14, 7] x `slow` [28, 56]: **4 trials**; EMA 200 fixed; the per-bar target pending.

## Ambiguities resolved

- Per-bar trailing take-profit kept pending (trailing_stop_pending). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
