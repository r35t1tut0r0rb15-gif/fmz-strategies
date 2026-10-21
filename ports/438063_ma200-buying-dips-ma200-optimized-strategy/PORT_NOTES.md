# #438063 买入低点-MA200优化策略Buying-Dips-MA200-Optimized-Strategy -> `fmz_438063_one_bar_dip_above_sma100`

- FMZ source id: 438063 (lineage).
- Source: https://www.fmz.com/strategy/438063 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-08 16:54:21). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C109). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Percent change and SMA side |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`drop` [-3.0, -2.0] x `ma_len` [100, 200]: **4 trials**; lookback 1 and the +1 % exit fixed.

## Ambiguities resolved

- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
