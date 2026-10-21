# #436786 RSI与EMA通道日内交易策略RSI-and-EMA-Channel-Intraday-Trading-Strategy -> `fmz_436786_rsi_ema_channel_range_target`

- FMZ source id: 436786 (lineage).
- Source: https://www.fmz.com/strategy/436786 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-27 16:57:09). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C96). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; target fixed at entry |
| 2 | PASS | Range-based target |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [6, 9] x `ema_len` [5, 10]: **4 trials**; levels 70 / 30 and the 1x target fixed.

## Ambiguities resolved

- TP2 unreachable (TP1 closes the full position); one target as a distance; re-placing not ported. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
