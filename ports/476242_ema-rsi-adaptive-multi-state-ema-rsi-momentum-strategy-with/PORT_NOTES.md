# #476242 自适应多状态EMA-RSI动量策略结合波动指数过滤系统-Adaptive-Multi-State-EMA-RSI-Momentum-Strategy-with-Choppiness-Index-Filter-System -> `fmz_476242_choppiness_regime_ema_cross_rsi_extreme_reversal`

- FMZ source id: 476242 (lineage).
- Source: https://www.fmz.com/strategy/476242 (PineScript v6, author ChaoZhang, FMZ last
  modified 2024-12-27 14:05:32). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C230). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; per-bar bracket described (pending) |
| 2 | PASS | Choppiness regimes with EMA crossings or RSI extremes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent bracket inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ci_length` [14, 21] x `fast` [9, 5]: **4 trials**; slow EMA 21, RSI 14, CI levels fixed; the per-bar bracket pending.

## Ambiguities resolved

- CI denominator is log10 of the two-bar range, as written; a non-positive range or log gives no regime.
- Per-bar bracket from the latest close kept pending (trailing_stop_pending). REVERSAL INTENDED. FREQ = "45min".

## FAMILY (proposed, user to confirm)

`FAMILY = "regime_switch"`.

## Marks

`trailing_stop_pending`
