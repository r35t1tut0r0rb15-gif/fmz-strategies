# #474868 多指标趋势追踪策略结合布林带和-ATR-动态止损-Multi-Indicator-Trend-Following-Strategy-with-Bollinger-Bands-and-ATR-Dynamic-Stop-Loss -> `fmz_474868_bollinger_breakout_adx_supertrend_volume_macd_exit_reversal`

- FMZ source id: 474868 (lineage).
- Source: https://www.fmz.com/strategy/474868 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-12 16:08:45). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V35). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bollinger breakouts with ADX, supertrend and volume confirmation, MACD / ADX exits |
| 3 | PASS | Exchange pair in the header only (Nifty options named in the title). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`adx_entry` [25.0, 30.0] x `adx_exit` [20.0, 15.0]: **4 trials**; BB 20 x 2, supertrend 3 / 10, DMI 17 / 14, MACD 12 / 26 / 9.

## Ambiguities resolved

- The ATR "trailing stop" tests can never fire. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
