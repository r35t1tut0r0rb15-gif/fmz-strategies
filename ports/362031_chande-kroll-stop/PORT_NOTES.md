# #362031 Chande-Kroll-Stop -> `fmz_362031_chande_kroll_cross_faded`

- Source: https://www.fmz.com/strategy/362031 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-09 17:44:31). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A6). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | ATR-based lines, ADX threshold. |
| 3 | PASS | No venue code. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `DG362031` (Jaccard >= 0.80) with #431251 (DUPLICATE); best Jaccard 0.859 with #431251. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`p` [10, 20] x `q` [9, 20] x `x` [1, 2] = **8 trials**. ADX 14/14 > 20 fixed.

## Ambiguities resolved

- **Direction as written** (a fall through the long stop buys). Flagged in the worker report.
- No backtest header: `FREQ = "bar_size_pending"`, mark `bar_size_pending` (rule 1).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks (2026-10-07)

`bar_size_pending`
