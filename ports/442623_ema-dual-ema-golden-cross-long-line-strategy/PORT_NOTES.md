# #442623 双EMA黄金交叉长线策略Dual-EMA-Golden-Cross-Long-Line-Strategy -> `fmz_442623_ema200_stack_atr_filter_pct_trail_long`

- FMZ source id: 442623 (lineage).
- Source: https://www.fmz.com/strategy/442623 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-23 12:17:40). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C159). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the trail is a house trail (approximation stated) |
| 2 | PASS | EMA trend stack with an ATR filter; percent trail |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trail_pct` [0.15, 0.05] x `atr_mult` [1.5, 1.0]: **4 trials**; the EMA lengths fixed.

## Ambiguities resolved

- Percent trail as a house trail from the fill. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`trailing_stop`
