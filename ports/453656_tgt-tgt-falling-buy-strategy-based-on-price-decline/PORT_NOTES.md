# #453656 TGT基于价格下跌买入策略-TGT-Falling-Buy-Strategy-Based-on-Price-Decline -> `fmz_453656_five_pct_drop_buy_close_over_fill_long`

- FMZ source id: 453656 (lineage).
- Source: https://www.fmz.com/strategy/453656 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-07 15:33:26). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C193). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the profit test against the fill price |
| 2 | PASS | Big-drop dip buying |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The balance-based quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`drop_pct` [5.0, 3.0, 8.0]: **3 trials**.

## Ambiguities resolved

- Exit on the first close over the fill price. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
