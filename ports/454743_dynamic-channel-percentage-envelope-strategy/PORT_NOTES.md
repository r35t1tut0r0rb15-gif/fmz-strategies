# #454743 Dynamic Channel Percentage Envelope Strategy -> `fmz_454743_sma10_envelope_reentry_basis_exit_long`

- FMZ source id: 454743 (lineage).
- Source: https://www.fmz.com/strategy/454743 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-06-21 15:33:47). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C196). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Envelope re-entries with a basis exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [10, 20] x `pct` [10.0, 5.0]: **4 trials**.

## Ambiguities resolved

- Long only. FREQ = "2D" (blocks of 2 broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
