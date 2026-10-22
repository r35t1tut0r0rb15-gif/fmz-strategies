# #441132 Bottom Hunter Strategy -> `fmz_441132_macd_divergence_bottom_pct_bracket_long`

- FMZ source id: 441132 (lineage).
- Source: https://www.fmz.com/strategy/441132 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-06 09:26:54). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C146). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | PASS | Divergence, EMA, RSI and range filters with a percent bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp` [0.10, 0.05] x `sl` [0.02, 0.05]: **4 trials**; indicator lengths and thresholds fixed.

## Ambiguities resolved

- Bracket from the signal close, re-based on the fill. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`coarse_bar_stop`
