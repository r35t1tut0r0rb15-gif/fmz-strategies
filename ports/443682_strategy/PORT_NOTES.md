# #443682 均线突破 -> `fmz_443682_close_vs_sma120_daily_long`

- FMZ source id: 443682 (lineage).
- Source: https://www.fmz.com/strategy/443682 (javascript, author Crypto Joe, FMZ last
  modified 2024-03-24 13:45:19). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C168). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS (with note) | Acts once per new bar on the forming bar; the port evaluates on completed bars |
| 2 | PASS | Close vs SMA |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The balance-fraction size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [120, 50]: **2 trials**.

## Ambiguities resolved

- Completed-bar evaluation of a forming-bar bot. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
