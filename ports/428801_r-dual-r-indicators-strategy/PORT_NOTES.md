# #428801 双R指标策略Dual-R-Indicators-Strategy -> `fmz_428801_rsi6_recovery_in_trend`

- FMZ source id: 428801 (lineage).
- Source: https://www.fmz.com/strategy/428801 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-10-09 15:46:05). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C20). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | RSI levels and moving-average comparisons only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() pyramiding, commission and capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_length` [6, 14] x `trend_length` [182, 100]: **4 trials**; 30 / 70 and SMA 10 / 20 fixed.

## Ambiguities resolved

- The unused SAR is dropped. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
