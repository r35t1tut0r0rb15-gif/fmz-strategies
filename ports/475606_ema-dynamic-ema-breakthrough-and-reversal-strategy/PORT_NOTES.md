# #475606 EMA均线动态突破与反转策略-Dynamic-EMA-Breakthrough-and-Reversal-Strategy -> `fmz_475606_ema14_candle_break_body_wick_reversal`

- FMZ source id: 475606 (lineage).
- Source: https://www.fmz.com/strategy/475606 (PineScript v6, author ChaoZhang, FMZ last
  modified 2024-12-20 15:00:36). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C229). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA candle breaks |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_length` [14, 21]: **2 trials**; the candle shares fixed.

## Ambiguities resolved

- The sell wick test always holds (as written). REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
