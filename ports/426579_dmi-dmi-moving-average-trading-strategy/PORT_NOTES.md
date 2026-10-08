# #426579 DMI Moving Average Trading Strategy -> `fmz_426579_dmi_extremes`

- Source: https://www.fmz.com/strategy/426579 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-13 14:42:19). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A23). Not run.

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

`di_len` [11, 14, 21] x `low_level` [10, 15]: **6 trials**, defaults 11 / 10 (the source's); high level 40 fixed.

## Ambiguities resolved

- Contrarian as written: long when DI- dominates, short when DI+ dominates.
- ADX only plots.
- FREQ = "1min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "directional_movement"`.

## Marks (2026-10-07)

`none`
