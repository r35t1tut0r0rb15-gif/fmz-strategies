# #437034 基于QQE和MA的趋势跟踪策略Trend-Following-Strategy-Based-on-QQE-and-MA -> `fmz_437034_qqe_channel_exit_ma_direction`

- FMZ source id: 437034 (lineage).
- Source: https://www.fmz.com/strategy/437034 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-29 16:36:47). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C100). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI-based QQE and average directions |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG437034, ND431270. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [14, 21] x `threshold` [10, 5]: **4 trials**; EMA 16 / 21 / 26, anchor 4, smoothing 8, factor 5 and the XC / XQ signal choice fixed.

## Ambiguities resolved

- Signals one bar late as written; XQ close on the first bar of a run; entries from flat; start window dropped; VWMA type left out. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
