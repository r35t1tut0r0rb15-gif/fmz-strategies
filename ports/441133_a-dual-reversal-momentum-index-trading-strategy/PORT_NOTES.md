# #441133 A Dual Reversal Momentum Index Trading Strategy -> `fmz_441133_reversal123_rmi_combo`

- FMZ source id: 441133 (lineage).
- Source: https://www.fmz.com/strategy/441133 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-06 09:29:34). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C147). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close pattern, stochastic and RMI states |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `length_rmi` [20, 10]: **4 trials**; zones 40 / 70 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
