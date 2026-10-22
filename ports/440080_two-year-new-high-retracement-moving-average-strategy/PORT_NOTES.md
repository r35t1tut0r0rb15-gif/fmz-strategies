# #440080 Two Year New High Retracement Moving Average Strategy -> `fmz_440080_two_year_high_ema_zone_pullback_long`

- FMZ source id: 440080 (lineage).
- Source: https://www.fmz.com/strategy/440080 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-26 14:49:28). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C130). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the wrong-side stop read as a close signal |
| 2 | PASS | EMA zone, two-year high and percent levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`high_len` [504, 252] x `var_max` [10.0, 5.0]: **4 trials**; EMA 13 / 21 and the 5 % / 20 % exits fixed.

## Ambiguities resolved

- End-date close_all dropped; wrong-side stop read as a close. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
