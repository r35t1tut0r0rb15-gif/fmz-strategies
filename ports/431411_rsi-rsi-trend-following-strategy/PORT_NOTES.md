# #431411 基于RSI的趋势追踪策略RSI-Trend-Following-Strategy -> `fmz_431411_rsi_extreme_exit_stop`

- FMZ source id: 431411 (lineage).
- Source: https://www.fmz.com/strategy/431411 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-11-07 16:33:43). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C45). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry |
| 2 | ADAPT | Tick stop -> ATR fraction |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 7] x `sl_atr` [0.08, 1.5]: **4 trials**; levels 30 / 70 fixed.

## Ambiguities resolved

- Tick stop as an ATR fraction (criterion 2 ADAPT). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
