# #458058 Double Smoothed Heiken Ashi Trend Following Strategy -> `fmz_458058_double_smoothed_heikin_ashi_turn_long`

- FMZ source id: 458058 (lineage).
- Source: https://www.fmz.com/strategy/458058 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-29 16:02:27). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C200). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Smoothed Heikin Ashi colour turns |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len` [10, 20] x `len2` [10, 5]: **4 trials**.

## Ambiguities resolved

- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
