# #475596 Triple Supertrend and Bollinger Bands Multi Indicator Trend Following Strategy -> `fmz_475596_bb20_break_triple_supertrend_agree_reversal`

- FMZ source id: 475596 (lineage).
- Source: https://www.fmz.com/strategy/475596 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-20 14:28:58). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C228). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band breakouts with three agreeing supertrends |
| 3 | PASS | No exchange header. |
| 4 | DONE | Commission and slippage stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length_bb` [20, 50] x `atr_period` [10, 20]: **4 trials**; factors 3 / 4 / 5.

## Ambiguities resolved

- No bar size in the source (bar_size_pending). REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`bar_size_pending`
