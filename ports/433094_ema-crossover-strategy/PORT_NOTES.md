# #433094 EMA Crossover Strategy -> `fmz_433094_ema_cross_signal_bar_exit`

- FMZ source id: 433094 (lineage).
- Source: https://www.fmz.com/strategy/433094 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-24 13:49:45). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C58). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average crosses and signal-bar levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [50, 20, 100]: **3 trials**.

## Ambiguities resolved

- Entry wins over a same-bar close. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
