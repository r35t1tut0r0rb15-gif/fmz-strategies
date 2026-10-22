# #449968 RSI变动方向改变策略-RSI-Direction-Change-Strategy -> `fmz_449968_rsi_jump_entry_rsi_move_exit_reversal`

- FMZ source id: 449968 (lineage).
- Source: https://www.fmz.com/strategy/449968 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-30 17:29:10). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C182). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI jumps with an RSI-move exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`change` [10.0, 15.0] x `exit_move` [5.0, 10.0]: **4 trials**; the RSI length and the 1 % price test fixed.

## Ambiguities resolved

- Closes act on held, non-reversed positions. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
