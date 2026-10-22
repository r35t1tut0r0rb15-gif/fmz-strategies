# #477535 Dynamic Dual Technical Indicator Oversold Overbought Confirmation Trading Strategy -> `fmz_477535_rsi14_cci20_joint_extreme_pct_bracket_reversal`

- FMZ source id: 477535 (lineage).
- Source: https://www.fmz.com/strategy/477535 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-01-06 11:54:50). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C233). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar bracket as fractions of the fill |
| 2 | PASS | RSI / CCI joint extremes with a bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`cci_level` [200, 150] x `rr` [2.0, 1.0]: **4 trials**; RSI 14 / 80 / 20, CCI 20, stop 1 %.

## Ambiguities resolved

- Repeat-signal re-sends not followed. REVERSAL INTENDED. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`trailing_stop_pending`
