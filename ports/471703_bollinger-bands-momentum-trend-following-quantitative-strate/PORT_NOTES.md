# #471703 Bollinger Bands Momentum Trend Following Quantitative Strategy -> `fmz_471703_rsi7_lower_band_dip_ema500_filter_long`

- FMZ source id: 471703 (lineage).
- Source: https://www.fmz.com/strategy/471703 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-12 15:53:44). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C210). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI band dips in a long-term uptrend |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `mult` [1.8, 2.5] x `ema_len` [500, 200]: **8 trials**; the RSI levels fixed.

## Ambiguities resolved

- Default switches only. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
