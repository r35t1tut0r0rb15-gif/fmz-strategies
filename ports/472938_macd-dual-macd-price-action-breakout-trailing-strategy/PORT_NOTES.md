# #472938 双重MACD价格行为突破追踪策略-Dual-MACD-Price-Action-Breakout-Trailing-Strategy -> `fmz_472938_strong_candle_breakout_double_macd_15m_colours_reversal`

- FMZ source id: 472938 (lineage).
- Source: https://www.fmz.com/strategy/472938 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-25 11:15:50). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C212). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; 15-minute values from completed 15-minute bars |
| 2 | PASS | Strong-candle breakouts with double-MACD confirmation; armed exits described (pending) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`strong_k` [1.5, 1.0]: **2 trials**; the MACD lengths fixed.

## Ambiguities resolved

- Flags reset every bar (as written); 15-minute MACD colours from the chart bar's last 15 minutes; exits pending (trailing_stop_pending). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks

`trailing_stop_pending`
