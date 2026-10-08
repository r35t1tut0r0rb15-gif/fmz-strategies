# #426834 Simple Trend Following Strategy -> `fmz_426834_millebot_hull_mcginley`

- Source: https://www.fmz.com/strategy/426834 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-14 18:01:07). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A26). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`hma_len` [30, 50] x `mcg_len` [30, 50] x `sl_pct` [3, 5]: **8 trials**, defaults 50 / 50 / 5 (the source's); RRR 2 fixed.

## Ambiguities resolved

- Bracket from the signal close applied to the fill (sl 5 %, tp 10 %); simulate() mirrors it because entries need flat.
- isLong / isShort clear only at the Hull turn (a stopped trade's flag then closes nothing).
- Risk-based contracts are sizing.
- Stops on 4h bars: coarse_bar_stop.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`coarse_bar_stop`
