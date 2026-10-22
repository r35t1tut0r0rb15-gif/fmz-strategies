# #439643 反转向量RSI趋势跟踪ETF交易策略Reversal-RSI-Trend-Tracking-ETF-Trading-Strategy -> `fmz_439643_r3_rsi2_three_bar_decline_long`

- FMZ source id: 439643 (lineage).
- Source: https://www.fmz.com/strategy/439643 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-22 17:15:18). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C122). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI sequences and an EMA filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [2, 3] x `exit_rsi` [70, 60]: **4 trials**; levels 10 / 60 and EMA 200 fixed.

## Ambiguities resolved

- Long only. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
