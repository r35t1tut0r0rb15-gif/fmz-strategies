# #427516 Bollinger Bands and Fibonacci Trading Strategy -> `fmz_427516_bb_fib_as_written`

- FMZ source id: 427516 (lineage).
- Source: https://www.fmz.com/strategy/427516 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-21 21:04:38). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C9). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bands in standard deviations, range fractions. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 40, 10] x `mult` [2, 1.5]: **6 trials**; defaults 20 / 2.0 (the source's); Fibonacci levels 0 % / 100 % and 50 bars fixed.

## Ambiguities resolved

- **As written** the default Fibonacci levels make the long filter impossible (low above the 50-bar high): effectively short only. **Decision owed (minor):** other Fibonacci levels would be a separate version.
- The script's own flags gate entries as written; a close only acts on the side held.
- FREQ = "45min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
