# #474815 动态RSI智能择时波段交易策略-Dynamic-RSI-Smart-Timing-Swing-Trading-Strategy -> `fmz_474815_rsi14_cross_up30_down70_long`

- FMZ source id: 474815 (lineage).
- Source: https://www.fmz.com/strategy/474815 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-12 11:32:55). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C224). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI level re-crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Percent-of-equity size, commission and slippage stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [14, 7]: **2 trials**; levels 30 / 70.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
