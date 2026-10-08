# #426879 Trend Following Strategy Based on Dynamic Support and Resistance -> `fmz_426879_highest_average_breakout_long`

- Source: https://www.fmz.com/strategy/426879 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-15 11:28:00). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A27). Not run.

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

`highest_length` [100, 200] x `atr_multiplier` [2, 3]: **4 trials**, defaults 200 / 2 (the source's); average 10, ATR 14 fixed.

## Ambiguities resolved

- Same bar: from flat the entry stands; while long the close goes flat.
- Long only. Daily bars are broker days.

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks (2026-10-07)

`none`
