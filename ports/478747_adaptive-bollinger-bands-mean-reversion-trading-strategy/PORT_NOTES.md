# #478747 Adaptive Bollinger Bands Mean Reversion Trading Strategy -> `fmz_478747_bb20_reentry_basis_close_pct_bracket_reversal`

- FMZ source id: 478747 (lineage).
- Source: https://www.fmz.com/strategy/478747 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-17 16:37:52). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C240). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar bracket as fractions of the fill |
| 2 | PASS | Bollinger re-entries with basis closes and a percent bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 200 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_length` [20, 50] x `tp_pct` [0.02, 0.01]: **4 trials**; 2 sd, stop 1 %.

## Ambiguities resolved

- Repeat-signal re-sends not followed. REVERSAL INTENDED. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`trailing_stop_pending`
