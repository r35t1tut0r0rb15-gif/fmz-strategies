# #432804 Momentum Oscillation Trading Strategy -> `fmz_432804_basis_cross_close_target`

- FMZ source id: 432804 (lineage).
- Source: https://www.fmz.com/strategy/432804 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-21 16:57:20). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C54). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-checked exits |
| 2 | PASS | Basis crosses and percentages of the fill |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the close-checked exits quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `target_pct` [0.5, 1.0]: **4 trials**; the 95 % stop fixed.

## Ambiguities resolved

- Close-checked target and stop (rule 3). Entries from flat. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
