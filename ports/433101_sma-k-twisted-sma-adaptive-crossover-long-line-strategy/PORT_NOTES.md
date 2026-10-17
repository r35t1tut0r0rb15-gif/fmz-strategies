# #433101 三重SMA自适应K线交叉长线策略Twisted-SMA-Adaptive-Crossover-Long-Line-Strategy -> `fmz_433101_twisted_sma_adaptive_long`

- FMZ source id: 433101 (lineage).
- Source: https://www.fmz.com/strategy/433101 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-24 14:26:37). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C58). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average order and an efficiency ratio |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 100 % of equity and the commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND433101. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`main_len` [100, 50] x `ad_len` [25, 50]: **4 trials**; SMA 4 / 9 / 18 fixed, self powered on.

## Ambiguities resolved

- Adaptive average as written. Long only. FREQ = "1D" (broker days; the title's 4h is not used).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
