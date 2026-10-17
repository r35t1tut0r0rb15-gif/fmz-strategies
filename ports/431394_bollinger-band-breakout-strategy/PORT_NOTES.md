# #431394 Bollinger Band Breakout Strategy -> `fmz_431394_bb_width_reentry_long`

- FMZ source id: 431394 (lineage).
- Source: https://www.fmz.com/strategy/431394 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-07 15:08:36). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C44). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percentage target |
| 2 | PASS | Bollinger bands and their relative width |
| 3 | PASS | BAT/USDT in the title and the pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [16, 32] x `tp_pct` [8.0, 2.0]: **4 trials**; 3 sd and the width band 20-50 fixed.

## Ambiguities resolved

- Long only. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
