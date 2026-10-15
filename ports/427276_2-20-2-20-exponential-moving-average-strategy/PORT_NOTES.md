# #427276 2/20 Exponential Moving Average Strategy -> `fmz_427276_hpotter_2_20_ema`

- FMZ source id: 427276 (lineage).
- Source: https://www.fmz.com/strategy/427276 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-19 17:02:20). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Price-to-price comparisons. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 10, 40]: **3 trials**; default 20 (the source's).

## Ambiguities resolved

- Broker-day bars stamped with their first minute.
- Always in the market after the first signal (REVERSAL INTENDED). FREQ = "1D" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
