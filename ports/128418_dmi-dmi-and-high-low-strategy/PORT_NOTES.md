# #128418 动向指数DMI与高低点策略 -> `fmz_128418_kaufman_ama_cross`

- Source: https://www.fmz.com/strategy/128418 (MyLanguage, author 阿基米德的浴缸, FMZ last modified
  2019-08-20 10:24:43). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A1). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Close-price model, completed bars. |
| 2 | PASS | Efficiency ratio and smoothing constants are dimensionless. |
| 3 | PASS | BitMEX in the header only. |
| 4 | DONE | One lot per signal; no sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED | |

## Declared grid (criterion 5)

`n` [10, 20, 30] x `m` [40, 60, 80] = **9 trials** (the efficiency-ratio windows of the fast and
slow AMA). Fast/slow smoothing ends 4/60 and 8/120 fixed.

## Ambiguities resolved

- The title says DMI and high/low; the code computes two adaptive moving averages and trades
  their cross. The port follows the code.
- `cq22`/`aa` lines are display only.
- Reversal in one bar (BPK/SPK) as written; flat-first is not offered by the source.
- `FREQ = "5min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`: moving-average cross, always in (as #103070).

## Marks (2026-10-07)

`none`
