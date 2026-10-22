# #449949 Price-Action-Pyramiding-5-Profit-Target-3-Stop-Loss-价格行为-金字塔加仓-5止盈-3止损 -> `fmz_449949_three_pct_dip_counter_buy_five_pct_target_long`

- FMZ source id: 449949 (lineage).
- Source: https://www.fmz.com/strategy/449949 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-30 16:20:28). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C182). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; target fixed from the signal close |
| 2 | PASS | Dip buying with a percent target |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 1000 / close quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`drop` [0.03, 0.05] x `target` [0.05, 0.1]: **4 trials**; the 5-bar look-back and the counter fixed.

## Ambiguities resolved

- Add-on buys never fill (no pyramiding); counter as written. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`coarse_bar_stop`
