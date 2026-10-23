# #481117 Multi Indicator Trend Divergence Quantitative Trading Strategy -> `fmz_481117_latched_bb_rsi3_stoch_mfi_trend_long_only`

- FMZ source id: 481117 (lineage).
- Source: https://www.fmz.com/strategy/481117 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-08 16:08:01). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V38). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Latched Bollinger / RSI / stochastic oversold-recovery set-ups with MFI trend |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_lo` [15.0, 20.0] x `rsi_hi` [85.0, 80.0]: **4 trials**; BB 20 x 2, RSI 3, stoch 10 / 3, MFI 14.

## Ambiguities resolved

- Latched flags as written. Volume = broker tick volume (MFI). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
