# #489134 Fibonacci Bollinger Bands with RSI Dynamic Take Profit Strategy -> `fmz_489134_vwma200_band_breakout_pct_target_rsi_exit_1h_reversal`

- FMZ source id: 489134 (lineage).
- Source: https://www.fmz.com/strategy/489134 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-02 09:37:00). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V46). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-checked target from the fill and RSI closes in the signals |
| 2 | PASS | Volume-weighted band breakouts with a fixed-percent target |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mult` [3.0, 2.0] x `tp_pct` [2.0, 3.0]: **4 trials**; VWMA / stdev 200 of hlc3, RSI 14 30 / 70.

## Ambiguities resolved

- Close-checked target from the fill. Volume = broker tick volume (VWMA). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
