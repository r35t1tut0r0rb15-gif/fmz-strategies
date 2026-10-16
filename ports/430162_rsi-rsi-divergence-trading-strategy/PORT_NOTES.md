# #430162 RSI指标背离交易策略RSI-Divergence-Trading-Strategy -> `fmz_430162_rsi_regression_divergence`

- FMZ source id: 430162 (lineage).
- Source: https://www.fmz.com/strategy/430162 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-10-25 16:47:14). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C33). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket and trail fixed at entry. |
| 2 | ADAPT | The tick-based trail offset -> 2.5 % of the price. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the exits quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 28] x `trail_pct` [0.025, 0.05]: **4 trials**; RSI 14, TP 25 %, stop 5 % fixed.

## Ambiguities resolved

- Trail offset in ticks -> 2.5 % (BTC_USDT 0.1 tick); activation at the signal close treated as immediate.
- REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_divergence"`.

## Marks

`trailing_stop, coarse_bar_stop`
