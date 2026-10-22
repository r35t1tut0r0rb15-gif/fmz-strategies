# #453238 EMA与RSI交叉策略-EMA-RSI-Crossover-Strategy -> `fmz_453238_rsi7_extreme_vs_ema50_atr_body_bracket`

- FMZ source id: 453238 (lineage).
- Source: https://www.fmz.com/strategy/453238 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-03 11:08:30). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C191). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the signal-bar levels as fractions; re-issued levels pending (mark) |
| 2 | PASS | RSI extremes against the EMA with ATR / body brackets |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The margin settings stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [7, 14] x `ema_len` [50, 100] x `tp_mult` [1.2, 2.0]: **8 trials**; the levels 20 / 80 fixed.

## Ambiguities resolved

- Shorts only from flat; re-issued levels pending. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
