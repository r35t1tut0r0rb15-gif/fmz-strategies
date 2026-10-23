# #431004 基于态势的Karobein均值回归策略Scaled-Normalized-Vector-Strategy-with-Karobein-Mean-Reversion -> `fmz_431004_last_34min_return_sign_daily_reversal`

- FMZ source id: 431004 (lineage).
- Source: https://www.fmz.com/strategy/431004 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-03 16:56:13). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V11). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Sign of the day's last intraday return |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 1-unit orders stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tf` [34, 60] x `thresh` [14.0, 100.0]: **4 trials**; divisor 1000000.

## Ambiguities resolved

- The 34-minute bars counted from the broker-day start (repainting noted by the author). No volume.
- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "intraday_return"`.

## Marks

`none`
