# #482602 Multi Indicator Trend Following Enhanced Quantitative Trading Strategy -> `fmz_482602_ema50_200_cross_adx25_rsi_pct_bracket_rsi_exit_reversal`

- FMZ source id: 482602 (lineage).
- Source: https://www.fmz.com/strategy/482602 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-19 11:30:19). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C247). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket from the signal close as fractions of the fill |
| 2 | PASS | EMA crossings with ADX and RSI filters and RSI exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 200 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`adx_threshold` [25, 20] x `rsi_overbought` [70, 80]: **4 trials**; EMA 50 / 200, DMI 14, oversold 30, TP 5 %, SL 2 %.

## Ambiguities resolved

- A repeat crossing's re-sent bracket is pending and its bar's RSI close is dropped.
- REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
