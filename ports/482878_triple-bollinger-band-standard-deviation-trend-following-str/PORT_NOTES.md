# #482878 Triple Bollinger Band Standard Deviation Trend Following Strategy -> `fmz_482878_three_closes_beyond_bb20_2_first_bar_stop_1r_flat`

- FMZ source id: 482878 (lineage).
- Source: https://www.fmz.com/strategy/482878 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-20 16:16:14). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C252). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; three-bar bracket as fractions of the fill |
| 2 | PASS | Three closes beyond a Bollinger band with a 1R bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 40] x `mult` [2.0, 1.5]: **4 trials**; target 1R.

## Ambiguities resolved

- The flat gate is followed in a loop with the bracket on bar highs / lows. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
