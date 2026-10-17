# #432225 CCI强势突破策略CCI-Strong-Breakthrough-Strategy -> `fmz_432225_cci_turn_long`

- FMZ source id: 432225 (lineage).
- Source: https://www.fmz.com/strategy/432225 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-15 16:52:06). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C50). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-checked stop |
| 2 | PASS | CCI bands and percentages of the open / fill |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the close-checked stop quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 14] x `loss_pct` [8.0, 4.0]: **4 trials**; the bands +-150 and the 0.25 % filter fixed.

## Ambiguities resolved

- The 8 % stop is close-checked (exit signal). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
