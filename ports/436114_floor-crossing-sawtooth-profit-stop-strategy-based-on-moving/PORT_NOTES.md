# #436114 Floor Crossing Sawtooth Profit Stop Strategy Based on Moving Average -> `fmz_436114_span_b_alternating_bracket`

- FMZ source id: 436114 (lineage).
- Source: https://www.fmz.com/strategy/436114 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-21 12:26:18). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C86). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | REVIEW | Ternary flags true on every flat bar; price-unit ATR limits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`span` [52, 26] x `filter` [True, False]: **4 trials**; stop 1 %, target 2 % and the ATR limits fixed.

## Ambiguities resolved

- Flat-branch flags; alternation filter; ATR limits as fractions. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`none`
