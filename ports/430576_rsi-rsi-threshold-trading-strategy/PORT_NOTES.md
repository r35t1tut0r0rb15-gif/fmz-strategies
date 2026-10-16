# #430576 基于RSI的阈值交易策略RSI-Threshold-Trading-Strategy -> `fmz_430576_rsi10_dip_time_exit_long`

- FMZ source id: 430576 (lineage).
- Source: https://www.fmz.com/strategy/430576 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-30 14:58:38). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C36). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the time exit as a signal. |
| 2 | PASS | RSI levels. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The commented-out cash order size stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`oversold` [30, 20] x `exit_bars` [10, 5]: **4 trials**; RSI 10 and overbought 40 fixed.

## Ambiguities resolved

- The hour filter is vacuous on daily bars: not ported. Time exit as a signal. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
