# #437748 基于双MA叠加的自适应回测时间范围选择策略Adaptive-Backtest-Date-Range-Selection-Strategy-Based-on-Double-MA -> `fmz_437748_sma_14_28_cross_long`

- FMZ source id: 437748 (lineage).
- Source: https://www.fmz.com/strategy/437748 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-05 12:12:10). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C105). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossing |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [14, 7] x `slow` [28, 56]: **4 trials**.

## Ambiguities resolved

- Date range dropped. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
