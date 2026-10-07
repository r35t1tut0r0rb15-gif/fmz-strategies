# #362418 Smaller-Fractals-Transparency -> `fmz_362418_williams_fractal_side`

- Source: https://www.fmz.com/strategy/362418 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-11 14:11:03). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A7). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Fractals confirmed n bars later; bar-close orders. |
| 2 | PASS | Bar comparisons only. |
| 3 | PASS | Binance futures pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | One parameter; see grid. |
| 6 | PORTED (rule 7) | Group `DG362418` (Jaccard >= 0.80) with #442255 (DUPLICATE); best Jaccard 0.806 with #442255. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`n` [2, 3, 5] = **3 trials**.

## Ambiguities resolved

- **Direction as written**: long on an up (swing-high) fractal. Flagged in the worker report.
- `FREQ = "1h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_reversal"`.

## Marks (2026-10-07)

`none`
