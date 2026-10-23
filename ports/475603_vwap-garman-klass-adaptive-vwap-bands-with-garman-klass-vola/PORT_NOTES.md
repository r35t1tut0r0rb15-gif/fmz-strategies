# #475603 自适应VWAP波段基于Garman-Klass波动率动态跟踪策略-Adaptive-VWAP-Bands-with-Garman-Klass-Volatility-Dynamic-Tracking-Strategy -> `fmz_475603_vwma_gk_volatility_band_breakout_long_only`

- FMZ source id: 475603 (lineage).
- Source: https://www.fmz.com/strategy/475603 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-20 14:51:00). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V36). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Volatility-scaled VWMA band breakouts |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [25, 50] x `vwap_len` [14, 28]: **4 trials**; multiplier 1.

## Ambiguities resolved

- "VWAP" = VWMA 14. Volume = broker tick volume. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_band"`.

## Marks

`none`
