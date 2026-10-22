# #451729 EMA5与EMA13交叉策略-EMA5-and-EMA13-Crossover-Strategy -> `fmz_451729_ema5_13_state_short_2d`

- FMZ source id: 451729 (lineage).
- Source: https://www.fmz.com/strategy/451729 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-17 15:28:17). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C187). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA 5 / 13 trend state |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The quantity 1 stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [5, 9] x `slow` [13, 21]: **4 trials**.

## Ambiguities resolved

- Short only. FREQ = "2D" (blocks of 2 broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
