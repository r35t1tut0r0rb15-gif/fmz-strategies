# #449724 GBS高低点确认策略-GBS-TOP-BOTTOM-Confirmed-Strategy -> `fmz_449724_swing_high_break_swing_low_exit_long`

- FMZ source id: 449724 (lineage).
- Source: https://www.fmz.com/strategy/449724 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-28 14:42:02). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C180). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; swing levels from completed bars |
| 2 | PASS | Swing-high breaks with swing-low exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

No parameter reaches the orders: **1 trial**, the source as written.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`none`
