# #434585 Donchian Channel With Trailing Stop Loss Strategy -> `fmz_434585_donchian_mid_swing_exit`

- FMZ source id: 434585 (lineage).
- Source: https://www.fmz.com/strategy/434585 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-07 16:53:10). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C69). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Channel midline crosses and ATR-padded swing levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG434585. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [20, 50] x `atr_div` [3.0, 1.0]: **4 trials**; ATR 20 and the 3-bar swing fixed.

## Ambiguities resolved

- Exits as close-based signals; same-bar entry beats the close. REVERSAL INTENDED. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`
