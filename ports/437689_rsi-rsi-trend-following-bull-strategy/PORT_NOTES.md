# #437689 RSI趋势追踪型多头策略RSI-Trend-Following-Bull-Strategy -> `fmz_437689_rsi_dip_buy_emergency_exit_long`

- FMZ source id: 437689 (lineage).
- Source: https://www.fmz.com/strategy/437689 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-04 17:48:41). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C104). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI levels, SMA side, MACD crossing |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_long` [21.0, 30.0] x `ema_length` [200, 100]: **4 trials**; close 86, emergency 73 and MACD 12 / 26 / 9 fixed.

## Ambiguities resolved

- SMA as coded; long needs the close under it, as written. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
