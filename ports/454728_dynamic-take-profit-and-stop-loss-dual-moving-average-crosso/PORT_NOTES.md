# #454728 Dynamic Take Profit and Stop Loss Dual Moving Average Crossover Trading Strategy -> `fmz_454728_sma50_100_cross_close_test_bracket_reversal`

- FMZ source id: 454728 (lineage).
- Source: https://www.fmz.com/strategy/454728 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-21 14:02:56). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C195). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the stop / target are close tests |
| 2 | PASS | SMA crossings with close-test exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_len` [50, 20] x `long_len` [100, 200] x `tp_pct` [0.05, 0.10]: **8 trials**; the 3 % stop fixed.

## Ambiguities resolved

- Close tests against the latest signal close. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
