# #429393 基于RSI和移动平均线的多时间框架交易策略RSI-and-Moving-Average-Crossover-Multi-Timeframe-Trading-Strategy -> `fmz_429393_sma9_rsi_wma_cross_bracket`

- FMZ source id: 429393 (lineage).
- Source: https://www.fmz.com/strategy/429393 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-16 16:31:28). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C24). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry. |
| 2 | PASS | Moving-average and RSI crosses, percentages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The commented-out strategy() stored; the bracket quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [3.0, 1.5] x `tp_pct` [15.0, 5.0]: **4 trials**; RSI 9, WMA 21, SMA 9 fixed.

## Ambiguities resolved

- Default signal type only. Long only. Mark coarse_bar_stop. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`coarse_bar_stop`
