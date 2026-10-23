# #430252 基于RSI指标的趋势跟随策略RSI-Trend-Following-Strategy -> `fmz_430252_rsi14_percent_b_band_reentry_reversal`

- FMZ source id: 430252 (lineage).
- Source: https://www.fmz.com/strategy/430252 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-10-26 15:44:15). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V9). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI %B band re-entries |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Lot = equity / close x 100 % stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [50, 20] x `mult` [1.618, 2.0]: **4 trials**; RSI 14.

## Ambiguities resolved

- MFI branch off (no volume). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_threshold"`.

## Marks

`none`
