# #442342 Bollinger Bands Breakout Trading Strategy -> `fmz_442342_bb_poke_return_named_entries_reversal`

- FMZ source id: 442342 (lineage).
- Source: https://www.fmz.com/strategy/442342 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-21 11:35:14). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C154). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | REVIEW | Band pokes and returns; the basis stops are pending |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size, capital and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [51, 20] x `mult` [1.1, 2.0]: **4 trials**; the basis stops are pending.

## Ambiguities resolved

- Named entries in call order, one position at a time; the re-sent basis stops are pending (trailing_stop_pending). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`trailing_stop_pending`
