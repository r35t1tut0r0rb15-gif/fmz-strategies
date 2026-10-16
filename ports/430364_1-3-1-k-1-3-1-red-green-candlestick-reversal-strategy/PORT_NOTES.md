# #430364 1-3-1-红绿K线反转策略1-3-1-Red-Green-Candlestick-Reversal-Strategy -> `fmz_430364_red_then_three_green_bracket_long`

- FMZ source id: 430364 (lineage).
- Source: https://www.fmz.com/strategy/430364 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-10-27 16:00:41). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C35). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry. |
| 2 | PASS | Bar colours, lows and a 1 R target. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity per entry stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rr` [1.0, 2.0]: **2 trials**; the pattern is fixed.

## Ambiguities resolved

- Flat follows the house bracket on bars. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
