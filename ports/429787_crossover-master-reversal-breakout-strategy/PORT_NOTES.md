# #429787 Crossover Master Reversal Breakout Strategy -> `fmz_429787_cdc_action_zone_long`

- FMZ source id: 429787 (lineage).
- Source: https://www.fmz.com/strategy/429787 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-10-20 17:24:14). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C29). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Moving-average states only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND429787. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`prd1` [12, 8] x `prd2` [26, 50]: **4 trials**; EMA 2 of ohlc4 fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
