# #429491 Trend Following Long Only Strategy -> `fmz_429491_channel_center_trend_long`

- FMZ source id: 429491 (lineage).
- Source: https://www.fmz.com/strategy/429491 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-17 15:55:41). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C25). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | An ATR multiple around a price channel. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 100 % of equity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [200, 100] x `atr_mult` [0.5, 1.0]: **4 trials**; smoother 5, ATR 10 fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`
