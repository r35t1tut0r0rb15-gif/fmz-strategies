# #431678 EMA均线交叉策略EMA-Crossover-Strategy -> `fmz_431678_close_ema_20_30_long`

- FMZ source id: 431678 (lineage).
- Source: https://www.fmz.com/strategy/431678 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-10 15:05:22). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C46). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`buy_len` [20, 50] x `sell_len` [30, 15]: **4 trials**.

## Ambiguities resolved

- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
