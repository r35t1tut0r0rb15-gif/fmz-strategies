# #477550 RSI趋势突破与动量增强交易策略-RSI-Trend-Breakthrough-and-Momentum-Enhancement-Trading-Strategy -> `fmz_477550_rising_rsi13_higher_highs_sma55_exit_long`

- FMZ source id: 477550 (lineage).
- Source: https://www.fmz.com/strategy/477550 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-06 13:43:48). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C233). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Rising RSI with higher highs; SMA 55 exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity qty stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_length` [13, 21] x `exit_ma` [55, 21]: **4 trials**; RSI average 13.

## Ambiguities resolved

- The sell condition reduces to the SMA 55 cross-down. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
