# #491038 Multi Indicator Dynamic Trend Capture and Mean Reversion Strategy -> `fmz_491038_ema9_21_sma20_bb_basis_rsi_state_reversal`

- FMZ source id: 491038 (lineage).
- Source: https://www.fmz.com/strategy/491038 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-18 09:27:27). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C274). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA / SMA / RSI / Bollinger states |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`emaFastLen` [9, 5] x `emaSlowLen` [21, 50]: **4 trials**; SMA 20, RSI 14, BB 20.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days). MPL 2.0.

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
