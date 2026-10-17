# #488541 动态布林带突破趋势追踪策略-Dynamic-Bollinger-Bands-Breakout-Trend-Tracking-Strategy -> `fmz_488541_bb_breakout_pct_bracket`

- FMZ source id: 488541 (lineage).
- Source: https://www.fmz.com/strategy/488541 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-28 17:24:35). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L9). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the fill. |
| 2 | PASS | Bands and percentages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mult` [2.0, 1.5] x `sl_pct` [2.0, 4.0]: **4 trials**; defaults 2 / 2 (the source's); BB 20 and TP 5 % fixed.

## Ambiguities resolved

- The bracket from the average price (the fill) is exact as scalars. REVERSAL INTENDED. FREQ = "3h";
  `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`coarse_bar_stop`
