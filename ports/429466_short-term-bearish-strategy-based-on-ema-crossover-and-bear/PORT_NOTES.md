# #429466 Short term Bearish Strategy Based on EMA Crossover and Bear Power Indicators -> `fmz_429466_combo_ema_bear_power`

- FMZ source id: 429466 (lineage).
- Source: https://www.fmz.com/strategy/429466 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-10-17 14:00:41). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C24). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | Price-unit levels -> ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND429466. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 20] x `sell_atr` [0.07, 0.5]: **4 trials**; buy level 0.007 ATR fixed.

## Ambiguities resolved

- Levels as ATR multiples. Disagreement closes all. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
