# #451490 RSI双重差分策略-Dual-RSI-Differential-Strategy -> `fmz_451490_dual_rsi_difference_hold_days_reversal`

- FMZ source id: 451490 (lineage).
- Source: https://www.fmz.com/strategy/451490 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-15 10:41:10). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C185). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI-difference extremes with a time exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity sizing, commission and slippage stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_len` [21, 14] x `long_len` [42, 28] x `diff_lvl` [5, 10]: **8 trials**; the 5-day hold fixed.

## Ambiguities resolved

- The hold counts from the last bar the condition held. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
