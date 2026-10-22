# #442961 Mayan Treasure Hunting Guide -> `fmz_442961_ema20_cross_close_direction_reversal`

- FMZ source id: 442961 (lineage).
- Source: https://www.fmz.com/strategy/442961 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-27 16:33:02). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C164). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings with the close direction |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50]: **2 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
