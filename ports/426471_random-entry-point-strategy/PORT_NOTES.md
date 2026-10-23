# #426471 Random Entry Point Strategy -> `fmz_426471_volume_mod6_random_entry_long_close_bracket`

- FMZ source id: 426471 (lineage).
- Source: https://www.fmz.com/strategy/426471 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-12 14:11:33). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-based target / stop |
| 2 | PASS | Volume-parity entry with a fixed close-based target / stop (a random-entry benchmark) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Cash 500 (commented strategy()) stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`i` [6, 10] x `take_profit` [15.0, 8.0]: **4 trials**; stop -5 %.

## Ambiguities resolved

- Volume mod 6 is the draw, as written (weird case). Volume = broker tick volume. Long only. FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "random_benchmark"`.

## Marks

`none`
