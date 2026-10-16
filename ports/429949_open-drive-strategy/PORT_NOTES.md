# #429949 Open Drive Strategy -> `fmz_429949_london_ny_open_drive`

- FMZ source id: 429949 (lineage).
- Source: https://www.fmz.com/strategy/429949 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-10-23 15:13:49). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C29). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close entries; the moving limit exit is not emitted (rule 2). |
| 2 | PASS | Range ratios only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 2-contract quantity and the commission stored; the exit quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`threshold` [0.15, 0.25] x `range_len` [5, 10]: **4 trials**; the London windows fixed.

## Ambiguities resolved

- Pending (not emitted): from the fourth bar after a signal, a limit exit at each bar's close,
  re-placed every bar (same id), for both sides.
- REVERSAL INTENDED. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`trailing_stop_pending`
