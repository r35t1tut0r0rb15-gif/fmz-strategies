# #483504 动量阈值驱动的平衡力量交易策略-Momentum-Threshold-Driven-Balance-of-Power-Trading-Strategy -> `fmz_483504_balance_of_power_threshold_long`

- FMZ source id: 483504 (lineage).
- Source: https://www.fmz.com/strategy/483504 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 16:50:22). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L19). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | A bar-shape ratio. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The leverage qty quoted, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`entry_level` [0.8, 0.6] x `exit_level` [-0.8, -0.6]: **4 trials**; defaults 0.8 / -0.8 (the source's).

## Ambiguities resolved

- A bar with high == low has no value (na), as in Pine.
- "US30 4H" in the title is a label; the backtest header says 1d: broker days stamped with their first minute (as
  #430984). Long only: opposite entries cannot occur. No stops. FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum"`.

## Marks

`none`
