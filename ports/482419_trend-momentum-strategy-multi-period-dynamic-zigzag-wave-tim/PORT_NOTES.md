# #482419 趋势动量策略-之字形多重周期动态波段择时系统-Trend-Momentum-Strategy-Multi-Period-Dynamic-ZigZag-Wave-Timing-System -> `fmz_482419_zigzag_dir_williams_r_cross_pct_bracket_2d`

- FMZ source id: 482419 (lineage).
- Source: https://www.fmz.com/strategy/482419 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-18 13:29:06). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L37). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders and a bracket set at entry. |
| 2 | PASS | Confirmed pivots, Williams %R and percentages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 300 % of equity; the bracket via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`depth` [5, 3] x `tp_pct` [2, 4]: **4 trials**; defaults 5 / 2 (the source's); deviation 1 %, %R 14 (-20 / -80) and
the 1 % stop fixed.

## Ambiguities resolved

- Strict pivots confirmed `depth` bars later (as #430850); the 1 % deviation test as written.
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). Two-day bars: blocks of broker-day dates from
  1970-01-01 (decision owed, #426509).

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`coarse_bar_stop`
