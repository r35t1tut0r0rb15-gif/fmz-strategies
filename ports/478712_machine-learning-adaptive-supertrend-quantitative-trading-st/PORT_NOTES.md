# #478712 Machine Learning Adaptive SuperTrend Quantitative Trading Strategy -> `fmz_478712_supertrend_flip_atr_regime_atr_bracket_reversal`

- FMZ source id: 478712 (lineage).
- Source: https://www.fmz.com/strategy/478712 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-17 15:11:40). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C239). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar ATR bracket as fractions of the fill |
| 2 | PASS | SuperTrend flips in ATR regimes with an ATR bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 200 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [3.0, 2.0] x `training` [100, 300]: **4 trials**; ATR 10, SL 2 ATR, TP 1.5 x SL.

## Ambiguities resolved

- Repeat-signal re-sends not followed. REVERSAL INTENDED. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`trailing_stop_pending`
