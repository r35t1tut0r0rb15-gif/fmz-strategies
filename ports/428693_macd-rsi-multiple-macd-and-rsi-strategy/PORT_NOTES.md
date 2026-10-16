# #428693 多MACD与RSI策略Multiple-MACD-and-RSI-Strategy -> `fmz_428693_two_macd_rsi_open`

- FMZ source id: 428693 (lineage).
- Source: https://www.fmz.com/strategy/428693 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-10-08 14:03:47). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C19). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Oscillator thresholds and sign tests only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`overbought` [70, 80] x `oversold` [20, 30]: **4 trials**; MACD lengths 10 / 22 / 9 and 21 / 45 / 20 and RSI 14 fixed.

## Ambiguities resolved

- The MACD signal lines are SMAs as written. `year > 2015` dropped (backtest window).
- REVERSAL INTENDED. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks

`none`
