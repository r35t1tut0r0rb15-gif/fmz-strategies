# #442091 基于ABCD形态且带止损追踪和止盈追踪的全新量化交易策略Best-ABCD-Pattern-Trading-Strategy-with-Stop-Loss-and-Take-Profit-Tracking -> `fmz_442091_abcd_zigzag_triggered_trailing_exits`

- FMZ source id: 442091 (lineage).
- Source: https://www.fmz.com/strategy/442091 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-19 11:25:29). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C150). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Fractal zigzag ABCD and bar-tested trailing levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_trail` [0.03, 0.05] x `tp_trigger` [0.03, 0.05]: **4 trials**; the ratio bands and the other percentages fixed.

## Ambiguities resolved

- Trailing levels are bar tests as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`none`
