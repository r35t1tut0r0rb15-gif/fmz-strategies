# #437503 基于ATR通道的破口踏入趋势策略ATR-Channel-Breakout-Trend-following-Strategy -> `fmz_437503_atr_renko_box_steps`

- FMZ source id: 437503 (lineage).
- Source: https://www.fmz.com/strategy/437503 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-03 11:53:52). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C101). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ATR box steps |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_length` [60, 30]: **2 trials**.

## Ambiguities resolved

- Same-resolution security; box rules as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`none`
