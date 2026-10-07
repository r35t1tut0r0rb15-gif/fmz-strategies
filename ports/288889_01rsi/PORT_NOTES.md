# #288889 练习01RSI -> `fmz_288889_rsi_30_70_long`

- Source: https://www.fmz.com/strategy/288889 (Python, author 3028165668, FMZ last modified
  2021-06-09 10:24:00). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A3). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS (with note) | Polls the forming 4-hour bar; the port evaluates on completed bars. |
| 2 | PASS | RSI thresholds only. |
| 3 | PASS (screen: REVIEW) | Spot only. |
| 4 | DONE | 1 % slices repeated on every loop while the RSI stays beyond a threshold (scaling in/out) -> `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED | |

## Declared grid (criterion 5)

`rsi_period` [7, 14, 21] x `zone` [20, 30] (buy below `zone`, sell above 100-`zone`) = **6 trials**.

## Ambiguities resolved

- The source scales in and out in 1 % slices; the port reduces this to one position: in from the
  first oversold bar, out at the first overbought bar. The slice ladder is sizing.
- `FREQ = "4h"` from `GetRecords(PERIOD_H1 * 4)` (no backtest header; the code's own request).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks (2026-10-07)

`none`
