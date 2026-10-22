# #492007 RSI动态背离量化策略-RSI-Dynamic-Divergence-Quantitative-Strategy -> `fmz_492007_rsi14_pivot5_divergence_reversal`

- FMZ source id: 492007 (lineage).
- Source: https://www.fmz.com/strategy/492007 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-25 14:57:31). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C275). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the re-sent swing bracket pending |
| 2 | PASS | RSI pivot divergences |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookLeft` [5, 3] x `rangeUpper` [60, 30]: **4 trials**; RSI 14, right 5, min spacing 5.

## Ambiguities resolved

- The per-bar swing bracket is pending. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_divergence"`.

## Marks

`trailing_stop_pending`
