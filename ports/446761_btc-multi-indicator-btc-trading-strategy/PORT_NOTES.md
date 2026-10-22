# #446761 多指标BTC交易策略-Multi-indicator-BTC-Trading-Strategy -> `fmz_446761_rsi_recovery_or_macd_cross_bracket_rsi50_exit_long`

- FMZ source id: 446761 (lineage).
- Source: https://www.fmz.com/strategy/446761 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-04-01 11:26:00). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C177). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed on the signal bar; the wrong-side stop read as a close |
| 2 | PASS | RSI recovery or MACD cross entries, bracket and RSI / MACD exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_low` [20, 25] x `sl` [0.005, 0.01]: **4 trials**; the upper bound, the SMAs and the ATR target fixed.

## Ambiguities resolved

- RSI >= 50 closes at the next open (stop at the high). Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
