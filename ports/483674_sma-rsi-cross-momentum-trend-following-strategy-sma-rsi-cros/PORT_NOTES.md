# #483674 交叉动能趋势跟踪策略SMA-RSI交叉动量系统-Cross-Momentum-Trend-Following-Strategy-SMA-RSI-Cross-Momentum-System -> `fmz_483674_sma20_cross_rsi8_long`

- FMZ source id: 483674 (lineage).
- Source: https://www.fmz.com/strategy/483674 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-25 10:44:04). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L18). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | A moving average and RSI. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_buy` [60, 55] x `rsi_sell` [40, 45]: **4 trials**; defaults 60 / 40 (the source's); SMA 20 and RSI 8 fixed.

## Ambiguities resolved

- The success / failure counters feed only the table: not ported.
- Long only: opposite entries cannot occur. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum"`.

## Marks

`none`
