# #473365 Dual Moving Average Crossover Adaptive Parameter Trading Strategy -> `fmz_473365_sma10_30_cross_reversal_long_bracket_from_replaced_avg`

- FMZ source id: 473365 (lineage).
- Source: https://www.fmz.com/strategy/473365 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-29 15:29:24). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C217). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the replaced position's price as the bracket base, as written |
| 2 | PASS | SMA crossings with a long bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [10, 20] x `slow` [30, 60] x `sl_pct` [0.01, 0.02] x `tp_pct` [0.02, 0.04]: **16 trials**.

## Ambiguities resolved

- The long's bracket from the replaced short's price (na from flat), as written; no trail (offset only). REVERSAL INTENDED. FREQ = "2D" (blocks of 2 broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
