# #482673 动态波云趋势ATR止损策略-Dynamic-Cloud-Trend-ATR-Stop-Loss-Strategy -> `fmz_482673_tenkan_kijun_cross_cloud_chikou_atr_stop`

- FMZ source id: 482673 (lineage).
- Source: https://www.fmz.com/strategy/482673 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:54:39). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L33). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders and a stop set at entry. |
| 2 | PASS | Ichimoku mid-points, lagged closes and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity; the stop via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [1.5, 2.5] x `base_len` [26, 20]: **4 trials**; defaults 1.5 / 26 (the source's); tenkan 9, span B 52,
displacement 26 and ATR 14 fixed.

## Ambiguities resolved

- The spans are not displaced; the chikou test is close[26] against the current close (a long needs the close below
  the close 26 bars ago), as written.
- The closes act on the position held at the bar's start and never undo an entry on that bar (#430850);
  `simulate()` mirrors the house stop from the fill (as #430254).
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

none
