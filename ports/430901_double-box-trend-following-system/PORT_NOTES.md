# #430901 Double Box Trend Following System -> `fmz_430901_double_box_trend`

- FMZ source id: 430901 (lineage).
- Source: https://www.fmz.com/strategy/430901 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-02 17:19:22). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C42). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving stop fixed at entry (rule 2) |
| 2 | PASS | Rolling boxes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`flb` [80, 160] x `slb` [21, 10]: **4 trials**.

## Ambiguities resolved

- Pending (not emitted as written): the stop re-issued at the moving 80-bar low; fixed at the signal bar here.
- Close / close_all conventions as stated. REVERSAL INTENDED. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`trailing_stop_pending`
