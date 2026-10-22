# #473155 Dynamic Take Profit Smart Trailing Strategy -> `fmz_473155_intrabar_drop_buy_pct_target_long`

- FMZ source id: 473155 (lineage).
- Source: https://www.fmz.com/strategy/473155 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-27 16:41:16). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C214). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the fill-price target as a fixed fraction |
| 2 | PASS | Intrabar drop buys with a small target |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`drop_pct` [0.0098, 0.02] x `tp_pct` [0.0123, 0.03]: **4 trials**.

## Ambiguities resolved

- No trail (offset only), no stop. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`coarse_bar_stop`
