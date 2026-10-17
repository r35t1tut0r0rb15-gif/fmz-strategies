# #432969 Bollinger Trend Shock Trading Strategy -> `fmz_432969_bb_trend_dip`

- FMZ source id: 432969 (lineage).
- Source: https://www.fmz.com/strategy/432969 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-23 10:57:10). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C56). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band crosses relative to moving averages |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() fixed quantity 1 stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG432969. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`boll_len` [20, 40] x `boll_mult` [2.3, 1.5]: **4 trials**; SMA 200 / 230 fixed.

## Ambiguities resolved

- Short entry on an upward cross of the upper band, as written; entry wins over a same-bar exit. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
