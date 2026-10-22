# #478706 Triple EMA Trend Following Multi Indicator Quantitative Trading Strategy -> `fmz_478706_ema10_25_cross_ema50_diplus_rsi_dpo_atr_bracket_reversal`

- FMZ source id: 478706 (lineage).
- Source: https://www.fmz.com/strategy/478706 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-17 14:57:26). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C239). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar ATR bracket as fractions of the fill |
| 2 | PASS | EMA crossings with DI+, RSI and DPO filters and an ATR bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity and risk 2 % stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [1.5, 2.5] x `tp_mult` [2.0, 4.0]: **4 trials**; EMA 10 / 25 / 50, DMI 14, DPO 14, RSI 14.

## Ambiguities resolved

- The "ADX" filter is DI+ (misnamed outputs), as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
