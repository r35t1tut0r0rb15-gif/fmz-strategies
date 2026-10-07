# #364540 _CM_MacD_Ult_MTF_V2.1 -> `fmz_364540_macd_cross_zero_side`

- Source: https://www.fmz.com/strategy/364540 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-20 17:25:31). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A11). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `ND364540` (Jaccard 0.65-0.80) with #432356 (PORT_CANDIDATE); best Jaccard 0.770 with #432356. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [8, 12] x `slow` [21, 26] x `signal` [5, 9] = **8 trials**.

## Ambiguities resolved

- Indicator timeframe default "" = chart timeframe: no higher-timeframe read.
- Long needs the cross above zero, short the cross below zero.
- `FREQ = "10min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks (2026-10-07)

`none`
