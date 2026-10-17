# #431226 基于ROC的RSI交易策略RSI-Based-on-ROC-Trading-Strategy -> `fmz_431226_rsi_of_roc_levels`

- FMZ source id: 431226 (lineage).
- Source: https://www.fmz.com/strategy/431226 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-11-06 10:52:31). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C43). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI levels of a ROC |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [20, 10] x `roc_len` [20, 10]: **4 trials**; zones 30 / 70 fixed.

## Ambiguities resolved

- Zones as written (momentum reading). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
