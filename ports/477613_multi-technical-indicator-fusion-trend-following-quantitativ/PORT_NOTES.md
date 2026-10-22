# #477613 Multi Technical Indicator Fusion Trend Following Quantitative Trading Strategy -> `fmz_477613_rsi14_bb30_extreme_sma20_50_pullback_reversal`

- FMZ source id: 477613 (lineage).
- Source: https://www.fmz.com/strategy/477613 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-06 16:57:57). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C236). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI / band extremes against the SMA order |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_low` [25, 30] x `bb_length` [30, 20]: **4 trials**; RSI high 80, SMA 20 / 50, 2 sd.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
