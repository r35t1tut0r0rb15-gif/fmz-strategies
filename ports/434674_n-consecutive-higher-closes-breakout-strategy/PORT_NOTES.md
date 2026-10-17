# #434674 N Consecutive Higher Closes Breakout Strategy -> `fmz_434674_n_bars_up_long`

- FMZ source id: 434674 (lineage).
- Source: https://www.fmz.com/strategy/434674 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-08 10:50:54). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C70). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the script's levels as exit signals |
| 2 | ADAPT | Price-unit distances -> ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND434674. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`n_len` [4, 3] x `sl_atr` [0.0125, 1.0]: **4 trials**; the target is twice the stop distance (20 / 10), ATR 14 fixed.

## Ambiguities resolved

- Script levels tested on closes; price units -> ATR. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`none`
