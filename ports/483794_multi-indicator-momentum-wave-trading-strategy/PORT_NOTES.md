# #483794 多指标动量波浪交易策略-Multi-Indicator-Momentum-Wave-Trading-Strategy -> `fmz_483794_macd_hist_zero_cross_levels`

- FMZ source id: 483794 (lineage).
- Source: https://www.fmz.com/strategy/483794 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-26 10:30:20). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L17). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | Price-unit histogram exit levels +11 / -9 -> +0.09 / -0.075 ATR; MACD. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`long_exit_atr` [0.09, 0.3] x `signal_length` [20, 9]: **4 trials**; defaults 0.09 / 20 (the source as written: on
daily ETH_USDT, ATR about 120, the +11 level is about 0.09 ATR; judgement stated before any backtest); MACD 12 / 26,
the -0.075 ATR short exit and ATR 14 fixed.

## Ambiguities resolved

- The closes test the position at the bar's start (#430850). REVERSAL INTENDED. Daily bars are broker days;
  FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd"`.

## Marks

`none`
