# #432309 Trend Following Short term Trading Strategy -> `fmz_432309_noro_sila_vote`

- FMZ source id: 432309 (lineage).
- Source: https://www.fmz.com/strategy/432309 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-11-16 11:11:32). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C51). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Dimensionless votes (the band and stop distances are ATR multiples) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sens` [5, 3] x `wow_len` [30, 15]: **4 trials**; the other votes' lengths fixed; the up and down sensitivities move together.

## Ambiguities resolved

- The votes as written (states kept). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_vote"`.

## Marks

`none`
