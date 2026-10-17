# #488883 高级动态范围突破趋势追踪策略-Advanced-Dynamic-Range-Breakout-Trend-Following-Strategy -> `fmz_488883_keltner_breakout_trend_atr_bracket`

- FMZ source id: 488883 (lineage).
- Source: https://www.fmz.com/strategy/488883 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-31 15:43:43). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L8). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at the signal bar. |
| 2 | PASS | ATR bands, EMAs, RSI and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mult` [2.0, 1.5] x `sl_atr` [1.5, 3.0]: **4 trials**; defaults 2 / 1.5 (the source's); EMA 20 / ATR 20, EMA 200,
RSI 14 and TP 2 ATR fixed.

## Ambiguities resolved

- Raw entry signals (stop module); the EMA 20 crosses are close-based exits. REVERSAL INTENDED.
- Broker-day bars; FREQ = "1D"; `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`coarse_bar_stop`
