# #432357 多时间框架MA蒙德里安交叉策略MZ-MA-Cross-Multiple-TimeFrame-Strategy -> `fmz_432357_daily_ha_edsma_lrc_cross`

- FMZ source id: 432357 (lineage).
- Source: https://www.fmz.com/strategy/432357 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-16 17:28:43). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C52). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; daily values from completed broker days |
| 2 | PASS | MA crosses of a daily Heikin Ashi close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Fixed quantity 5 and the commission stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_len` [30, 15] x `slow_len` [50, 100]: **4 trials**; the super smoother 20 / 2 poles fixed.

## Ambiguities resolved

- Daily HA close from completed broker days; MAs on the hourly bars as written. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_timeframe_ma"`.

## Marks

`none`
