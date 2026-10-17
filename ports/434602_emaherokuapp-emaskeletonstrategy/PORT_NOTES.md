# #434602 动态EMAherokuapp俯瞰策略EMAskeletonstrategy -> `fmz_434602_ema_high_cross_bracket_long`

- FMZ source id: 434602 (lineage).
- Source: https://www.fmz.com/strategy/434602 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-07 17:20:44). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C69). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-sized exits fixed at entry (approximation stated) |
| 2 | PASS | An average against the high and percent exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the exits quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [50, 25] x `safety_len` [70, 140]: **4 trials**; the 5.1 % / 9.6 % exits fixed.

## Ambiguities resolved

- Close-sized exits fixed at the fill (trailing_stop_pending); date window dropped. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`trailing_stop_pending`
