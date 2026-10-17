# #482424 动量趋势跟踪指标DMIADX交叉策略-Momentum-Trend-Following-DMIADX-Crossover-Strategy -> `fmz_482424_di_cross_adx25_pct_bracket`

- FMZ source id: 482424 (lineage).
- Source: https://www.fmz.com/strategy/482424 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-18 13:47:09). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L36). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders and a bracket from the fill. |
| 2 | PASS | DMI / ADX and percentage distances. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 250 % of equity; the bracket via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`adx_min` [25, 20] x `tp_pct` [2, 4]: **4 trials**; defaults 25 / 2 (the source's); DMI / ADX 14 and the 1 % stop
fixed.

## Ambiguities resolved

- The bracket is measured from `strategy.position_avg_price` (one entry: the fill): applied from the fill (decision
  owed as #489289).
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

`coarse_bar_stop`
