# #458179 Adaptive Standard Deviation Breakout Trading Strategy Multi Period Optimization System Based on Dynamic Volatility -> `fmz_458179_sma20_3sd_lower_band_recovery_pct_close_tests_long`

- FMZ source id: 458179 (lineage).
- Source: https://www.fmz.com/strategy/458179 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-30 16:09:04). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C203). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the exits are close tests against the fill |
| 2 | PASS | Lower-band recoveries with percent exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mult` [3.0, 2.0] x `tp_pct` [0.01, 0.02] x `sl_pct` [0.005, 0.01]: **8 trials**; the SMA length fixed.

## Ambiguities resolved

- Date window dropped; exits are close tests vs the fill. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
