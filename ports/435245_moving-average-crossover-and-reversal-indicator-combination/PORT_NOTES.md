# #435245 Moving Average Crossover and Reversal Indicator Combination Strategy -> `fmz_435245_rsi_sma_cci_side`

- FMZ source id: 435245 (lineage).
- Source: https://www.fmz.com/strategy/435245 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-13 15:20:20). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C76). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI and CCI states |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The fixed quantity 1 stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_ma` [50, 20] x `cci_len` [14, 28]: **4 trials**; RSI 14 fixed.

## Ambiguities resolved

- Unused price filters dropped. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
