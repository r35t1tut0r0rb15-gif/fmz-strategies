# #428975 PB SAR Backtest Strategy with Elastic Stop Loss -> `fmz_428975_peterbolic_sar`

- FMZ source id: 428975 (lineage).
- Source: https://www.fmz.com/strategy/428975 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-11 15:22:26). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C22). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Completed-bar state machine, bar-close orders. |
| 2 | PASS | Price levels from the bars themselves only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trigger_buffer_atr` [0.0, 0.25]: **2 trials** (declared starting variants; 0 is the source).

## Ambiguities resolved

- No inputs: two declared variants. Inert exits on non-existent ids. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "parabolic_sar"`.

## Marks

`none`
