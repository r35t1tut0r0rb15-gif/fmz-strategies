# #488268 趋势过滤多均线交叉ATR风控量化策略-Multi-Moving-Average-Crossover-Strategy-with-Trend-Filter-and-ATR-Risk-Management -> `fmz_488268_sma20_ema89_cross_flat_bracket`

- FMZ source id: 488268 (lineage).
- Source: https://www.fmz.com/strategy/488268 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-26 13:42:55). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L11). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at the signal bar. |
| 2 | PASS | Moving averages and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_mult` [2.0, 1.5] x `tp_mult` [3.0, 4.0]: **4 trials**; defaults 2 / 3 (the source's); SMA 20, EMA 89, SMA 200 and
ATR 14 fixed.

## Ambiguities resolved

- Entries only from flat (`position_size == 0`): `simulate()` mirrors the house bracket from the fill bar (#430254);
  an entry is allowed on the bar a stop or target is hit. Opposite entries cannot occur. Stop module:
  `portfolio_kwargs` {} (D4). FREQ = "2h": `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
