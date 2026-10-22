# #453650 RSI基于百分比止盈止损的交易策略-RSI-based-Trading-Strategy-with-Percentage-based-Take-Profit-and-Stop-Loss -> `fmz_453650_rsi30_crossunder_close_test_bracket_long`

- FMZ source id: 453650 (lineage).
- Source: https://www.fmz.com/strategy/453650 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-07 15:04:39). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C192). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the stop / target are close tests |
| 2 | PASS | RSI dips with close-test exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity sizing and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [14, 7] x `sl_pct` [0.05, 0.02] x `tp_pct` [0.20, 0.05]: **8 trials**; the levels fixed.

## Ambiguities resolved

- Close tests against the latest signal close. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
