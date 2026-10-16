# #428756 blackcat L1 MartinGale Scalping Strategy -> `fmz_428756_sma3_8_state_long`

- FMZ source id: 428756 (lineage).
- Source: https://www.fmz.com/strategy/428756 (PineScript v5, author Zer3192, FMZ last
  modified 2023-11-03 17:27:45). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C19). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Moving-average comparisons only. |
| 3 | PASS |  |
| 4 | DONE | Pyramiding, the adds and the inert take-profit / stop levels stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG428756. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [3, 5] x `slow` [8, 13]: **4 trials**; the inert take-profit / stop multipliers are not parameters.

## Ambiguities resolved

- Non-`var` levels make the exits pure SMA-state exits. Short entries forbidden by the default mode.
- Long only. FREQ = "bar_size_pending" (no bar size in the source).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`bar_size_pending`
