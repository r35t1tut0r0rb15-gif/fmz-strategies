# #442936 Donchain Channel Based Trading Strategy -> `fmz_442936_donchian_260_high_60_low_exit_long`

- FMZ source id: 442936 (lineage).
- Source: https://www.fmz.com/strategy/442936 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-27 14:57:37). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C163). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Long-window channel highs with a short-window exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`longer` [260, 120] x `shorter` [60, 20]: **4 trials**.

## Ambiguities resolved

- Exit tests i = 1 only (loop break as written); the run-date close dropped. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`
