# #482464 Multi Indicator Trend Momentum Trading Strategy A Comprehensive Quantitative Trading System Based on Bollinger Bands RSI and OBV -> `fmz_482464_bb_basis_rsi_obv_trend_lower_band_exit_1h_long_only`

- FMZ source id: 482464 (lineage).
- Source: https://www.fmz.com/strategy/482464 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-18 15:24:56). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V39). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Basis-side momentum with OBV trend, lower-band exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_len` [20, 40] x `rsi_mid` [50.0, 55.0]: **4 trials**; BB x 2, RSI 14, OBV EMA 10.

## Ambiguities resolved

- Entry is a state. Volume = broker tick volume (OBV). Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_trend"`.

## Marks

`none`
