# #442543 Bull Flag Breakout Strategy -> `fmz_442543_bull_flag_six_bar_exit_long`

- FMZ source id: 442543 (lineage).
- Source: https://www.fmz.com/strategy/442543 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-22 16:41:04). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C158). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Flagpole and flag pattern |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`pole_mult` [3.0, 2.0] x `exit_bars` [6, 12]: **4 trials**; the ATR length and the flag zone fixed.

## Ambiguities resolved

- Zone from the latest pole at each bar; count from the latest flag. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
