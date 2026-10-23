# #439103 Dual Moving Average Golden Cross Strategy -> `fmz_439103_vwma_stack_rsi30_edge_3bar_hold_1h_reversal`

- FMZ source id: 439103 (lineage).
- Source: https://www.fmz.com/strategy/439103 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-17 17:38:36). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V22). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Stacked volume-weighted averages with an RSI filter, fixed 3-bar hold |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Entry qty 1 unit, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`hold_bars` [3, 6] x `rsi_len` [30, 14]: **4 trials**; VWMA 20 / 50 / 100, RSI 50 / 48.5.

## Ambiguities resolved

- Closes three bars after the signal, only on an unchanged position. Volume = broker tick volume (VWMA). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_weighted_ma"`.

## Marks

`none`
