# #361802 3EMA-Boullinger-PIVOT -> `fmz_361802_pivot_confirm_side`

- Source: https://www.fmz.com/strategy/361802 (PineScript v4, author ChaoZhang (JCMR76 indicator), FMZ last
  modified 2022-05-08 12:29:27). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A5). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Pivots confirmed `dist` bars later; bar-close orders. |
| 2 | PASS | Pivot tests only. |
| 3 | PASS | Binance futures pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | One parameter; see grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`dist` [3, 6, 10] = **3 trials**.

## Ambiguities resolved

- The EMAs and Bollinger bands of the title are display only.
- Both pivots on one bar: short wins (later order).
- `FREQ = "1h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_reversal"`.

## Marks (2026-10-07)

`none`
