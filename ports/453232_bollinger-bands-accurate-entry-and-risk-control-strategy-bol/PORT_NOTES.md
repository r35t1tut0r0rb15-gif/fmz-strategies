# #453232 Bollinger-Bands-Accurate-Entry-And-Risk-Control-Strategy-Bollinger-Bands准确入场和风险控制策略 -> `fmz_453232_sma34_one_sd_band_state_reversal`

- FMZ source id: 453232 (lineage).
- Source: https://www.fmz.com/strategy/453232 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-03 10:53:56). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C191). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | One-deviation band states |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [34, 20, 50]: **3 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
