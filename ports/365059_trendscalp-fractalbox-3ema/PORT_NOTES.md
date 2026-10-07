# #365059 [VDB]TrendScalp-FractalBox-3EMA -> `fmz_365059_fractal_box_breakout`

- Source: https://www.fmz.com/strategy/365059 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-23 12:01:38). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A11). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

No parameter reaches the orders (the fractal pattern is fixed): **1 trial**, the source as written.

## Ambiguities resolved

- Fractal confirmed two bars after its centre (no look-ahead); before the first fractal the level is the bar's own high/low (nz).
- EMA ribbon and trend-strength EMA only draw.
- `FREQ = "45min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_reversal"`.

## Marks (2026-10-07)

`none`
