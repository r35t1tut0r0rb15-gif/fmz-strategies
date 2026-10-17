# #431272 多重MA带动量交易策略Multi-Timeframe-Moving-Average-Momentum-Trading-Strategy -> `fmz_431272_ema_ribbons_state_engine`

- FMZ source id: 431272 (lineage).
- Source: https://www.fmz.com/strategy/431272 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-11-06 16:04:46). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C44). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-checked trailing exits |
| 2 | PASS | EMA ribbons and percentage pull-backs |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG431272. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ts_pct` [3.0, 1.5] x `tp_pct` [3.0, 6.0]: **4 trials**; ribbons 5 / 25 / 28 / 72 and the 1 % trailing profit fixed.

## Ambiguities resolved

- Body-based, close-checked trailing exits; state engine as written. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
