# #435477 EMA黄金交叉短线交易策略EMA-Golden-Cross-Short-term-Trading-Strategy -> `fmz_435477_ema_scalper_short`

- FMZ source id: 435477 (lineage).
- Source: https://www.fmz.com/strategy/435477 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-15 11:16:18). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C78). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The initial capital input stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG435477. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_l` [9, 5] x `ema_l2` [26, 21]: **4 trials**; the exit pair EMA 100 / 55 fixed.

## Ambiguities resolved

- Entry id "long" with direction short: short only. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
