# #427312 Adaptive Moving Average Crossover Strategy Based on Uhl MA -> `fmz_427312_uhl_ma_cross`

- FMZ source id: 427312 (lineage).
- Source: https://www.fmz.com/strategy/427312 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-19 22:06:42). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C5). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Variance ratios are scale-free. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code (the equity plot is display only). |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [100, 50, 200]: **3 trials**; default 100 (the source's). `mult` is declared but unused.

## Ambiguities resolved

- Population variance; nz() seeds with the close as written.
- Broker-day bars. REVERSAL INTENDED. FREQ = "1D" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
