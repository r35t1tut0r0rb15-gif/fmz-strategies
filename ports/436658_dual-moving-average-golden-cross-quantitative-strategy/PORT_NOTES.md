# #436658 Dual Moving Average Golden Cross Quantitative Strategy -> `fmz_436658_hull3_turn_vwma42_filter_flat_only`

- FMZ source id: 436658 (lineage).
- Source: https://www.fmz.com/strategy/436658 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-26 17:02:29). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V19). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Short Hull turns against a VWMA filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`z` [3, 5] x `a` [14, 20]: **4 trials**; VWMA filter length 3 x a.

## Ambiguities resolved

- Entries only from flat (opentrades before the close fills). Volume = broker tick volume. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "hull_ma"`.

## Marks

`none`
