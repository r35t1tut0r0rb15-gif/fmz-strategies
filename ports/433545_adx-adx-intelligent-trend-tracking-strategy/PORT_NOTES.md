# #433545 ADX智能趋势跟踪策略ADX-Intelligent-Trend-Tracking-Strategy -> `fmz_433545_adx_box_breakout_bracket`

- FMZ source id: 433545 (lineage).
- Source: https://www.fmz.com/strategy/433545 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-28 14:04:00). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C61). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | PASS | Box breaks, ADX level and box-width exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 100000 cash quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`box_len` [20, 40] x `adx_level` [18, 25]: **4 trials**; ADX 14 / 14, target 1.0 and stop 0.5 box widths fixed.

## Ambiguities resolved

- Bracket from the signal bar's box; flat-only entries tracked on bar highs / lows. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`
