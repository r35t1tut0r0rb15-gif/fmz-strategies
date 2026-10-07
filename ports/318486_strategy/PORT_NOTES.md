# #318486 均线傻瓜版 -> `fmz_318486_ma20_entry_ma10_exit`

- Source: https://www.fmz.com/strategy/318486 (JavaScript, author sabar, FMZ last modified
  2021-09-23 17:15:26). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A3). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS (with note) | Acts once per new bar on the forming bar; the port evaluates on completed bars. |
| 2 | PASS | Bar-count MAs only. |
| 3 | PASS (screen: REVIEW) | OKCoin swap is the venue only. |
| 4 | DONE | Fixed `Amount`, ticker order prices -> `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. Built on #193609's template (different rule: separate entry and exit MAs). |
| 7 | IGNORED | |

## Declared grid (criterion 5)

`ma_exit` [5, 10, 20] x `ma_entry` [10, 20, 40] = **9 trials**.

## Ambiguities resolved

- Exit then immediate re-entry in one pass: same side = stay in; opposite side = reversal.
- `FREQ = "5min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`
