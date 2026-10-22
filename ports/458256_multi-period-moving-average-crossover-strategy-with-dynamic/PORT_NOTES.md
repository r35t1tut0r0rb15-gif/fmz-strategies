# #458256 Multi Period Moving Average Crossover Strategy with Dynamic Volatility Filter -> `fmz_458256_sma10_200_cross_atr_filter_sma200_stop_reversal`

- FMZ source id: 458256 (lineage).
- Source: https://www.fmz.com/strategy/458256 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-31 12:03:54). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C205). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar levels as fractions of the fill |
| 2 | PASS | SMA crossings with a volatility filter and an SMA-anchored stop |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_len` [10, 20] x `tp_frac` [0.000179, 0.01]: **4 trials**; the SMA 200 and the ATR filter fixed.

## Ambiguities resolved

- Points as a fraction of 42000; a marketable stop is closed one bar late. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
