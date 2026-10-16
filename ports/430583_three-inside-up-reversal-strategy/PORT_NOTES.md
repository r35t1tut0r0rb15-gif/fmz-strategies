# #430583 Three Inside Up Reversal Strategy -> `fmz_430583_three_inside_up_short`

- FMZ source id: 430583 (lineage).
- Source: https://www.fmz.com/strategy/430583 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-10-30 15:36:07). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C36). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-time level checks. |
| 2 | ADAPT | The price-unit distances -> ATR fractions. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`dist_atr` [0.07, 0.5]: **2 trials**; take profit = stop distance (both 20 in the source).

## Ambiguities resolved

- The bullish pattern enters short, as written. Price-unit distances -> ATR. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
