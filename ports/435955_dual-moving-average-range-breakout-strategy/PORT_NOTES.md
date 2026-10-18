# #435955 Dual Moving Average Range Breakout Strategy -> `fmz_435955_ema_stack_persistence`

- FMZ source id: 435955 (lineage).
- Source: https://www.fmz.com/strategy/435955 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-20 13:59:38). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C83). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average stack |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The fixed order size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`hold` [10, 5] x `ema200` [200, 100]: **4 trials**; EMA 10 / 20 / 50 fixed.

## Ambiguities resolved

- Operator precedence in the close rule; orders in call order. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
