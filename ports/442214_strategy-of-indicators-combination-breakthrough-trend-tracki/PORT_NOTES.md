# #442214 Strategy of Indicators Combination Breakthrough Trend Tracking -> `fmz_442214_wavetrend_mfi_ltf_ema_pullback_atr_bracket`

- FMZ source id: 442214 (lineage).
- Source: https://www.fmz.com/strategy/442214 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-20 11:38:22). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C152). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from signal-bar data (approximation stated) |
| 2 | PASS | WaveTrend, candle MFI and lower-timeframe EMA pullback with an ATR bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size and capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_stop` [5.0, 3.0] x `atr_profit_long` [6.0, 4.0]: **4 trials**; the short target 3, the lengths and levels fixed.

## Ambiguities resolved

- 30-minute EMAs from the day's last 30-minute bar; ATR bracket from the signal bar. Opposite entries cannot occur (entries only from flat). FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`coarse_bar_stop`
