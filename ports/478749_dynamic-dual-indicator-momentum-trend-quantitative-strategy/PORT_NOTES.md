# #478749 Dynamic Dual Indicator Momentum Trend Quantitative Strategy System -> `fmz_478749_sma9_21_cross_rsi50_2_4pct_bracket_rsi_exit_reversal`

- FMZ source id: 478749 (lineage).
- Source: https://www.fmz.com/strategy/478749 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-17 16:41:17). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V37). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket at the signal close as fractions of the fill |
| 2 | PASS | SMA crossings against the RSI side, RSI-midline exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl` [0.02, 0.03] x `tp` [0.04, 0.06]: **4 trials**; SMA 9 / 21, RSI 14.

## Ambiguities resolved

- Filters off by default. Bracket at the signal close. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
