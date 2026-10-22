# #473367 RSI与EMA结合的动态多周期量化交易策略-Dynamic-Multi-Period-Quantitative-Trading-Strategy-Combining-RSI-and-EMA -> `fmz_473367_rsi_extreme_turn_ema400_reversal_bracket_pending`

- FMZ source id: 473367 (lineage).
- Source: https://www.fmz.com/strategy/473367 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-29 15:35:11). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C217). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI turns from extremes with an EMA filter; per-bar bracket described (pending) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent bracket stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_period` [400, 200] x `rsi_period` [14, 7]: **4 trials**; the bracket pending.

## Ambiguities resolved

- Per-bar bracket pending (trailing_stop_pending). REVERSAL INTENDED. FREQ = "2D" (blocks of 2 broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`trailing_stop_pending`
