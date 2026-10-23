# #429579 超趋势V策略Super-Trend-V-Strategy -> `fmz_429579_vpt_shadow_supertrend_open_ema_filter_long`

- FMZ source id: 429579 (lineage).
- Source: https://www.fmz.com/strategy/429579 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-18 12:35:53). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V9). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SuperTrend crossings of a volume-price line with an open-EMA filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity, capital 1000, commission 0.075 % stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`st_mult` [1.0, 2.0] x `st_period` [10, 20]: **4 trials**; EMA 7.

## Ambiguities resolved

- Long only through allow_entry_in. Volume = broker tick volume. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
