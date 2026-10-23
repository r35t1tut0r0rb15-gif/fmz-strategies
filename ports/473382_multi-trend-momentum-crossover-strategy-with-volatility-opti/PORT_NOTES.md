# #473382 Multi Trend Momentum Crossover Strategy with Volatility Optimization System -> `fmz_473382_ema_macd_rsi_volume_state_short_tick_bracket_reversal`

- FMZ source id: 473382 (lineage).
- Source: https://www.fmz.com/strategy/473382 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-29 16:07:17). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V34). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; fixed tick bracket from the fill (short only) |
| 2 | PASS | EMA / MACD / RSI trend agreement on above-average volume |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp` [4.167e-04, 8.333e-04] x `sl` [2.083e-04, 4.167e-04]: **4 trials**; EMA 9 / 21, MACD 12 / 26 / 9, RSI 14, volume SMA 14.

## Ambiguities resolved

- Shared exit id: short-only bracket; ticks converted at the source's BTC price. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_agreement"`.

## Marks

`coarse_bar_stop`
