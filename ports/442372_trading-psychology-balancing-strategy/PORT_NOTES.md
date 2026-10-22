# #442372 Trading Psychology Balancing Strategy -> `fmz_442372_psar_ttm_cross_ema100_swing_levels`

- FMZ source id: 442372 (lineage).
- Source: https://www.fmz.com/strategy/442372 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-21 14:33:04). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C155). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SAR / squeeze-momentum crosses with close-tested swing levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_length` [100, 200] x `rr` [1.125, 2.0]: **4 trials**; the SAR, TTM and swing settings fixed.

## Ambiguities resolved

- Close-tested swing stop / target. Opposite entries cannot occur (entries only from flat). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "parabolic_sar"`.

## Marks

`none`
