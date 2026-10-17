# #489300 可配置移动平均线交叉策略-Configurable-Moving-Average-Crossover-Strategy -> `fmz_489300_configurable_ma_cross_exit_ma`

- FMZ source id: 489300 (lineage).
- Source: https://www.fmz.com/strategy/489300 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-03 11:31:33). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Moving averages only |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted (the commission is a cost). |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_type` ["EMA", "SMA"] x `enable_shorts` [False, True]: **4 trials**; defaults EMA / off (the source's); MA 13 /
55 / 34 fixed.

## Ambiguities resolved

- barSinceEntry counts bars while a trade is open (fill bar = 1) and is reset to 1 by every entry signal, as written;
  the exit needs at least 2.
- Shorts off by default (a grid variant); with shorts on, entries reverse.
- Two-day bars from broker days in fixed blocks from 1970-01-01 (decision owed), as #426509.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
