# #362497 MAHL-Band -> `fmz_362497_mahl_band_dmi_entry`

- Source: https://www.fmz.com/strategy/362497 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-11 20:48:53). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A8). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_len` [3, 5, 8] x `di_len` [14, 17, 21] = **9 trials**.

## Ambiguities resolved

- The 60-bar band lines are plots only.
- `FREQ = "10min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "directional_movement"`.

## Marks (2026-10-07)

`none`
