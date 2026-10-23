# #491511 多指标融合自动化交易系统SuperTrend-ATR-RSI动态风控策略-Multi-Indicator-Fusion-Automated-Trading-System-SuperTrend-ATR-RSI-Dynamic-Risk-Control-Strategy -> `fmz_491511_one_step_supertrend_volume_body_rsi_atr_bracket_reversal`

- FMZ source id: 491511 (lineage).
- Source: https://www.fmz.com/strategy/491511 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-21 16:15:37). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V48). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket at the signal close as fractions of the fill |
| 2 | PASS | Band-state trend entries on volume and body strength |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Cash 1000 per order and qty = 10 / close stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [3.0, 2.0] x `rr` [2.0, 3.0]: **4 trials**; ATR 10, RSI 14 70 / 30, volume x 1.2, body 0.3 ATR, stop 1 ATR.

## Ambiguities resolved

- One-step band ratchet as written; repeats re-send the bracket (pending). Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
