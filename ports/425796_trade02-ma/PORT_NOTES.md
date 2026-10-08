# #425796 Trade02-阿隆指标MA策略 -> `fmz_425796_aroon_ema_reversal`

- Source: https://www.fmz.com/strategy/425796 (MyLanguage, author 作手君TradeMan, FMZ last
  modified 2023-09-04 22:33:13). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A19). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | LOTS formula (MONEYTOT) -> `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`N` [60, 120, 240] = **3 trials** (default 240, header args 120).

## Ambiguities resolved

- Statements run in order on the completed bar; the port emits the bar's net position change.
- BARSLAST of a never-true condition is na: Aroon na until the first new N-bar high/low.
- LOTS (MONEYTOT) -> original_sizing.txt. `FREQ = "1h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "directional_movement"`.

## Marks (2026-10-07)

`none`
