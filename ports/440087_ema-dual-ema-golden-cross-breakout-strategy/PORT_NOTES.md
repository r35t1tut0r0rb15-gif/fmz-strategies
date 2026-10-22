# #440087 双EMA黄金交叉突破策略Dual-EMA-Golden-Cross-Breakout-Strategy -> `fmz_440087_ema26_200_cross_reclaim_target`

- FMZ source id: 440087 (lineage).
- Source: https://www.fmz.com/strategy/440087 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-26 15:13:59). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C130). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings and a percent target |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The fixed quantity and percent inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`take_profit` [0.02, 0.05] x `ema1` [26, 50]: **4 trials**; EMA 200 fixed.

## Ambiguities resolved

- Close-tested target. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
