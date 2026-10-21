# #437800 基于RSI的多头趋势追踪策略RSI-Trend-Tracking-Long-Only-Strategy -> `fmz_437800_rsi_beni_long_entries`

- FMZ source id: 437800 (lineage).
- Source: https://www.fmz.com/strategy/437800 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-05 16:19:57). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C106). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the late-armed bracket not ported (mark) |
| 2 | PASS | RSI level |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the percent bracket quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 7] x `oversold` [25, 30]: **4 trials**.

## Ambiguities resolved

- Bracket armed only by repeated signals: not ported (trailing_stop_pending); no exit. Long only. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`trailing_stop_pending`
