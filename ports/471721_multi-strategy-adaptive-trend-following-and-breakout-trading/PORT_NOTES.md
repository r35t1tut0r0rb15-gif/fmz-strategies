# #471721 Multi Strategy Adaptive Trend Following and Breakout Trading System -> `fmz_471721_trend_range_breakout_volume_late_atr_bracket_reversal`

- FMZ source id: 471721 (lineage).
- Source: https://www.fmz.com/strategy/471721 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-12 16:43:34). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V33). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; late-armed ATR bracket followed in the signals |
| 2 | PASS | Trend dips, range reversals and volume breakouts |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code (capital-risk input unused). |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_mult` [1.2, 2.0] x `rr` [3.0, 2.0]: **4 trials**; EMA 50, RSI 14 35 / 65, ADX 25, 20-day windows.

## Ambiguities resolved

- Brackets armed only by repeated signals, followed at the next open. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_setup"`.

## Marks

`trailing_stop_pending`
