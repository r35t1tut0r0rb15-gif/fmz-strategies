# #361718 Swing-Highs-Lows-Candle-Patterns -> `fmz_361718_swing_pivot_side`

- Source: https://www.fmz.com/strategy/361718 (PineScript v4, author ChaoZhang (LuxAlgo indicator), FMZ last
  modified 2022-05-07 21:35:09). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A5). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Pivots confirmed `length` bars later; bar-close orders. |
| 2 | PASS | Pivot tests on bar prices only. |
| 3 | PASS | Binance futures pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | One parameter; see grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [10, 21, 34] = **3 trials**.

## Ambiguities resolved

- Long on a swing high and short on a swing low, as written (pivot of the CLOSE for highs, of the OPEN for lows).
- The candle-pattern booleans feed labels only.
- `FREQ = "2h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_reversal"`.

## Marks (2026-10-07)

`none`
