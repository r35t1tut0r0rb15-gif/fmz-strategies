# #440435 Scalping Strategy Based on Market Liquidity and Trend -> `fmz_440435_macd_obv_ema_sar_adx_mfi_tick_bracket_2h_reversal`

- FMZ source id: 440435 (lineage).
- Source: https://www.fmz.com/strategy/440435 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-30 15:36:33). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V24). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; fixed tick bracket from the fill |
| 2 | PASS | Trend-agreement entries timed by ADX and market-facilitation volume |
| 3 | PASS | Exchange pair in the header only; tick distances converted at the source's BTC price. |
| 4 | DONE | Entry qty 1 unit, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`adx_min` [30.0, 25.0] x `obv_len` [55, 21]: **4 trials**; tick bracket 2.381e-4 / 1.786e-4 of the fill.

## Ambiguities resolved

- Ticks converted at the source's BTC price. Volume = broker tick volume (OBV, MFI). REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`coarse_bar_stop`
