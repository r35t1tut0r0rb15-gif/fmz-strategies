# #452701 基于RSI背离的趋势反转交易策略-Trend-Reversal-Trading-Strategy-Based-on-RSI-Divergence -> `fmz_452701_rsi_reentry_latched_divergence_reversal`

- FMZ source id: 452701 (lineage).
- Source: https://www.fmz.com/strategy/452701 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-28 11:51:49). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C189). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI re-entries behind a latched divergence flag |
| 3 | PASS | Spot pair in the header only (the source sends shorts as written). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [14, 7] x `lookback` [5, 10]: **4 trials**; the levels fixed.

## Ambiguities resolved

- Latched divergence flags as written. REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
