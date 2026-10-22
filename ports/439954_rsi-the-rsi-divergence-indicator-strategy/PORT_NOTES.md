# #439954 RSI多空分歧指标The-RSI-Divergence-Indicator-Strategy -> `fmz_439954_rsi9_divergence_long_tp80`

- FMZ source id: 439954 (lineage).
- Source: https://www.fmz.com/strategy/439954 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-25 11:49:36). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C127). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; pivots known after the right lookback |
| 2 | PASS | RSI pivots and price pivots |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The fixed quantity and pyramiding stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND366941. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len` [9, 14] x `tp_level` [80, 70]: **4 trials**; pivots 1 / 3 and range 5-60 fixed.

## Ambiguities resolved

- Adds are sizing. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`none`
