# #433958 Oscillation Positioning Breakthrough Strategy with Multiple Indicators -> `fmz_433958_price_stoch_vs_stochrsi_d_rsi_cross_10m_reversal`

- FMZ source id: 433958 (lineage).
- Source: https://www.fmz.com/strategy/433958 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-01 17:49:34). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V15). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Stochastic and RSI oversold / overbought crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length_stoch` [14, 21] x `smooth_k` [3, 5]: **4 trials**; RSI 14, 80 / 20, 70 / 30.

## Ambiguities resolved

- ds = SMA of the stochastic-RSI K, as written. Volume not used (MFI is plot-only). REVERSAL INTENDED. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_rsi"`.

## Marks

`none`
