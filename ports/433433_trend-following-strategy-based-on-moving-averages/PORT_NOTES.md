# #433433 Trend Following Strategy Based on Moving Averages -> `fmz_433433_tk_cross_above_ema200`

- FMZ source id: 433433 (lineage).
- Source: https://www.fmz.com/strategy/433433 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-11-27 15:57:15). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C60). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Ichimoku lines and an EMA |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The initial_capital / close quantity stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`conv` [9, 20] x `ema_len` [200, 100]: **4 trials**; base 26 fixed.

## Ambiguities resolved

- Level entry. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
