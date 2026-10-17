# #434466 动态K线大阳线交易策略Dynamic-Candlestick-Big-Yang-Line-Trading-Strategy -> `fmz_434466_big_body_bar_reversal`

- FMZ source id: 434466 (lineage).
- Source: https://www.fmz.com/strategy/434466 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-06 16:22:08). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C67). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the late-armed bracket not ported (mark) |
| 2 | PASS | Body / range ratios |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the tick bracket quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bull_th` [26, 20] x `bear_th` [30, 24]: **4 trials**.

## Ambiguities resolved

- Bracket armed only by repeated signals inside a trade: not ported (trailing_stop_pending). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`trailing_stop_pending`
